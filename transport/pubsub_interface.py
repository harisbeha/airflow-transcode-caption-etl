# from google.cloud import pubsub_v1
# from google.api_core.exceptions import AlreadyExists


class PubSubService(object):
    def __init__(self, topic_name, subscription_name=None):
        self.topic_name = topic_name
        self.publisher_name = subscription_name if subscription_name else topic_name
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()

        try:
            self.topic = "{}".format(self.topic_name)
            self.publisher.api.create_topic(self.topic)
        except AlreadyExists:
            pass
        try:
            self.subscription = "{}".format(subscription_name)
            self.subscriber.api.create_subscription(self.subscription, self.topic, ack_deadline_seconds=10)
        except AlreadyExists:
            pass

    def publish(self, data):
        self.publisher.publish(self.topic, data=data)

    def pull_from_subscription(self):
        pull = self.subscriber.api.pull(subscription=self.subscription, max_messages=1, return_immediately=True)
        if not pull.received_messages:
            return None, None
        return pull.received_messages[0].ack_id, pull.received_messages[0].message

    def acknowledge_pull(self, ack_id):
        self.subscriber.api.acknowledge(ack_ids=[ack_id], subscription=self.subscription)