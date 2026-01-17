import pika
import json
import os
import logging

logger = logging.getLogger(__name__)

class QueueProducer:
    def __init__(self):
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
        self.queue_name = os.getenv("QUEUE_NAME", "telegram_updates")
        
        self.connection = None
        self.channel = None
        self._connection_attempted = False
    
    def _connect(self):
        """Membuat koneksi ke RabbitMQ"""
        if self._connection_attempted and self.connection and not self.connection.is_closed:
            return True
            
        try:
            credentials = pika.PlainCredentials(
                os.getenv("RABBITMQ_USER", "guest"),
                os.getenv("RABBITMQ_PASS", "guest")
            )
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
                connection_attempts=3,
                retry_delay=1
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue dengan durability
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            self._connection_attempted = True
            logger.info(f"Connected to RabbitMQ at {self.rabbitmq_host}")
            return True
        except Exception as e:
            self._connection_attempted = True
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def publish_update(self, update_data: dict):
        """Publish update ke queue"""
        try:
            if not self.connection or self.connection.is_closed:
                if not self._connect():
                    logger.warning("Cannot publish update: RabbitMQ not available")
                    return False
            
            message = json.dumps(update_data)
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            logger.info(f"Published update {update_data.get('update_id')}")
        except Exception as e:
            logger.error(f"Failed to publish update: {e}")
            self._connect()  # Reconnect
            raise
    
    def close(self):
        """Tutup koneksi"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()