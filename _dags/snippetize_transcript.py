from airflow import DAG
from airflow.models import BaseOperator, Variable, SkipMixin
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.pubsub_operator import PubSubPublishOperator
# from airflow.contrib.sensors.python_sensor import PythonSensor
from airflow.utils import dates
from caption_tools.core import BuildCaption
from elementlist_tools.core import Elementlist
from google.cloud import storage
from datetime import datetime, timedelta
import base64, json, logging, os, requests, sys, uuid
STORAGE_CLIENT = storage.Client()
PROJECT_ID = "coresystem-171219"
TOPIC = "snippetized-training-data"

def _download_elementlist(bucket_name, file_key):
	"""
		Downloads File from bucket and loads it to json
		:param bucket_name: name of GCS bucket
		:type bucket_name: string
		:param file_key: path of file blob stored in GCS bucket
		:type file_key: string
		:return dict: elementlist in json format 
	"""
	bucket = STORAGE_CLIENT.bucket(bucket_name)
	blob = bucket.blob(file_key)
	el_string = blob.download_as_string()
	return json.loads(el_string)
def _upload_to_gcs(caption_string, file_key, bucket_name):
	bucket = STORAGE_CLIENT.bucket(bucket_name)
	blob = bucket.blob(file_key)
	blob.upload_from_string(caption_string)
	return {"bucket": bucket_name, "path": file_key}
def set_up_snippet_times(start_time_ms, end_time_ms):
	i = 1
	current_start_time = start_time_ms
	snippet_times = []
	while current_start_time < end_time_ms:
		current_end_time = current_start_time + 60000
		if current_end_time > end_time_ms:
			current_end_time = end_time_ms
		if current_start_time >= current_end_time:
			break
		snippet_times.append(i, current_start_time)
		current_start_time = current_end_time
		i +=1
	return snippet_times
dag_kwargs = dict(
	owner="airflow",
	depends_on_past=False,
	catchup=False,
	start_date=dates.days_ago(0),
	email=['devs@mydomain.com'],
	email_on_failure=False,
	email_on_retry=False,
	retries=0,
	provide_context=True
)
dag = DAG('Snippetize-Training-Data', default_args=dag_kwargs, schedule_interval=None)
# DJANGO Operators
def setup_main_django_for_airflow():
    # Add Django project root to path
    sys.path.append('/home/airflow/gcs/data/services/legacy-db-microservices/')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service.settings.db_only_pool")
    import django
    django.setup()
def setup_cirrus_django_for_airflow():
	# Add Django project root to path
	sys.path.append('/home/airflow/gcs/data/services/cirrus_models/')
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service.settings.db_only_pool")
	import django
	django.setup()
class DjangoOperator(BaseOperator):
    ui_color = '#7FFFD4'
    def __init__(self, django_app, *args, **kwargs):
    	self.django_app = django_app
    	super(DjangoOperator, self).__init__(*args, **kwargs)
    def pre_execute(self, *args, **kwargs):
    	if self.django_app == "main":
    		setup_main_django_for_airflow()
    	elif self.django_app == "cirrus":
    		setup_cirrus_django_for_airflow()
    	else:
    		raise ValueError("{} is not a valid django app".format(self.django_app))
class FetchJobData(DjangoOperator, SkipMixin):
	def execute(self, context):
		from workflow.models import CoreJob, CoreElementlist
		# TODO: change this line once we determine trigger type (current setup, http trigger)
		job_id = context['dag_run'].conf.get('job_id')
		iwp_name = context['dag_run'].conf.get('iwp_name', 'FINAL')
		elementlist_data = CoreElementlist.objects.filter(job_fk__job_id=job_id, iwp_name=iwp_name).order_by('-version').first()
		if not elementlist_data:
			downstream_tasks = context['task'].get_flat_relatives(upstream=False)
			if downstream_tasks:
				logger.warning("Skipping downstream tasks. No Elementlist Data to fetch.")
				self.skip(context['dag_run'], ti.execution_date, downstream_tasks)
			return
		storage_data = json.loads(elementlist_data.storage_data)
		clean_storage_data = {"bucket": storage_data["bucket"], "path": storage_data['path']}
		return {"job_id": job_id, "storage_data": clean_storage_data}

def snippetize_and_strip_text_from_el(**context):
	try:
		fetched_data = context['ti'].xcom_pull('')
		job_id = fetched_data['job_id']
		storage_data = fetched_data['storage_data']
		el_json = _download_elementlist(storage_data['bucket'], storage_data['path'])
		el = Elementlist(el_json)
		snippet_times = set_up_snippet_times(0, el.end_time)
		bucket_name = 'training-text'
		storage_data_map = {}
		for index, start_time_ms, end_time_ms in snippet_times:
			el_snippet = el.get_time_range(start_time_ms, end_time_ms)
			text_blob = "{0}_{1}.wav ".format(job_id, index)
			transcript = BuildCaption(el, 'training').caption
			text_blob.join(transcript)
			snippet_name = "{}_{}".format(index, job_id)
			file_path = "{}.txt".format(snippet_name)
			_upload_to_gcs(text_blob, bucket_name, file_path)
			storage_data_map.update({snippet_name: {"path": file_path, "bucket": bucket_name, "start_time_ms": start_time_ms, "end_time_ms": end_time_ms}})
		# PubSub Messages must be base64 encoded {"data": b64encode(dumped_bytes_data)}
		pubsub_message = base64.b64encode(json.dumps(storage_data_map).encode()).decode()
		return pubsub_message
	except Exception as e:
		downstream_tasks = context['task'].get_flat_relatives(upstream=False)
		if downstream_tasks:
			logger.warning("Skipping downstream tasks. No Elementlist Data to fetch.")
			self.skip(context['dag_run'], ti.execution_date, downstream_tasks)
		return
messages_template = {'data': ("{{ task_instance.xcom_pull(task_ids='create-snippets') }}")}

t1 = FetchJobData(task_id='fetch-job-data', dag=dag, django_app='main')
t2 = PythonOperator(task_id='create-snippets', dag=dag, python_callable=snippetize_and_strip_text_from_el)
t3 = PubSubPublishOperator(task_id='Publish-to-PubSub', dag=dag, project=PROJECT_ID, topci=TOPIC, message=messages_template)
t1 >> t2 >> t3