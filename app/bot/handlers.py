import os
import logging
from sqlalchemy.orm import Session
from app.bot.telegram_api import TelegramAPI
from app.services.stock_service import StockService
from app.database import crud
from app.database.models import User

logger = logging.getLogger(__name__)

class BotHandler:
    def __init__(self):
        self.telegram = TelegramAPI()
        self.stock_service = StockService()
    
    def handle_message(self, message: dict, db: Session):
        """Handle incoming message"""
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user_data = message["from"]
        
        # Simpan/update user
        user = crud.get_or_create_user(
            db,
            telegram_id=user_data["id"],
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name")
        )
        
        # Handle commands
        if text.startswith("/start"):
            self._handle_start(chat_id)
        elif text.startswith("/help"):
            self._handle_help(chat_id)
        elif text.startswith("/harga"):
            self._handle_stock_price(chat_id, text)
        elif text.startswith("/watchlist"):
            self._handle_watchlist(chat_id, user, db)
        elif text.startswith("/tambah"):
            self._handle_add_watchlist(chat_id, user, text, db)
        elif text.startswith("/hapus"):
            self._handle_remove_watchlist(chat_id, user, text, db)
        elif text.startswith("/info"):
            self._handle_stock_info(chat_id, text)
        else:
            # Anggap sebagai ticker symbol
            self._handle_stock_price(chat_id, text)
    
    def handle_callback(self, callback: dict, db: Session):
        """Handle callback query dari inline buttons"""
        callback_id = callback["id"]
        chat_id = callback["message"]["chat"]["id"]
        data = callback["data"]
        
        if data.startswith("stock_"):
            symbol = data.replace("stock_", "")
            self._handle_stock_info(chat_id, f"/info {symbol}")
        
        # Answer callback query
        self.telegram.answer_callback_query(callback_id)
    
    def _handle_start(self, chat_id: int):
        """Handle /start command"""
        message = (
            "🤖 *Selamat datang di Stock Bot!*\n\n"
            "Bot ini membantu Anda memantau harga saham.\n\n"
            "Gunakan /help untuk melihat daftar perintah."
        )
        self.telegram.send_message(chat_id, message)
    
    def _handle_help(self, chat_id: int):
        """Handle /help command"""
        message = (
            "📋 *Daftar Perintah:*\n\n"
            "/harga BBCA - Cek harga saham\n"
            "/info BBCA - Info detail saham\n"
            "/watchlist - Lihat watchlist Anda\n"
            "/tambah BBCA - Tambah ke watchlist\n"
            "/hapus BBCA - Hapus dari watchlist\n\n"
            "Atau langsung ketik kode saham (contoh: BBCA)"
        )
        self.telegram.send_message(chat_id, message)
    
    def _handle_stock_price(self, chat_id: int, text: str):
        """Handle stock price request"""
        parts = text.split()
        if len(parts) < 2 and not text.startswith("/"):
            symbol = text.strip().upper()
        elif len(parts) >= 2:
            symbol = parts[1].upper()
        else:
            self.telegram.send_message(
                chat_id,
                "❌ Format salah. Gunakan: /harga BBCA"
            )
            return
        
        stock_data = self.stock_service.get_stock_price(symbol)
        
        if stock_data:
            change_emoji = "🟢" if stock_data["change_percent"] >= 0 else "🔴"
            message = (
                f"📈 *{stock_data['symbol']}*\n\n"
                f"Harga: Rp {stock_data['price']:,.0f}\n"
                f"Perubahan: {change_emoji} {stock_data['change_percent']:+.2f}%\n"
                f"Volume: {stock_data['volume']:,}\n"
                f"Updated: {stock_data['updated']}"
            )
            
            # Inline keyboard
            keyboard = {
                "inline_keyboard": [[
                    {"text": "ℹ️ Info Detail", "callback_data": f"stock_{symbol}"}
                ]]
            }
            
            self.telegram.send_message(chat_id, message, reply_markup=keyboard)
        else:
            self.telegram.send_message(
                chat_id,
                f"❌ Saham {symbol} tidak ditemukan."
            )
    
    def _handle_stock_info(self, chat_id: int, text: str):
        """Handle detailed stock info"""
        parts = text.split()
        if len(parts) >= 2:
            symbol = parts[1].upper()
        else:
            self.telegram.send_message(
                chat_id,
                "❌ Format salah. Gunakan: /info BBCA"
            )
            return
        
        info = self.stock_service.get_stock_info(symbol)
        
        if info:
            message = (
                f"ℹ️ *{info['symbol']} - {info['name']}*\n\n"
                f"Harga: Rp {info['price']:,.0f}\n"
                f"52W High: Rp {info['high_52w']:,.0f}\n"
                f"52W Low: Rp {info['low_52w']:,.0f}\n"
                f"Market Cap: Rp {info['market_cap']:,.0f}M\n"
                f"P/E Ratio: {info['pe_ratio']:.2f}"
            )
            self.telegram.send_message(chat_id, message)
        else:
            self.telegram.send_message(
                chat_id,
                f"❌ Info untuk {symbol} tidak tersedia."
            )
    
    def _handle_watchlist(self, chat_id: int, user: User, db: Session):
        """Handle watchlist command"""
        watchlist = crud.get_user_watchlist(db, user.id)
        
        if watchlist:
            message = "⭐ *Watchlist Anda:*\n\n"
            for item in watchlist:
                stock_data = self.stock_service.get_stock_price(item.symbol)
                if stock_data:
                    change_emoji = "🟢" if stock_data["change_percent"] >= 0 else "🔴"
                    message += (
                        f"• {item.symbol}: Rp {stock_data['price']:,.0f} "
                        f"{change_emoji} {stock_data['change_percent']:+.2f}%\n"
                    )
            self.telegram.send_message(chat_id, message)
        else:
            self.telegram.send_message(
                chat_id,
                "📋 Watchlist Anda masih kosong.\nGunakan /tambah BBCA untuk menambah."
            )
    
    def _handle_add_watchlist(self, chat_id: int, user: User, text: str, db: Session):
        """Handle add to watchlist"""
        parts = text.split()
        if len(parts) >= 2:
            symbol = parts[1].upper()
            
            # Validasi saham exists
            if self.stock_service.get_stock_price(symbol):
                if crud.add_to_watchlist(db, user.id, symbol):
                    self.telegram.send_message(
                        chat_id,
                        f"✅ {symbol} ditambahkan ke watchlist."
                    )
                else:
                    self.telegram.send_message(
                        chat_id,
                        f"ℹ️ {symbol} sudah ada di watchlist."
                    )
            else:
                self.telegram.send_message(
                    chat_id,
                    f"❌ Saham {symbol} tidak ditemukan."
                )
        else:
            self.telegram.send_message(
                chat_id,
                "❌ Format salah. Gunakan: /tambah BBCA"
            )
    
    def _handle_remove_watchlist(self, chat_id: int, user: User, text: str, db: Session):
        """Handle remove from watchlist"""
        parts = text.split()
        if len(parts) >= 2:
            symbol = parts[1].upper()
            
            if crud.remove_from_watchlist(db, user.id, symbol):
                self.telegram.send_message(
                    chat_id,
                    f"✅ {symbol} dihapus dari watchlist."
                )
            else:
                self.telegram.send_message(
                    chat_id,
                    f"❌ {symbol} tidak ada di watchlist."
                )
        else:
            self.telegram.send_message(
                chat_id,
                "❌ Format salah. Gunakan: /hapus BBCA"
            )