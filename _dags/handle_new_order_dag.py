from airflow import DAG
from airflow.models import BaseOperator, SkipMixin, Variable
from airflow.contrib.operators.pubsub_operator import PubSubPublishOperator
from airflow.contrib.sensors.python_sensor import PythonSensor
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.sensors.pubsub_sensor import PubSubPullSensor
from airflow.contrib.operators.gcp_speech_to_text_operator import GcpSpeechToTextRecognizeSpeechOperator
from airflow.utils import dates
from elementlist_tools.core import Elementlist
from caption_tools.core import BuildCaption
from gcloud import storage
from google.cloud import speech_v1p1beta1

import base64, json, logging, os, requests, sys, urllib, uuid, json
from datetime import datetime, timedelta


YTRANSLATOR_SECRET = Variable.get('YTRANSLATOR_SECRET')
GCS_CREDENTIALS = json.loads(Variable.get("GCS_CREDENTIALS"))
GASR_CONFIG = {"language_code": "en_US", "encoding": "LINEAR16", "enable_word_time_offsets": True, "max_alternatives": 2, "sample_rate_hertz":16000}
# AUDIO = {"uri": "gs://{bucket}/{object}".format(bucket=BUCKET_NAME, object=FILENAME)}

TOPIC = "return-ytranslator"
SUBSCRIPTION = "order-ytranslator"
PROJECT_ID = "coresystem-171219"

GCS_CLIENT = storage.Client(project=PROJECT_ID, credentials=GCS_CREDENTIALS)

dag_kwargs = dict(owner="airflow",
    depends_on_past=False,
    catchup=False,
    start_date=dates.days_ago(0),
    email=['devs@mydomain.com'],
    email_on_failure=False,
    email_on_retry=False,
    retries=1,
    provide_context=True)

dag = DAG('handle_new_cirrus_order', default_args=dag_kwargs, schedule_interval=None)

def order_from_ytranslator(**context):
    order_uuid = context['dag_run'].conf.get('order_uuid')
    entry_uuid = context['dag_run'].conf.get('entry_uuid')
    media_url = context['dag_run'].conf.get('media_url')
    job_type = context['dag_run'].conf.get('job_type')
    turnaround_time = context['dag_run'].conf.get('turnaround_time')
    print("values", order_uuid, entry_uuid, media_url, job_type, turnaround_time, context, context['dag_run'], context['dag_run'].conf)

    yt_endpoint = "https://api.ytranslator.com/transcribe/v1"

    # TODO: Add Callback URL
    data = {"fileUrl": media_url}
    headers = {'Authorization': 'Bearer myToken'}
    # headers = {}
    response = requests.post(yt_endpoint, json=data, headers=headers)
    response.raise_for_status()
    response_json = response.json()
    ytranslator_id = response_json.get("id")
    context['ti'].xcom_push(key='ytranslator_id', value=ytranslator_id)
    print('yt_id', ytranslator_id)
    return response.json()

def run_google_asr(**context):
    order_uuid = context['dag_run'].conf.get('order_uuid')
    entry_uuid = context['dag_run'].conf.get('entry_uuid')
    media_url = context['dag_run'].conf.get('media_url')
    job_type = context['dag_run'].conf.get('job_type')
    turnaround_time = context['dag_run'].conf.get('turnaround_time')

    client = speech_v1p1beta1.SpeechClient()

    encoding = 'FLAC'
    sample_rate_hertz = 44100
    language_code = 'en-US'
    config = {'sample_rate_hertz': sample_rate_hertz, 'language_code': language_code, 'audio_channel_count': 2, "enable_word_time_offsets": True, "enable_word_confidence": True, "enable_speaker_diarization": True, "enable_automatic_punctuation": True}
    uri = 'gs://dev-experiments/freshlas.flac'
    audio = {'uri': uri}

    operation = client.long_running_recognize(config, audio)

    print(u"Waiting for operation to complete...")
    response = operation.result()
    transcript = []
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        print(u"Transcript: {}".format(alternative.transcript))
        transcript.append(alternative.transcript)
        for word in alternative.words:
            print(u"Confidence: {}".format(word.confidence, word.speaker_tag))
    return transcript

def return_ytranslator(**context):
    ytranslator_id = context['ti'].xcom_pull('ytranslator_id')
    print(ytranslator_id)
    url = "https://api.ytranslator.com/transcribe/v1/ElementList/{}".format(ytranslator_id)
    headers = {'Authorization': 'Bearer cielo24.g_VIBQ_mqwhgQuUwbC6V97cyM4I'}
    response = requests.get(url, headers=headers)
    json_response = response.json()
    print(json_response)
    transcript_url = json_response.get("transcriptUrl", None)

    if transcript_url:
        context['ti'].xcom_push(key='ytranslator_url', value=transcript_url)
        return True
    else:
        return False

print_gcs_info = BashOperator(task_id='print_gcs_info', bash_command='echo {{ dag_run.conf }}')

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
        order_uuid = context['dag_run'].conf.get('order_uuid')
        ytranslator_url = context['ti'].xcom_pull('ytranslator_url')

        response = requests.get(ytranslator_url)

        order = OrderItem.objects.get(order_uuid=order_uuid)

        # Self Validates the elementlist
        el = Elementlist(el_data=response.json(), language=order.source_language)

        file_name = urllib.parse.quote("{}.json".format(order_uuid))
        file_path = "MECH/{}".format(file_name)

        # store elementlist
        logging.info("Storing elementlist to GCS")
        gcs_bucket = GCS_CLIENT.get_bucket('dev-experiments')
        blob = gcs_bucket.blob(file_path)
        blob.upload_from_string(json.dumps(el.json))

        storage_paths = {"MECHANICAL": {"json": {"bucket": 'dev-experiments', "path": file_path}}}

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
            op.status = "COMPLETE"
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
                self.skip(context['dag_run'], context['ti'].execution_date, downstream_tasks)


class ShouldTriggerFailedResponseOperator(BaseOperator, SkipMixin):
    def execute(self, context):
        try:
            context['ti'].xcom_pull("poll-ytranslator", key="failed_ytranslator_response")
            return True
        except:
            downstream_tasks = context['task'].get_flat_relatives(upstream=False)

            if downstream_tasks:
                logger.info("Skipping downstream tasks. Job Failed.")
                self.skip(context['dag_run'], context['ti'].execution_date, downstream_tasks)


class FailedResponseOperator(DjangoOperator):
    def execute(self, context):
        order_uuid, data = json.loads(context['ti'].xcom_pull('poll-ytranslator', key='failed_ytranslator_response')).items()


# t1 = PythonOperator(task_id='order-ytranslator', dag=dag, python_callable=order_from_ytranslator)
t1 = PythonOperator(task_id='google-asr', dag=dag, python_callable=run_google_asr)
# t2 = PythonSensor(task_id='poll-ytranslator', dag=dag, python_callable=return_ytranslator)
t2 = GcpSpeechToTextRecognizeSpeechOperator(
    dag=dag,
    config=GASR_CONFIG,
    project_id="coresystem-171219",
    gcp_conn_id="full_gcp_conn",
    audio= {"uri": "{{ dag_run.conf['media_url']}}"},
    task_id="run_google_asr"
)
t3 = ShouldUnpackOperator(task_id='should-unpack', dag=dag)
t4 = UnpackYTranslator(task_id='unpack-ytranslator', dag=dag)
t5 = ShouldTriggerFailedResponseOperator(task_id="should-trigger-failed", dag=dag)
t6 = FailedResponseOperator(task_id='failed-response', dag=dag)

t1 >> t4
