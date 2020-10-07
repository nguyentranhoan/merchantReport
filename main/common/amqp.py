import logging
from typing import Type, Optional, Dict, List

from injector import singleton, inject
from kombu import Producer, Consumer, Connection
from kombu.mixins import ConsumerMixin, ConsumerProducerMixin

LOGGER = logging.getLogger(__name__)

CONSUMER_KEY = '__consumer__'


def is_consumer(cls):
    return hasattr(cls, CONSUMER_KEY)


def consumer():
    def decorator(cls):
        setattr(cls, CONSUMER_KEY, {})
        return singleton(inject(cls))

    return decorator


@singleton
@inject
class Worker(ConsumerProducerMixin):
    def __init__(self, connection: Connection, consumers: List[Consumer]):
        self.consumers = consumers
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        consumer = [consumer.get_consumer(Consumer) for consumer in self.consumers]
        return consumer


class Publisher:
    def __init__(self, producer: Producer):
        self.producer = producer

    @property
    def binding(self) -> Dict[Type, str]:
        return {}

    def publish(self, body, routing_key: Optional[str] = None):
        if routing_key is None and type(body) in self.binding:
            routing_key = self.binding[type(body)]
        if routing_key is None:
            raise ValueError('unspecified routing key')
        return self.producer.publish(body=body,
                                     routing_key=routing_key,
                                     retry=True,
                                     retry_policy={'interval_start': 0, 'interval_step': 2, 'interval_max': 30,
                                                   'max_retries': 30})
