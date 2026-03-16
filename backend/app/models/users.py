from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class User(Base):
    __tablename__ = "users"

    vk_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), default='Игрок')
    avatar = Column(String(255), default='')
    character_class = Column(String(50), default='warrior')
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    
    strength = Column(Integer, default=10)
    agility = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    spirit = Column(Integer, default=10)
    vitality = Column(Integer, default=10)
    
    hp = Column(Integer, default=150)
    max_hp = Column(Integer, default=150)
    mana = Column(Integer, default=50)
    max_mana = Column(Integer, default=50)
    stamina = Column(Integer, default=150)
    max_stamina = Column(Integer, default=150)
    stamina_last_regen = Column(TIMESTAMP, default=func.now())
    
    fatigue_state = Column(String(20), default='fit')
    fatigue_penalty = Column(JSONB, default={})
    stamina_warnings_sent = Column(JSONB, default=[])
    
    gold = Column(Integer, default=0)
    location = Column(String(50), default='village', index=True)
    story_context = Column(JSONB, default=[])
    
    in_combat = Column(Boolean, default=False, index=True)
    combat_opponent_id = Column(Integer, nullable=True)
    
    inventory_slots = Column(Integer, default=20)
    equipment = Column(JSONB, default={})
    active_buffs = Column(JSONB, default=[])
    active_debuffs = Column(JSONB, default=[])
    
    created_at = Column(TIMESTAMP, default=func.now())
    last_login = Column(TIMESTAMP, default=func.now())