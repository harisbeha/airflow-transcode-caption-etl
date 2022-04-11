from rest_framework.viewsets import ModelViewSet
from service.custom_auth import CustomAuthentication
from workflow.serializers import JobSerializer, EventSerializer, WorkflowTrackerSerializer
from workflow.models import Job, Event, WorkflowTracker


class JobViewSet(ModelViewSet):
    queryset = Job.objects.filter(deleted=False)
    serializer_class = JobSerializer
    authentication_classes = [CustomAuthentication]


class EventViewSet(ModelViewSet):
    queryset = Event.objects.filter()
    serializer_class = EventSerializer
    authentication_classes = [CustomAuthentication]


class WorkflowTrackerViewSet(ModelViewSet):
    queryset = WorkflowTracker.objects.filter(job__deleted=False)
    serializer_class = WorkflowTrackerSerializer
    authentication_classes = [CustomAuthentication]
