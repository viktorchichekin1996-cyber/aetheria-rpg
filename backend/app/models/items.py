# backend/app/models/items.py
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, func, Text
from sqlalchemy.types import JSON  # Используем универсальный JSON
from app.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    item_type = Column(String(50), nullable=False)
    rarity = Column(String(20), default='common')
    slot = Column(String(50), nullable=True)
    
    # ИСПРАВЛЕНО: JSON вместо JSONB
    stats = Column(JSON, default={})
    
    min_level = Column(Integer, default=1)
    durability = Column(Integer, default=100)
    max_durability = Column(Integer, default=100)
    value = Column(Integer, default=0)
    buy_price = Column(Integer, default=0)
    
    # ИСПРАВЛЕНО: JSON вместо JSONB
    effects = Column(JSON, default=[])
    
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
    
    # ИСПРАВЛЕНО: JSON вместо JSONB
    bonus_stats = Column(JSON, default={})
    
    enchantment_level = Column(Integer, default=0)
    acquired_at = Column(TIMESTAMP, default=func.now())