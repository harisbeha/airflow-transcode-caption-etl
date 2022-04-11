from rest_framework.routers import SimpleRouter

from workflow.views import JobViewSet, WorkflowTrackerViewSet, EventViewSet


router = SimpleRouter()
router.register('job', JobViewSet)
router.register('event', EventViewSet)
router.register('workflow_tracker', WorkflowTrackerViewSet)

urlpatterns = router.urls
