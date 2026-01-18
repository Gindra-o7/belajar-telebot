import os
import time
import logging
import subprocess
import pika
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkerAutoscaler:
    def __init__(self):
        # RabbitMQ Configuration
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
        self.rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
        self.rabbitmq_pass = os.getenv("RABBITMQ_PASS", "guest")
        self.queue_name = os.getenv("QUEUE_NAME", "telegram_updates")
        
        # Scaling Configuration
        self.min_workers = int(os.getenv("MIN_WORKERS", 1))
        self.max_workers = int(os.getenv("MAX_WORKERS", 10))
        self.scale_up_threshold = int(os.getenv("SCALE_UP_THRESHOLD", 10))  # messages per worker
        self.scale_down_threshold = int(os.getenv("SCALE_DOWN_THRESHOLD", 2))  # messages per worker
        self.check_interval = int(os.getenv("CHECK_INTERVAL", 30))  # seconds
        self.cooldown_period = int(os.getenv("COOLDOWN_PERIOD", 60))  # seconds
        
        # Service name in docker-compose
        self.worker_service = os.getenv("WORKER_SERVICE_NAME", "worker")
        self.compose_file = os.getenv("COMPOSE_FILE", "docker-compose.yml")
        
        self.last_scale_time = 0
        self.current_workers = self.min_workers
        
    def get_queue_length(self):
        """Get jumlah messages di RabbitMQ queue"""
        try:
            credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=2
            )
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            # Passive declare untuk get queue info tanpa create
            queue = channel.queue_declare(queue=self.queue_name, passive=True)
            message_count = queue.method.message_count
            
            connection.close()
            return message_count
        except Exception as e:
            logger.error(f"Error getting queue length: {e}")
            return 0
    
    def get_current_worker_count(self):
        """Get jumlah worker containers yang running"""
        try:
            result = subprocess.run(
                ["docker-compose", "-f", self.compose_file, "ps", "-q", self.worker_service],
                capture_output=True,
                text=True,
                check=True
            )
            # Count non-empty lines (container IDs)
            containers = [line for line in result.stdout.strip().split('\n') if line]
            count = len(containers)
            self.current_workers = count if count > 0 else self.min_workers
            return self.current_workers
        except Exception as e:
            logger.error(f"Error getting worker count: {e}")
            return self.current_workers
    
    def scale_workers(self, target_count):
        """Scale workers ke target count"""
        if target_count < self.min_workers:
            target_count = self.min_workers
        elif target_count > self.max_workers:
            target_count = self.max_workers
        
        if target_count == self.current_workers:
            return False
        
        try:
            logger.info(f"Scaling workers from {self.current_workers} to {target_count}")
            subprocess.run(
                ["docker-compose", "-f", self.compose_file, "up", "-d", "--scale", 
                 f"{self.worker_service}={target_count}", "--no-recreate"],
                check=True,
                capture_output=True
            )
            self.current_workers = target_count
            self.last_scale_time = time.time()
            logger.info(f"Successfully scaled to {target_count} workers")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error scaling workers: {e}")
            logger.error(f"stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
            return False
    
    def calculate_target_workers(self, queue_length):
        """Calculate berapa workers yang dibutuhkan"""
        if queue_length == 0:
            return self.min_workers
        
        # Calculate workers based on messages per worker threshold
        target = queue_length // self.scale_up_threshold
        
        # Add buffer worker
        if queue_length % self.scale_up_threshold > 0:
            target += 1
        
        # Ensure within bounds
        target = max(self.min_workers, min(target, self.max_workers))
        
        return target
    
    def should_scale(self, queue_length, current_workers):
        """Determine apakah perlu scale up atau down"""
        # Check cooldown period
        if time.time() - self.last_scale_time < self.cooldown_period:
            return None
        
        if current_workers == 0:
            return self.min_workers
        
        messages_per_worker = queue_length / current_workers if current_workers > 0 else 0
        
        # Scale up jika messages per worker > threshold
        if messages_per_worker > self.scale_up_threshold and current_workers < self.max_workers:
            new_count = min(current_workers + 1, self.max_workers)
            logger.info(f"Scale up trigger: {messages_per_worker:.1f} msgs/worker > {self.scale_up_threshold}")
            return new_count
        
        # Scale down jika messages per worker < threshold dan workers > min
        if messages_per_worker < self.scale_down_threshold and current_workers > self.min_workers:
            new_count = max(current_workers - 1, self.min_workers)
            logger.info(f"Scale down trigger: {messages_per_worker:.1f} msgs/worker < {self.scale_down_threshold}")
            return new_count
        
        return None
    
    def run(self):
        """Main loop untuk monitoring dan scaling"""
        logger.info("Worker Autoscaler started")
        logger.info(f"Configuration:")
        logger.info(f"  Min workers: {self.min_workers}")
        logger.info(f"  Max workers: {self.max_workers}")
        logger.info(f"  Scale up threshold: {self.scale_up_threshold} msgs/worker")
        logger.info(f"  Scale down threshold: {self.scale_down_threshold} msgs/worker")
        logger.info(f"  Check interval: {self.check_interval}s")
        logger.info(f"  Cooldown period: {self.cooldown_period}s")
        
        # Initial scale to min workers
        self.get_current_worker_count()
        if self.current_workers < self.min_workers:
            self.scale_workers(self.min_workers)
        
        while True:
            try:
                # Get metrics
                queue_length = self.get_queue_length()
                current_workers = self.get_current_worker_count()
                
                messages_per_worker = queue_length / current_workers if current_workers > 0 else 0
                
                logger.info(
                    f"Queue: {queue_length} msgs | "
                    f"Workers: {current_workers} | "
                    f"Load: {messages_per_worker:.1f} msgs/worker"
                )
                
                # Check if scaling needed
                target_workers = self.should_scale(queue_length, current_workers)
                
                if target_workers is not None:
                    self.scale_workers(target_workers)
                else:
                    logger.debug("No scaling needed")
                
            except KeyboardInterrupt:
                logger.info("Autoscaler stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in autoscaler loop: {e}")
            
            # Wait before next check
            time.sleep(self.check_interval)


if __name__ == "__main__":
    autoscaler = WorkerAutoscaler()
    autoscaler.run()
