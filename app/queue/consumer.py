import pika
import os
import logging
import time

logger = logging.getLogger(__name__)

class QueueConsumer:
    def __init__(self):
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
        self.queue_name = os.getenv("QUEUE_NAME", "telegram_updates")
        
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Membuat koneksi ke RabbitMQ dengan retry"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
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
                    blocked_connection_timeout=300
                )
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                
                # Declare queue
                self.channel.queue_declare(
                    queue=self.queue_name,
                    durable=True
                )
                
                # Set prefetch count untuk load balancing antar worker
                self.channel.basic_qos(prefetch_count=1)
                
                logger.info(f"Consumer connected to RabbitMQ at {self.rabbitmq_host}")
                return
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise
    
    def consume(self, callback):
        """Mulai consume messages dari queue"""
        try:
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback,
                auto_ack=False  # Manual acknowledgment
            )
            logger.info(f"Starting to consume from {self.queue_name}")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.channel.stop_consuming()
        except Exception as e:
            logger.error(f"Error consuming: {e}")
            raise
    
    def close(self):
        """Tutup koneksi"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()