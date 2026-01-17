#!/usr/bin/env python3
"""
Script untuk set/delete webhook Telegram Bot

Usage:
    python set_webhook.py <webhook_url>        # Set webhook
    python set_webhook.py delete               # Delete webhook
    python set_webhook.py info                 # Get webhook info

Example:
    python set_webhook.py https://yourdomain.com/webhook/secret123
    python set_webhook.py delete
"""

import sys
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def set_webhook(webhook_url: str):
    """Set webhook URL"""
    print(f"🔄 Setting webhook to: {webhook_url}")
    
    url = f"{BASE_URL}/setWebhook"
    payload = {
        "url": webhook_url,
        "allowed_updates": ["message", "callback_query"],
        "drop_pending_updates": True  # Hapus pending updates
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ok"):
            print("✅ Webhook set successfully!")
            print(f"   URL: {webhook_url}")
            return True
        else:
            print(f"❌ Failed: {result.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def delete_webhook():
    """Delete webhook"""
    print("🔄 Deleting webhook...")
    
    url = f"{BASE_URL}/deleteWebhook"
    payload = {"drop_pending_updates": True}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ok"):
            print("✅ Webhook deleted successfully!")
            return True
        else:
            print(f"❌ Failed: {result.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_webhook_info():
    """Get current webhook info"""
    print("🔄 Getting webhook info...")
    
    url = f"{BASE_URL}/getWebhookInfo"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ok"):
            info = result.get("result", {})
            print("\n📊 Webhook Info:")
            print(f"   URL: {info.get('url', 'Not set')}")
            print(f"   Pending updates: {info.get('pending_update_count', 0)}")
            print(f"   Max connections: {info.get('max_connections', 0)}")
            
            if info.get('last_error_date'):
                print(f"   ⚠️  Last error: {info.get('last_error_message')}")
            
            allowed_updates = info.get('allowed_updates', [])
            if allowed_updates:
                print(f"   Allowed updates: {', '.join(allowed_updates)}")
            
            return True
        else:
            print(f"❌ Failed: {result.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_bot_info():
    """Get bot information"""
    url = f"{BASE_URL}/getMe"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ok"):
            bot = result.get("result", {})
            print("\n🤖 Bot Info:")
            print(f"   Name: {bot.get('first_name')}")
            print(f"   Username: @{bot.get('username')}")
            print(f"   ID: {bot.get('id')}")
            return True
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
        return False


def main():
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment!")
        print("   Please set it in .env file")
        sys.exit(1)
    
    # Show bot info
    get_bot_info()
    print()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python set_webhook.py <webhook_url>")
        print("  python set_webhook.py delete")
        print("  python set_webhook.py info")
        print("\nExample:")
        print("  python set_webhook.py https://yourdomain.com/webhook/secret")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "delete":
        delete_webhook()
    elif command == "info":
        get_webhook_info()
    elif command.startswith("http"):
        set_webhook(command)
    else:
        print(f"❌ Invalid command: {command}")
        print("   Use 'delete', 'info', or provide a webhook URL")
        sys.exit(1)


if __name__ == "__main__":
    main()

