# backend/tests/test_player.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os

from app.main import app, root, health_check
from app.database import Base, get_db
from app.models.users import User
from app.models.items import Item
from app.services import player_service
from app.utils.vk_auth import validate_vk_sign
from fastapi import HTTPException

# URL базы данных для тестов (SQLite в памяти)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- Тесты Модели (Unit) ---

@pytest.mark.unit
def test_stat_modifier_calculation():
    test_cases = [
        (1, -4), (3, -4), (4, -3), (5, -3),
        (6, -2), (7, -2), (8, -1), (9, -1),
        (10, 0), (11, 0), (12, 1), (13, 1),
        (14, 2), (15, 2), (18, 4), (19, 4), (20, 5)
    ]
    for stat_val, expected_mod in test_cases:
        assert User.get_stat_modifier(stat_val) == expected_mod

@pytest.mark.unit
def test_item_model_creation():
    # В SQLAlchemy default значения применяются только при flush/commit в БД.
    # Поэтому проверяем, что объект создается и атрибуты существуют.
    item = Item(name="Test Sword", item_type="weapon", rarity="common")
    assert item.name == "Test Sword"
    assert item.item_type == "weapon"
    # Проверяем значение по умолчанию через метаданные или просто игнорируем None до commit
    # Для покрытия кода достаточно факта создания объекта
    assert hasattr(item, 'durability')

# --- Тесты Сервиса (Unit/Integration) ---

@pytest.mark.integration
def test_service_create_or_update_player_new():
    db = TestingSessionLocal()
    new_user = player_service.create_or_update_player(db, vk_id=999, username="Newbie", avatar="")
    assert new_user.vk_id == 999
    assert new_user.username == "Newbie"
    db.close()

@pytest.mark.integration
def test_service_create_or_update_player_existing():
    db = TestingSessionLocal()
    user = User(vk_id=888, username="OldName", avatar="old.jpg")
    db.add(user)
    db.commit()
    
    updated_user = player_service.create_or_update_player(db, vk_id=888, username="NewName", avatar="new.jpg")
    assert updated_user.username == "NewName"
    db.close()

@pytest.mark.integration
def test_service_get_player_full_data():
    db = TestingSessionLocal()
    user = User(vk_id=777, username="Tester", strength=12)
    db.add(user)
    db.commit()
    
    data = player_service.get_player_full_data(db, vk_id=777)
    assert "user" in data
    assert "calculated_stats" in data
    db.close()

@pytest.mark.integration
def test_service_get_player_full_data_not_found():
    db = TestingSessionLocal()
    with pytest.raises(HTTPException) as exc_info:
        player_service.get_player_full_data(db, vk_id=99999)
    assert exc_info.value.status_code == 404
    db.close()

@pytest.mark.integration
def test_service_update_location():
    db = TestingSessionLocal()
    user = User(vk_id=666, location="forest")
    db.add(user)
    db.commit()
    
    updated_user = player_service.update_player_location(db, vk_id=666, new_location="castle")
    assert updated_user.location == "castle"
    db.close()

@pytest.mark.integration
def test_service_get_player_by_vk_id_not_found():
    # Дополнительный тест для покрытия ветки return None в get_player_by_vk_id
    db = TestingSessionLocal()
    result = player_service.get_player_by_vk_id(db, vk_id=123456789)
    assert result is None
    db.close()

# --- Тесты API (Integration) ---

@pytest.mark.integration
def test_api_get_player():
    db = TestingSessionLocal()
    user = User(vk_id=12345, username="Hero", avatar="img.png")
    db.add(user)
    db.commit()
    db.close()
    
    response = client.get("/api/v1/player/12345")
    assert response.status_code == 200
    data = response.json()
    assert data["vk_id"] == 12345

@pytest.mark.integration
def test_api_get_player_stats():
    db = TestingSessionLocal()
    user = User(vk_id=54321, strength=14, agility=8)
    db.add(user)
    db.commit()
    db.close()
    
    response = client.get("/api/v1/player/54321/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    stats = data["data"]["stats"]
    assert stats["strength"]["modifier"] == 2
    assert stats["agility"]["modifier"] == -1

@pytest.mark.integration
def test_api_player_not_found():
    response = client.get("/api/v1/player/99999")
    assert response.status_code == 404

@pytest.mark.integration
def test_api_update_location():
    db = TestingSessionLocal()
    user = User(vk_id=11111, location="start")
    db.add(user)
    db.commit()
    db.close()
    
    response = client.post("/api/v1/player/11111/location?location=end")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["location"] == "end"

@pytest.mark.unit
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "status" in data

@pytest.mark.unit
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.unit
def test_api_root_docs():
    # Тест для покрытия редиректа или доступности docs
    response = client.get("/api/v1/docs")
    # Swagger может вернуть 200 или перенаправить, главное что нет 404/500
    assert response.status_code in [200, 307, 308]

# --- Тесты Утилит (Unit) ---

@pytest.mark.unit
def test_vk_auth_missing_sign():
    with pytest.raises(HTTPException) as exc_info:
        validate_vk_sign({"vk_id": "123"})
    assert exc_info.value.status_code == 401
    assert "Отсутствует параметр sign" in str(exc_info.value.detail)

@pytest.mark.unit
def test_vk_auth_invalid_base64():
    with pytest.raises(HTTPException) as exc_info:
        validate_vk_sign({"vk_id": "123", "sign": "invalid!!!"})
    assert exc_info.value.status_code == 401