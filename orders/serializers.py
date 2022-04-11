from rest_framework.serializers import ModelSerializer
from orders.models import OrderItem, OutputProduct, Preset
from django.conf import settings
from transport.pubsub_interface import PubSubService
import json


class OutputProductSerializer(ModelSerializer):
    class Meta:
        model = OutputProduct
        fields = '__all__'

class PresetSerializer(ModelSerializer):

    class Meta:
        model = Preset
        fields = [
            "name",
            "source_language",
            "turnaround_time",
            "global_default",
            "is_default",
            "target_languages",
            "speaker_id",
            "rush_12",
            "true_verbatim",
            "rush_24",
        ]

class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

    def create(self, validated_data):
        pass

    def publish(self, validated_data):
        instance = super(OrderItemSerializer, self).create(validated_data)
        # In the case that validated data did not contain the pointer and to not double dump the details
        validated_data.update({'uuid': instance.uuid, 'order_details': json.loads(instance.order_details)})
        pubsub_client = PubSubService(settings.NEW_ORDER_TOPIC)
        dumped_message = json.dumps(validated_data)
        pubsub_client.publish(dumped_message)
        return instance