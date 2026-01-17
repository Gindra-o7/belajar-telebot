import os
import json
import logging
from dotenv import load_dotenv
from app.queue.consumer import QueueConsumer
from app.bot.handlers import BotHandler
from app.database.db import SessionLocal

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UpdateWorker:
    def __init__(self):
        self.consumer = QueueConsumer()
        self.bot_handler = BotHandler()
        
    def process_update(self, update_data: dict):
        """Process single update dari queue"""
        db = SessionLocal()
        try:
            logger.info(f"Processing update {update_data.get('update_id')}")
            
            # Handle message
            if "message" in update_data:
                message = update_data["message"]
                self.bot_handler.handle_message(message, db)
            
            # Handle callback query (inline buttons)
            elif "callback_query" in update_data:
                callback = update_data["callback_query"]
                self.bot_handler.handle_callback(callback, db)
                
        except Exception as e:
            logger.error(f"Error processing update: {e}")
        finally:
            db.close()
    
    def start(self):
        """Start consuming messages dari queue"""
        logger.info("Worker started, waiting for updates...")
        
        def callback(ch, method, properties, body):
            try:
                update_data = json.loads(body)
                self.process_update(update_data)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error in callback: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        self.consumer.consume(callback)

if __name__ == "__main__":
    worker = UpdateWorker()
    worker.start()