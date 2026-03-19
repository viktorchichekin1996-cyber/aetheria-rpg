# backend/app/models/users.py
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from app.database import Base
import os

# Определяем тип данных JSON динамически:
# Если используем PostgreSQL (в переменной DATABASE_URL есть 'postgresql'), используем JSONB.
# Иначе (для тестов на SQLite) используем стандартный JSON.
def get_json_type():
    db_url = os.getenv("DATABASE_URL", "")
    if "postgresql" in db_url:
        return JSONB
    return JSON

JSONType = get_json_type()


class User(Base):
    __tablename__ = "users"

    # Основные данные
    vk_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), default='Игрок')
    avatar = Column(String(255), default='')
    character_class = Column(String(50), default='warrior')
    
    # Прогрессия
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    
    # Базовые характеристики (Base Stats)
    strength = Column(Integer, default=10)
    agility = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    spirit = Column(Integer, default=10)
    vitality = Column(Integer, default=10)
    
    # Производные ресурсы (Derived Stats) - могут пересчитываться
    hp = Column(Integer, default=150)
    max_hp = Column(Integer, default=150)
    mana = Column(Integer, default=50)
    max_mana = Column(Integer, default=50)
    stamina = Column(Integer, default=150)
    max_stamina = Column(Integer, default=150)
    
    # Система выносливости
    stamina_last_regen = Column(TIMESTAMP, default=func.now())
    fatigue_state = Column(String(20), default='fit')
    # Используем универсальный тип JSON/JSONB
    fatigue_penalty = Column(JSONType, default={}) 
    stamina_warnings_sent = Column(JSONType, default=[])
    
    # Экономика и состояние
    gold = Column(Integer, default=0)
    location = Column(String(50), default='village', index=True)
    story_context = Column(JSONType, default=[])
    
    # Боевой статус
    in_combat = Column(Boolean, default=False, index=True)
    combat_opponent_id = Column(Integer, nullable=True)
    
    # Инвентарь и экипировка
    inventory_slots = Column(Integer, default=20)
    equipment = Column(JSONType, default={})
    active_buffs = Column(JSONType, default=[])
    active_debuffs = Column(JSONType, default=[])
    
    # Мета-данные
    created_at = Column(TIMESTAMP, default=func.now())
    last_login = Column(TIMESTAMP, default=func.now())

    @staticmethod
    def get_stat_modifier(stat_value: int) -> int:
        """
        Рассчитывает модификатор характеристики по таблице из ТЗ:
        1-3: -4
        4-5: -3
        6-7: -2
        8-9: -1
        10-11: 0
        12-13: +1
        ...
        
        Стандартная формула (stat - 10) // 2 дает для 1 значение -5, 
        поэтому добавляем корректировку для единицы согласно ТЗ.
        """
        if stat_value == 1:
            return -4
        return (stat_value - 10) // 2

    def get_full_stats(self) -> dict:
        """Возвращает полный расчет характеристик с модификаторами"""
        return {
            "strength": {
                "base": self.strength,
                "modifier": self.get_stat_modifier(self.strength),
                "formula": f"{self.strength} -> {self.get_stat_modifier(self.strength):+d}"
            },
            "agility": {
                "base": self.agility,
                "modifier": self.get_stat_modifier(self.agility),
                "formula": f"{self.agility} -> {self.get_stat_modifier(self.agility):+d}"
            },
            "intelligence": {
                "base": self.intelligence,
                "modifier": self.get_stat_modifier(self.intelligence),
                "formula": f"{self.intelligence} -> {self.get_stat_modifier(self.intelligence):+d}"
            },
            "spirit": {
                "base": self.spirit,
                "modifier": self.get_stat_modifier(self.spirit),
                "formula": f"{self.spirit} -> {self.get_stat_modifier(self.spirit):+d}"
            },
            "vitality": {
                "base": self.vitality,
                "modifier": self.get_stat_modifier(self.vitality),
                "formula": f"{self.vitality} -> {self.get_stat_modifier(self.vitality):+d}"
            },
            "resources": {
                "hp": f"{self.hp}/{self.max_hp}",
                "mana": f"{self.mana}/{self.max_mana}",
                "stamina": f"{self.stamina}/{self.max_stamina}"
            },
            "status": {
                "level": self.level,
                "exp": self.experience,
                "gold": self.gold,
                "location": self.location,
                "fatigue": self.fatigue_state
            }
        }