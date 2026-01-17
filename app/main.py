from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import logging
from app.queue.producer import QueueProducer
from app.database.db import init_db

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Stock Bot")
producer = QueueProducer()

# Buat semua tabel
init_db()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up webhook server...")

@app.on_event("shutdown")
async def shutdown_event():
    producer.close()
    logger.info("Shutting down webhook server...")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post(f"/webhook/{WEBHOOK_SECRET}")
async def webhook_handler(request: Request):
    try:
        update = await request.json()
        logger.info(f"Received update: {update.get('update_id')}")
        
        # Push ke queue untuk diproses worker
        producer.publish_update(update)
        
        return JSONResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Telegram Stock Bot API is running"}