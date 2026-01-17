# 📈 Telegram Stock Bot

Bot Telegram untuk monitoring saham dengan arsitektur scalable.

## 🏗️ Arsitektur

```
Telegram → FastAPI Webhook → RabbitMQ Queue → Workers (1-N) → PostgreSQL
```

**Keuntungan:**

- Handle banyak user bersamaan
- Tidak ada message loss (queue persistence)
- Mudah di-scale (tambah workers sesuai load)
- Load balancing otomatis

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Queue**: RabbitMQ
- **Container**: Docker Compose
- **Python**: 3.11

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy .env template
cp .env.example .env

# Edit .env dan isi TELEGRAM_BOT_TOKEN dari @BotFather
```

### 2. Start Services

```bash
docker-compose up -d --build
```

### 3. Set Webhook

**Development (dengan ngrok):**

```bash
# Jalankan ngrok
ngrok http 8000

# Set webhook
python set_webhook.py https://xxxx.ngrok.io/webhook/your_webhook_secret
```

**Production:**

```bash
python set_webhook.py https://yourdomain.com/webhook/your_webhook_secret
```

### 4. Test Bot

Buka Telegram dan test:

- `/start` - Mulai bot
- `/help` - Lihat bantuan
- `/harga BBCA` - Cek harga saham
- `BBCA` - Shortcut

## 🎮 Bot Commands

| Command          | Deskripsi            |
| ---------------- | -------------------- |
| `/start`         | Mulai bot            |
| `/help`          | Bantuan              |
| `/harga SYMBOL`  | Cek harga saham      |
| `/info SYMBOL`   | Info detail saham    |
| `/watchlist`     | Lihat watchlist      |
| `/tambah SYMBOL` | Tambah ke watchlist  |
| `/hapus SYMBOL`  | Hapus dari watchlist |

## ⚙️ Scale Workers

```bash
# Scale ke 5 workers
docker-compose up -d --scale worker=5

# Scale ke 10 workers
docker-compose up -d --scale worker=10
```

## 🔍 Monitoring

```bash
# Lihat logs
docker-compose logs -f

# Status services
docker-compose ps

# RabbitMQ Management UI
# http://localhost:15672 (guest/guest)

# Database access
docker-compose exec postgres psql -U stockbot -d stockbot_db
```

## 🔧 Customization

### Tambah Saham Baru

Edit `app/services/stock_service.py`:

```python
self.stocks = {
    "BBCA": {"name": "Bank Central Asia Tbk", "base_price": 9500},
    "NEWSYMBOL": {"name": "Company Name", "base_price": 1000},
}
```

### Integrasi API Real

Ganti dummy data di `StockService.get_stock_price()` dengan API call ke:

- Yahoo Finance
- Alpha Vantage
- IDX API
- RTI Business API

## 🐛 Troubleshooting

**Bot tidak merespon?**

```bash
# Cek webhook
python set_webhook.py info

# Cek logs
docker-compose logs -f webhook worker
```

**Worker tidak proses message?**

```bash
docker-compose restart worker
```

**Database error?**

```bash
docker-compose restart postgres
```

---

**Bot berhasil dibuat! 🎉**
