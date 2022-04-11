# Airflow Imports
from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.pubsub_operator import PubSubPublishOperator
from google.cloud.storage import Client

from airflow.utils.trigger_rule import TriggerRule
from airflow.utils import dates

# 3rd party modules
from google.cloud import storage

# Python Built-in modules
import base64, json, logging, requests, time, uuid

from django.utils import timezone
from elementlist_tools.convert_to_el import convert_caption_to_elementlist
import os
import sys
import subprocess


DEV_TESTING = False
SPEECH_RECOGNITION_SECRET = Variable.get("speech_recognition_secret")
ENDPOINT_SECRET = Variable.get("endpoint_secret")
STORAGE_CLIENT = storage.Client()
BUCKET_NAME = 'dev-experiments'
PROJECT_ID = 'coresystem-171219'
TOPIC = 'Customer-Upload-Complete'

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

SEND_EVENT_URL = Variable.get('send_event_legacy_api')
MICROSERVICE_OVERRIDE_SECRET = Variable.get('microservice_override_secret')
DAG_NAME = 'Handle-Customer-Upload'
BASE_API_URL = Variable.get('base_api_url')
ELEMENTLIST_STORAGE_BUCKET = Variable.get('elementlist_storage_bucket')
STORAGE_ACCOUNT = Variable.get('storage_account_secret')

STORAGE_CLIENT = storage.Client(project="coresystem-171219")

def dispatcher(**context):
    """
    Function determines if from main or if from external source
    also determines if needs transcoding or not
    :param context:
    :return:
    """
    try:
        # pubsub
        raw_data = context['dag_run'].conf['data']
        logging.info(json.dumps({type(raw_data).__name__: raw_data}))
        decoded_data = base64.b64decode(raw_data).decode('ascii').replace('\'', "\"").replace('"{', '{'). replace('}"', '}').replace("True", "true").replace("False", "false")
        logging.info(json.dumps({type(decoded_data).__name__: decoded_data}))
        data = json.loads(decoded_data)
        logging.info(json.dumps({type(data).__name__: data}))
    except json.decoder.JSONDecodeError as e:
        raise e
    except Exception as e:
        # http
        logging.warning(json.dumps({type(e).__name__: str(e)}))
        data = context['dag_run'].conf
        if not isinstance(data, dict):
            data = json.loads(data)

    # Job ID will probably not always be from main
    # therefore, if not entered in, it will assign a random uuid in hex form
    job_id = data.get('job_id')
    media_path = data.get('media_path')
    is_from_main = data.get('from_legacy_main', False)

    context['ti'].xcom_push(key='from_legacy_main', value=is_from_main)
    context['ti'].xcom_push(key='job_id', value=job_id)
    context['ti'].xcom_push(key='media_path', value=media_path)
    return dict(bucket_name='presigned-customer-uploads', media_path=media_path, job_id=job_id)


def handle_customer_upload(**context):
    """
    Upon successful file upload, updates Media with length, creates an Original media variant and 
    restarts the workflow if necessary.
    :param context:
    :return:
    """
    from workflow.models import CoreJob, CoreMedia, CoreMediavariant
    from datetime import datetime, timedelta

    ti = context['ti']
    job_id = ti.xcom_pull(task_ids='Dispatcher', key='job_id')
    media_path = ti.xcom_pull(task_ids='Dispatcher', key='media_path')

    job = CoreJob.objects.get(job_id=job_id)

    storage_data = dict(
        bucket='presigned-customer-uploads',
        path=media_path,
        account="2548c78f6b8545148459d74e1e166da3"
    )

    media_bucket = STORAGE_CLIENT.bucket('presigned-customer-uploads')
    blob = media_bucket.blob(media_path)
    expiry = datetime.now() + timedelta(days=7)
    presigned_url = blob.public_url

    media = job.media
    media_length = _check_media_length_from_uploaded_file(storage_data, job_id)
    media_size = media_length[1]
    media.length = media_length[0]
    media.original_storage_data = presigned_url
    media.media_source_type = "DIRECTLINK"
    media.save()

    storage_data["size"] = media_size
    storage_data_string = json.dumps(storage_data)

    media_variant = CoreMediavariant.objects.create(
        media_fk=media, media_type="ORIGINAL",
        storage_data=storage_data_string, size=media_size, deleted=False
    )
    logging.info(job.job_id, media_variant.id)

def send_event(job_id, event_name, event_kwargs=None):
    api_endpoint = SEND_EVENT_URL
    logging.info("Sending event to {}".format(api_endpoint))

    data = {
        "event": event_name,
    }

    if not job_id:
        logging.info("Skipping Send Event to Main, No job_id submitted")
        return False
    else:
        data.update({"job_id": job_id})

    if event_kwargs and isinstance(event_kwargs, dict):
        data.update({"event_kwargs": event_kwargs})

    headers = {
        "Authorization": "Bearer {}".format(MICROSERVICE_OVERRIDE_SECRET),
        "Content-Type": "application/json"
    }
    logging.info(
        "Handling Request with post url: {} data: {} headers: {}".format(api_endpoint, repr(data), repr(headers)))
    response = requests.post(api_endpoint, data=json.dumps(data), headers=headers)
    try:
        return response.json()
    except:
        return response.text

def _conditions_met(task_instance, conditional_keys, conditional_task_origin):
    """
    checks conditions and
    :param task_instance: (task instance object from airflow)
    :param conditional_keys: (list)
    :param conditional_task_origin: (string)
    :return:
    """
    conditions_met = []
    if conditional_keys and conditional_task_origin:
        if not isinstance(conditional_keys, list):
            raise TypeError("Conditional Keys must be a list")
        for conditional_key in conditional_keys:
            conditions_met.append(
                task_instance.xcom_pull(task_ids=conditional_task_origin, key=conditional_key)
            )
    else:
        conditions_met = [True]

    return all(conditions_met)

def _get_length(filename):
    logging.info("Downloading ffprobe")
    media_bucket = STORAGE_CLIENT.bucket('dev-experiments')
    blob = media_bucket.blob('ffprobe')
    blob.download_to_filename('ffprobe')
    # os.system("gsutil cp gs://dev-experiments/ffprobe .")
    os.system("chmod +x ffprobe")
    args = [
        "./ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename
    ]
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

def _check_media_length_from_uploaded_file(storage_data, job_id):
    """
    Downloads media file and then finds the length of the media
    :param storage_data:
    :param job_id:
    :return:
    """
    bucket = STORAGE_CLIENT.bucket('presigned-customer-uploads')
    blob = bucket.blob(storage_data['path'])
    blob.download_to_filename(job_id)
    return _get_length(job_id), os.path.getsize(job_id)

def send_select_workflow_event(**context):
    if context['ti'].xcom_pull(task_ids='Dispatcher', key='from_legacy_main'):
        event = "copy_account_configs"
        job_id = context['ti'].xcom_pull(task_ids='Dispatcher', key='job_id')
        return send_event(job_id, event)
    else:
        logging.info("Job is not from Legacy Main")
        return False

def send_failed_event_to_main(**context):
    api_endpoint = SEND_EVENT_URL
    logging.info("Sending event to {}".format(api_endpoint))

    try:
        job_id = context['ti'].xcom_pull(task_ids='Dispatcher', key='job_id')
    except:
        job_id = False

    data = {
        "event": "Halt the action with an error message",
        "event_kwargs": {"error_string": "Airflow failed to Transcribe with ASR"}
    }

    if not job_id:
        logging.info("Skipping Send Event to Main, No job_id submitted")
        return {}
    else:
        data.update({"job_id": job_id})

    headers = {
        "Authorization": "Bearer {}".format(MICROSERVICE_OVERRIDE_SECRET),
        "Content-Type": "application/json"
    }
    logging.info("Handling Request with post data: {}".format(repr(data)))
    response = requests.post(api_endpoint, data=json.dumps(data), headers=headers)
    response.raise_for_status()
    raise EOFError("Task completed successfully, Raising Error to mark dag Failed")

class ConditionalDjangoOperator(PythonOperator):
    ui_color = '#99e0a7'

    def __init__(self, conditional_task_origin=None, conditional_keys=None, *args, **kwargs):
        """
        Allows condtional arguments to be input to skip task on variable conditions
        :param conditional_task_origin: (string)
        :param conditional_keys: (list)
        :param args:
        :param kwargs:
        """
        super(ConditionalDjangoOperator, self).__init__(*args, **kwargs)
        self.conditional_task_origin = conditional_task_origin
        self.conditional_keys = conditional_keys

    @staticmethod
    def setup_django_for_airflow():
        import os, sys
        # Add Django project root to path
        sys.path.append('/home/airflow/gcs/data/services/legacy-db-microservices/')

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service.settings.db_only_pool")
        if DEV_TESTING:
            os.environ.setdefault('DEBUG', 'True')

        import django
        django.setup()

    def pre_execute(self, context):
        self.setup_django_for_airflow()
        super(ConditionalDjangoOperator, self).pre_execute(context)

    def execute(self, context):
        if _conditions_met(context['ti'], self.conditional_keys, self.conditional_task_origin):
            return super(ConditionalDjangoOperator, self).execute(context)
        else:
            logging.info("Skipping Step, Conditions not met")
            return

dag = DAG(DAG_NAME, default_args=dag_kwargs, schedule_interval=None)
dispatcher = PythonOperator(task_id='Dispatcher', dag=dag, python_callable=dispatcher)
handle_upload_event = ConditionalDjangoOperator(
    task_id='Handle-Upload', dag=dag, python_callable=handle_customer_upload,
    conditional_keys=['from_legacy_main'], conditional_task_origin='Dispatcher'
)
send_start_workflow_event = PythonOperator(task_id='Send-Event-Start-Workflow', dag=dag, python_callable=send_select_workflow_event)

dispatcher >> handle_upload_event >> send_start_workflow_event