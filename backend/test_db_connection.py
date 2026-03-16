"""
Тест подключения к PostgreSQL и Redis
Запуск: python test_db_connection.py
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import redis
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.config import settings
from app.models.users import User
from app.models.items import Item
from app.models.combats import Combat
from app.models.stamina_logs import StaminaLog


def test_postgresql():
    """Тест подключения к PostgreSQL"""
    print("=" * 50)
    print("ТЕСТ POSTGRESQL")
    print("=" * 50)
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        result = db.execute(text("SELECT version();"))
        pg_version = result.fetchone()[0]
        print(f"✅ PostgreSQL подключён")
        print(f"   Версия: {pg_version[:60]}...")
        
        tables = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)).fetchall()
        
        print(f"\n✅ Найдено таблиц: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        required_tables = ['users', 'items', 'user_items', 'combats', 'stamina_logs']
        existing_tables = [t[0] for t in tables]
        
        print(f"\n✅ Проверка обязательных таблиц:")
        for req_table in required_tables:
            if req_table in existing_tables:
                print(f"   ✅ {req_table}")
            else:
                print(f"   ❌ {req_table} (ОТСУТСТВУЕТ)")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL ошибка: {e}")
        return False


def test_redis():
    """Тест подключения к Redis"""
    print("\n" + "=" * 50)
    print("ТЕСТ REDIS")
    print("=" * 50)
    
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        
        ping_result = r.ping()
        print(f"✅ Redis подключён (PING: {ping_result})")
        
        r.set('test_connection_key', 'test_value')
        value = r.get('test_connection_key')
        print(f"✅ Запись/Чтение: {value}")
        
        r.delete('test_connection_key')
        
        info = r.info('server')
        print(f"   Версия Redis: {info['redis_version']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis ошибка: {e}")
        return False


def test_models():
    """Тест импорта моделей"""
    print("\n" + "=" * 50)
    print("ТЕСТ МОДЕЛЕЙ")
    print("=" * 50)
    
    try:
        from app.models.users import User
        from app.models.items import Item, UserItem
        from app.models.combats import Combat
        from app.models.stamina_logs import StaminaLog
        
        print("✅ User модель импортирована")
        print("✅ Item модель импортирована")
        print("✅ UserItem модель импортирована")
        print("✅ Combat модель импортирована")
        print("✅ StaminaLog модель импортирована")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта моделей: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 ЗАПУСК ТЕСТОВ БАЗЫ ДАННЫХ\n")
    
    pg_ok = test_postgresql()
    redis_ok = test_redis()
    models_ok = test_models()
    
    print("\n" + "=" * 50)
    print("ИТОГОВЫЙ СТАТУС")
    print("=" * 50)
    
    if pg_ok and redis_ok and models_ok:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("   - PostgreSQL: OK")
        print("   - Redis: OK")
        print("   - Модели: OK")
        sys.exit(0)
    else:
        print("❌ ЕСТЬ ОШИБКИ!")
        if not pg_ok:
            print("   - PostgreSQL: FAIL")
        if not redis_ok:
            print("   - Redis: FAIL")
        if not models_ok:
            print("   - Модели: FAIL")
        sys.exit(1)