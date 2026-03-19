# backend/tests/test_player.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os

# Импортируем компоненты приложения
from app.main import app
from app.database import Base, get_db
from app.models.users import User

# Настройка тестовой БД (SQLite в памяти)
# Важно: используем check_same_thread=False для SQLite в тестах
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=True  # Включите логирование SQL для отладки, если нужно
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Переопределяем зависимость get_db для использования тестовой БД
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Применяем переопределение зависимости перед созданием клиента
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """
    Фикстура для создания таблиц перед каждым тестом и их удаления после.
    """
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    yield
    # Удаляем все таблицы после теста
    Base.metadata.drop_all(bind=engine)

def test_stat_modifier_calculation():
    """
    Проверка формулы расчета модификаторов характеристик.
    Тестирует статический метод модели User.
    """
    # Тестовые данные: (Stat Value, Expected Modifier)
    # 1-3: -4, 4-5: -3, ..., 10-11: 0, 12-13: +1, ...
    test_cases = [
        (1, -4), (3, -4),
        (4, -3), (5, -3),
        (6, -2), (7, -2),
        (8, -1), (9, -1),
        (10, 0), (11, 0),
        (12, 1), (13, 1),
        (14, 2), (15, 2),
        (18, 4), (19, 4),
        (20, 5)
    ]
    
    for stat_val, expected_mod in test_cases:
        calculated_mod = User.get_stat_modifier(stat_val)
        assert calculated_mod == expected_mod, f"Failed for stat {stat_val}: expected {expected_mod}, got {calculated_mod}"

def test_create_and_get_player():
    """
    Тест создания пользователя напрямую в БД и получения через API.
    """
    vk_id = 12345
    username = "TestHero"
    avatar_url = "https://example.com/avatar.jpg"
    
    # 1. Создаем пользователя напрямую через сессию БД (эмуляция регистрации)
    db = TestingSessionLocal()
    user = User(
        vk_id=vk_id, 
        username=username, 
        avatar=avatar_url,
        strength=12,  # Модификатор должен быть +1
        agility=8     # Модификатор должен быть -1
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 2. Делаем запрос к API получения данных игрока
    response = client.get(f"/api/v1/player/{vk_id}")
    
    # Проверка статуса ответа
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Detail: {response.text}"
    
    data = response.json()
    
    # Проверка основных данных
    assert data["vk_id"] == vk_id
    assert data["username"] == username
    assert data["avatar"] == avatar_url
    
    # 3. Делаем запрос к API получения статистики
    response_stats = client.get(f"/api/v1/player/{vk_id}/stats")
    assert response_stats.status_code == 200, f"Expected 200 for stats, got {response_stats.status_code}"
    
    stats_data = response_stats.json()
    assert stats_data["success"] is True
    
    player_stats = stats_data["data"]["stats"]
    
    # Проверка расчета модификаторов
    # Strength 12 -> (12-10)//2 = 1
    assert player_stats["strength"]["base"] == 12
    assert player_stats["strength"]["modifier"] == 1
    
    # Agility 8 -> (8-10)//2 = -1
    assert player_stats["agility"]["base"] == 8
    assert player_stats["agility"]["modifier"] == -1
    
    db.close()

def test_player_not_found():
    """
    Тест обработки случая, когда игрок не найден.
    """
    non_existent_vk_id = 99999
    
    response = client.get(f"/api/v1/player/{non_existent_vk_id}")
    
    # Ожидаем ошибку 404
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    error_data = response.json()
    assert "detail" in error_data
    assert "not found" in error_data["detail"].lower()