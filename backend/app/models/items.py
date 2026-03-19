# backend/app/models/items.py
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from app.database import Base
import os

# Определяем тип данных JSON динамически (аналогично users.py)
def get_json_type():
    db_url = os.getenv("DATABASE_URL", "")
    if "postgresql" in db_url:
        return JSONB
    return JSON

JSONType = get_json_type()


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    item_type = Column(String(50), nullable=False)
    rarity = Column(String(20), default='common')
    slot = Column(String(50), nullable=True)
    
    # Используем универсальный тип
    stats = Column(JSONType, default={})
    
    min_level = Column(Integer, default=1)
    durability = Column(Integer, default=100)
    max_durability = Column(Integer, default=100)
    value = Column(Integer, default=0)
    buy_price = Column(Integer, default=0)
    
    # Используем универсальный тип
    effects = Column(JSONType, default=[])
    
    soulbound = Column(Boolean, default=False)
    tradeable = Column(Boolean, default=True)
    icon = Column(String(10), default='📦')
    created_at = Column(TIMESTAMP, default=func.now())


class UserItem(Base):
    __tablename__ = "user_items"

    id = Column(Integer, primary_key=True, index=True)
    vk_id = Column(Integer, ForeignKey("users.vk_id", ondelete="CASCADE"), index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    quantity = Column(Integer, default=1)
    equipped = Column(Boolean, default=False)
    
    # Используем универсальный тип
    bonus_stats = Column(JSONType, default={})
    
    enchantment_level = Column(Integer, default=0)
    acquired_at = Column(TIMESTAMP, default=func.now())