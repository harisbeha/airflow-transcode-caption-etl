from rest_framework.serializers import ModelSerializer
from workflow.models import Job, Event, WorkflowTracker


class JobSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'


class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class WorkflowTrackerSerializer(ModelSerializer):
    class Meta:
        model = WorkflowTracker
        fields = '__all__'
