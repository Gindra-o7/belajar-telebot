from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.models import User, Watchlist, StockQuery
import logging

logger = logging.getLogger(__name__)

def get_or_create_user(
    db: Session,
    telegram_id: int,
    username: str = None,
    first_name: str = None,
    last_name: str = None
) -> User:
    """Get user atau buat baru jika belum ada"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user: {telegram_id}")
    else:
        # Update user info jika ada perubahan
        updated = False
        if username and user.username != username:
            user.username = username
            updated = True
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updated = True
        
        if updated:
            db.commit()
            db.refresh(user)
    
    return user

def get_user_watchlist(db: Session, user_id: int) -> list:
    """Ambil semua watchlist user"""
    return db.query(Watchlist).filter(Watchlist.user_id == user_id).all()

def add_to_watchlist(db: Session, user_id: int, symbol: str) -> bool:
    """Tambah symbol ke watchlist"""
    try:
        watchlist_item = Watchlist(user_id=user_id, symbol=symbol)
        db.add(watchlist_item)
        db.commit()
        logger.info(f"Added {symbol} to watchlist for user {user_id}")
        return True
    except IntegrityError:
        db.rollback()
        logger.info(f"{symbol} already in watchlist for user {user_id}")
        return False

def remove_from_watchlist(db: Session, user_id: int, symbol: str) -> bool:
    """Hapus symbol dari watchlist"""
    item = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.symbol == symbol
    ).first()
    
    if item:
        db.delete(item)
        db.commit()
        logger.info(f"Removed {symbol} from watchlist for user {user_id}")
        return True
    return False

def log_stock_query(db: Session, user_id: int, symbol: str, query_type: str):
    """Log query untuk analytics"""
    try:
        query = StockQuery(
            user_id=user_id,
            symbol=symbol,
            query_type=query_type
        )
        db.add(query)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to log query: {e}")

def get_popular_stocks(db: Session, limit: int = 10) -> list:
    """Ambil saham paling sering dicari"""
    from sqlalchemy import func
    
    results = db.query(
        StockQuery.symbol,
        func.count(StockQuery.symbol).label('count')
    ).group_by(
        StockQuery.symbol
    ).order_by(
        func.count(StockQuery.symbol).desc()
    ).limit(limit).all()
    
    return [{"symbol": r.symbol, "count": r.count} for r in results]