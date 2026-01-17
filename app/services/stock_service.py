import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StockService:
    """
    Service untuk mengambil data saham.
    Dalam implementasi nyata, integrasikan dengan API seperti:
    - Yahoo Finance API
    - Alpha Vantage
    - IDX API
    - RTI Business API
    """
    
    def __init__(self):
        # Dummy data untuk demo
        self.stocks = {
            "BBCA": {"name": "Bank Central Asia Tbk", "base_price": 9500},
            "BBRI": {"name": "Bank Rakyat Indonesia Tbk", "base_price": 5200},
            "BMRI": {"name": "Bank Mandiri Tbk", "base_price": 6400},
            "TLKM": {"name": "Telkom Indonesia Tbk", "base_price": 3800},
            "ASII": {"name": "Astra International Tbk", "base_price": 5500},
            "UNVR": {"name": "Unilever Indonesia Tbk", "base_price": 4200},
            "BBNI": {"name": "Bank Negara Indonesia Tbk", "base_price": 5800},
            "GOTO": {"name": "GoTo Gojek Tokopedia Tbk", "base_price": 120},
        }
    
    def get_stock_price(self, symbol: str) -> dict:
        """
        Ambil harga saham real-time
        Implementasi nyata: panggil API eksternal
        """
        if symbol not in self.stocks:
            return None
        
        base = self.stocks[symbol]["base_price"]
        # Simulasi perubahan harga random
        change_percent = random.uniform(-5, 5)
        price = base * (1 + change_percent / 100)
        volume = random.randint(1000000, 50000000)
        
        return {
            "symbol": symbol,
            "name": self.stocks[symbol]["name"],
            "price": round(price),
            "change_percent": round(change_percent, 2),
            "volume": volume,
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_stock_info(self, symbol: str) -> dict:
        """
        Ambil informasi detail saham
        Implementasi nyata: panggil API eksternal
        """
        if symbol not in self.stocks:
            return None
        
        price_data = self.get_stock_price(symbol)
        base = self.stocks[symbol]["base_price"]
        
        return {
            "symbol": symbol,
            "name": self.stocks[symbol]["name"],
            "price": price_data["price"],
            "high_52w": round(base * 1.3),
            "low_52w": round(base * 0.7),
            "market_cap": random.randint(50000, 500000),
            "pe_ratio": round(random.uniform(10, 25), 2)
        }
    
    def get_multiple_stocks(self, symbols: list) -> list:
        """Ambil data multiple saham sekaligus"""
        results = []
        for symbol in symbols:
            data = self.get_stock_price(symbol)
            if data:
                results.append(data)
        return results