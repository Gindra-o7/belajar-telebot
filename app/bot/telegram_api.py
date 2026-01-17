import os
import requests
import logging

logger = logging.getLogger(__name__)

class TelegramAPI:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, chat_id: int, text: str, reply_markup=None):
        """Kirim pesan ke user"""
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None
    
    def answer_callback_query(self, callback_query_id: str, text: str = ""):
        """Answer callback query"""
        url = f"{self.base_url}/answerCallbackQuery"
        
        payload = {
            "callback_query_id": callback_query_id,
            "text": text
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to answer callback: {e}")
            return None
    
    def set_webhook(self, webhook_url: str):
        """Set webhook URL"""
        url = f"{self.base_url}/setWebhook"
        
        payload = {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Webhook set to: {webhook_url}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            return None
    
    def delete_webhook(self):
        """Delete webhook"""
        url = f"{self.base_url}/deleteWebhook"
        
        try:
            response = requests.post(url, timeout=10)
            response.raise_for_status()
            logger.info("Webhook deleted")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to delete webhook: {e}")
            return None