from airflow import DAG
from airflow.models import BaseOperator, SkipMixin, Variable
from airflow.contrib.operators.pubsub_operator import PubSubPublishOperator
from airflow.contrib.sensors.python_sensor import PythonSensor
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.sensors.pubsub_sensor import PubSubPullSensor
from airflow.utils import dates
from elementlist_tools.core import Elementlist
from caption_tools.core import BuildCaption
from gcloud import storage

import base64, json, logging, os, requests, sys, urllib, uuid


YTRANSLATOR_SECRET = Variable.get('YTRANSLATOR_SECRET')
GCS_CREDENTIALS = json.loads(Variable.get("GCS_CREDENTIALS"))

TOPIC = "return-ytranslator"
SUBSCRIPTION = "order-ytranslator"
PROJECT_ID = "coresystem-171219"


GCS_CLIENT = storage.Client(project=PROJECT_ID, credentials=GCS_CREDENTIALS)


def order_from_ytranslator(**context):
	order = context['ti'].xcom_pull('fetch-order')
	logging.info(order['ackId'])
	decoded_message = json.loads(base64.b64decode(message['message']['data'])).decode("ascii")
	file_url = decoded_message['file_url']
	yt_endpoint = "https://api.ytranslator.com/transcribe/v1"

	# TODO: Add Callback URL
	data = json.dumps(dict(fileUrl=file_url))
	headers = dict()
	response = requests.post(yt_endpoint, data=data, headers=headers)
	response.raise_for_status()
	return {decoded_message['order_uuid']: response.json()}


def return_ytranslator(**context):
	order_data = context['ti'].xcom_pull('order-ytranslator')
	order_uuid, response_json = order.items()[0]

	url = "https://api.ytranslator.com/transcribe/v1/ElementList/{}".format(response_json['id'])
	headers = {'Authorization': 'Bearer {}'.format(YTRANSLATOR_SECRET)}

	response = requests.get(url, headers=headers)

	if response.json().get('job', {}).get('status') == 'transcribed':
		context['ti'].xcom_push(key='ytranslator_response', value=json.dumps({order_uuid, response.json()}))
		return True
	elif response.json().get('job', {}).get('status') == 'failed':
		# TODO: Trigger status update on order for failed media (whether its external or internal)
		context['ti'].xcom_push(key='failed_ytranslator_response', value=json.dumps({order_uuid, response.json()}))
		return True
	else:
		logging.info("Status: {}\tResponse: {}".format(response.status_code, repr(response.json)))
		return False


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

dag = DAG('handle_new_cirrus_order', default_args=dag_kwargs, schedule_interval=None)


# DJANGO Operators
def setup_django_for_airflow():
	# Add Django project root to path
	sys.path.append('/home/airflow/gcs/data/services/cirrus_models/')

	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service.settings.db_only_pool")

	import django
	django.setup()


class DjangoOperator(BaseOperator):
	ui_color = '#7FFFD4'

	def pre_execute(self, *args, **kwargs):
		setup_django_for_airflow()


class UnpackYTranslator(DjangoOperator):
	def execute(self, context):
		from order import OrderItem, OutputProduct
		order_uuid, data = json.loads(context['ti'].xcom_pull('poll-ytranslator', key='ytranslator_response')).items()[0]

		transcript_url = data['job']['transcriptUrl']
		response = request.get(transcript_url)

		order = OrderItem.objects.get(order_uuid=order_uuid)

		# Self Validates the elementlist
		el = Elementlist(el_data=response.json(), language=order.source_language)

		file_name = urllib.parse.quote("{}.json".format(order_uuid))
		file_path = "MECH/{}".format(file_name)

		# store elementlist
		logging.info("Storing elementlist to GCS")
		gcs_bucket = GCS_CLIENT.get_bucket('final-elementlist')
		blob = gcs_bucket.blob(file_path)
		blob.upload_from_string(json.dumps(el.json))

		storage_paths = {"MECHANICAL": {"json": {"bucket": 'final-elementlist', "path": file_path}}}

		# create and store vtt
		# TODO: Include code to handle different caption formats for account
		logging.info("Creating .vtt")
		caption_builder = BuildCaption(el, 'vtt')
		caption_string = caption_builder.caption

		# Store vtt to cloud
		gcs_bucket = GCS_CLIENT.get_bucket('final-captions')
		file_name = urllib.parse.quote("{}.vtt".format(order_uuid))
		file_path = "VTT/{}".format(file_name)
		blob = gcs_bucket.blob(file_path)
		blob.upload_from_string(caption_string)

		storage_paths['MECHANICAL'].update({"vtt": {"bucket": "final-captions", "path": file_path}})


		op = OutputProduct.objects.filter(order_uuid=order_uuid).first()
		if not op:
			op = OutputProduct.objects.create(entry=order.entry, order=order, progess=100, status="COMPLETE", storage_paths=json.dumps(storage_paths))
		else:
			existing_storage_paths = json.loads(op.storage_paths)
			existing_storage_paths.update(storage_paths)
			op.storage_paths = json.dumps(existing_storage_paths)
			op.progress = 100
			status = "COMPLETE"
			op.save()


class ShouldUnpackOperator(BaseOperator, SkipMixin):
	def execute(self, context):
		try:
			context['ti'].xcom_pull("poll-ytranslator", key="ytranslator_response")
			return True
		except:
			downstream_tasks = context['task'].get_flat_relatives(upstream=False)

			if downstream_tasks:
				logger.info("Skipping downstream tasks. Job Failed.")
				self.skip(context['dag_run'], ti.execution_date, downstream_tasks)


class ShouldTriggerFailedResponseOperator(BaseOperator, SkipMixin):
	def execute(self, context):
		try:
			context['ti'].xcom_pull("poll-ytranslator", key="failed_ytranslator_response")
			return True
		except:
			downstream_tasks = context['task'].get_flat_relatives(upstream=False)

			if downstream_tasks:
				logger.info("Skipping downstream tasks. Job Failed.")
				self.skip(context['dag_run'], ti.execution_date, downstream_tasks)


class FailedResponseOperator(DjangoOperator):
	def execute(self, context):
		order_uuid, data = json.loads(context['ti'].xcom_pull('poll-ytranslator', key='failed_ytranslator_response')).items()[0]


t1 = PubSubPullSensor(task_id='fetch-order', ack_messages=True, dag=dag, project=PROJECT_ID, subscription=SUBSCRIPTION, max_messages=1)
t2 = PythonOperator(task_id='order-ytranslator', dag=dag, python_callable=order_from_ytranslator)
t3 = PythonSensor(task_id='poll-ytranslator', dag=dag, python_callable=return_ytranslator)
t4 = ShouldUnpackOperator(task_id='should-unpack', dag=dag)
t5 = UnpackYTranslator(task_id='unpack-ytranslator', dag=dag)
t6 = ShouldTriggerFailedResponseOperator(task_id="should-trigger-failed", dag=dag)
t7 = FailedResponseOperator(task_id='failed-response', dag=dag)

t1 >> t2 >> t3 >> [t4, t6]
t4 >> t5
t6 >> t7


