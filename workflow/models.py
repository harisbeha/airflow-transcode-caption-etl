from django.contrib.auth.models import User
from django.db.models import (
    Model, CharField, IntegerField, UUIDField,
    TextField, OneToOneField, deletion, BooleanField,
    DateTimeField, ForeignKey, DO_NOTHING
)
from django.db.models.manager import Manager
from datetime import timedelta
import json, uuid

from service.enums import WorkflowTrackerEnum


class Job(Model):
    job_id = UUIDField(primary_key=True, verbose_name='job_id', default=uuid.uuid4)
    job_name = CharField(max_length=100, null=False, db_index=True)
    external_id = CharField(max_length=100, null=True, blank=True, db_index=True)
    order = OneToOneField(to="orders.OrderItem", on_delete=DO_NOTHING)
    deleted = BooleanField(default=False)

    def __str__(self):
        return str(self.job_id)

class Event(Model):
    created = DateTimeField(auto_now_add=True)
    event_type = CharField(max_length=100, null=False)
    data = TextField(default=json.dumps({}))
    uuid = CharField(max_length=100, null=False, db_index=True)
    timestamp = DateTimeField(auto_now_add=True)
    reference_url = CharField(max_length=100, null=False)

    def __str__(self):
        return "[{0}][ID: {1}] {2} @ {3}".format(self.event_type, self.uuid, self.data, self.timestamp)


class WorkflowTracker(Model):
    job = OneToOneField(to=Job, on_delete=DO_NOTHING)
    workflow_steps = TextField(
        default=json.dumps(
            dict(
                standard_workflow=dict(
                    status=WorkflowTrackerEnum.PENDING.value,
                    progress="0%"
                )
            )
        )
    )

    def get_current_actions_and_progress(self):
        workflow_steps = self.json
        steps_in_progress = filter(lambda x: x[1]['status'] in [WorkflowTrackerEnum.IN_PROGRESS.value, WorkflowTrackerEnum.FINALIZING.value], workflow_steps.items())
        if not steps_in_progress:
            return "INITIALIZING"
        else:
            cleaned_steps = ["{}: {}".format(s[0], s[1]['progress']) for s in steps_in_progress]
            return "\t".join(cleaned_steps)

    @property
    def json(self):
        return json.loads(self.workflow_steps)

    def __str__(self):
        return "{}: {}".format(self.job_id, self.get_current_actions_and_progress())
