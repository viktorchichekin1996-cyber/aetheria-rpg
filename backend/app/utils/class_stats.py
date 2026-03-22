# backend/app/utils/class_stats.py
from typing import Dict, List, Any, Optional  # Добавлен импорт Optional

# Базовые статы для каждого класса
# Формат: {strength, agility, intelligence, spirit, vitality}
CLASS_STATS: Dict[str, Dict[str, int]] = {
    "warrior": {
        "strength": 14, "agility": 10, "intelligence": 8, "spirit": 9, "vitality": 14,
        "hp_bonus": 50, "mana_bonus": 0, "stamina_bonus": 20
    },
    "paladin": {
        "strength": 12, "agility": 8, "intelligence": 10, "spirit": 14, "vitality": 13,
        "hp_bonus": 40, "mana_bonus": 20, "stamina_bonus": 10
    },
    "rogue": {
        "strength": 10, "agility": 15, "intelligence": 10, "spirit": 8, "vitality": 10,
        "hp_bonus": 10, "mana_bonus": 10, "stamina_bonus": 30
    },
    "hunter": {
        "strength": 11, "agility": 14, "intelligence": 9, "spirit": 10, "vitality": 11,
        "hp_bonus": 20, "mana_bonus": 10, "stamina_bonus": 20
    },
    "mage": {
        "strength": 6, "agility": 8, "intelligence": 16, "spirit": 12, "vitality": 8,
        "hp_bonus": -10, "mana_bonus": 60, "stamina_bonus": 0
    },
    "warlock": {
        "strength": 8, "agility": 9, "intelligence": 15, "spirit": 10, "vitality": 9,
        "hp_bonus": 0, "mana_bonus": 50, "stamina_bonus": 10
    },
    "priest": {
        "strength": 7, "agility": 7, "intelligence": 12, "spirit": 16, "vitality": 10,
        "hp_bonus": 10, "mana_bonus": 40, "stamina_bonus": 10
    },
    "druid": {
        "strength": 10, "agility": 9, "intelligence": 12, "spirit": 12, "vitality": 11,
        "hp_bonus": 20, "mana_bonus": 30, "stamina_bonus": 10
    },
    "shaman": {
        "strength": 9, "agility": 9, "intelligence": 13, "spirit": 14, "vitality": 10,
        "hp_bonus": 15, "mana_bonus": 35, "stamina_bonus": 10
    },
    "necromancer": {
        "strength": 8, "agility": 8, "intelligence": 15, "spirit": 13, "vitality": 9,
        "hp_bonus": 5, "mana_bonus": 45, "stamina_bonus": 5
    },
    "monk": {
        "strength": 11, "agility": 13, "intelligence": 10, "spirit": 11, "vitality": 12,
        "hp_bonus": 30, "mana_bonus": 15, "stamina_bonus": 25
    }
}

# Описания классов для API
CLASS_INFO: Dict[str, Dict[str, str]] = {
    "warrior": {"name": "Воин", "desc": "Мастер ближнего боя с высоким здоровьем и силой."},
    "paladin": {"name": "Паладин", "desc": "Святой воин, сочетающий силу оружия с магией света."},
    "rogue": {"name": "Разбойник", "desc": "Ловкий убийца, наносящий критические удары из тени."},
    "hunter": {"name": "Охотник", "desc": "Мастер дистанционного боя и выживания в дикой природе."},
    "mage": {"name": "Маг", "desc": "Повелитель стихий, обладающий огромной магической силой."},
    "warlock": {"name": "Чернокнижник", "desc": "Призыватель демонов и мастер темной магии."},
    "priest": {"name": "Жрец", "desc": "Целитель и защитник, черпающий силу в вере."},
    "druid": {"name": "Друид", "desc": "Хранитель природы, способный менять облик и управлять силами леса."},
    "shaman": {"name": "Шаман", "desc": "Посредник между мирами, управляющий духами стихий."},
    "necromancer": {"name": "Некромант", "desc": "Повелитель мертвых, поднимающий армии нежити."},
    "monk": {"name": "Монах", "desc": "Мастер боевых искусств, использующий энергию ци для ударов."}
}

def get_all_classes() -> List[Dict[str, Any]]:
    """Возвращает список всех доступных классов с описанием."""
    result = []
    for key, stats in CLASS_STATS.items():
        info = CLASS_INFO.get(key, {})
        result.append({
            "id": key,
            "name": info.get("name", key.capitalize()),
            "description": info.get("desc", ""),
            "base_stats": stats
        })
    return result

def get_class_info(class_id: str) -> Optional[Dict[str, Any]]:
    """Возвращает информацию о конкретном классе или None, если класс не найден."""
    if class_id not in CLASS_STATS:
        return None
    
    stats = CLASS_STATS[class_id]
    info = CLASS_INFO.get(class_id, {})
    
    return {
        "id": class_id,
        "name": info.get("name", class_id.capitalize()),
        "description": info.get("desc", ""),
        "base_stats": stats
    }

def apply_class_bonuses(user: Any, class_id: str) -> bool:
    """
    Применяет бонусы класса к пользователю.
    Возвращает True если успешно, False если класс не найден.
    """
    if class_id not in CLASS_STATS:
        return False
    
    bonuses = CLASS_STATS[class_id]
    
    # Обновляем основные характеристики
    user.strength = bonuses["strength"]
    user.agility = bonuses["agility"]
    user.intelligence = bonuses["intelligence"]
    user.spirit = bonuses["spirit"]
    user.vitality = bonuses["vitality"]
    
    # Пересчитываем ресурсы с учетом бонусов
    # Базовые значения (уровень 1) + бонус класса
    base_hp = 100 + (user.vitality * 3) # Пример формулы
    base_mana = 50 + (user.intelligence * 2)
    base_stamina = 100 + (user.agility * 1.5)
    
    user.max_hp = int(base_hp + bonuses.get("hp_bonus", 0))
    user.hp = user.max_hp
    
    user.max_mana = int(base_mana + bonuses.get("mana_bonus", 0))
    user.mana = user.max_mana
    
    user.max_stamina = int(base_stamina + bonuses.get("stamina_bonus", 0))
    user.stamina = user.max_stamina
    
    return True