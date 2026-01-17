"""
Queue module untuk RabbitMQ producer dan consumer
"""

from .producer import QueueProducer
from .consumer import QueueConsumer

__all__ = ["QueueProducer", "QueueConsumer"]
