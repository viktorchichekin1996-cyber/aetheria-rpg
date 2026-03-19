# backend/app/utils/vk_auth.py
import hashlib
import hmac
import urllib.parse
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.config import settings


def validate_vk_sign(query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Проверяет цифровую подпись данных от VK Mini Apps.
    Возвращает распарсенные данные пользователя, если подпись верна.
    """
    sign = query_params.get('sign')
    if not sign:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствует параметр sign"
        )

    # Убираем параметр sign из данных для хеширования
    data_to_check = {k: v for k, v in query_params.items() if k != 'sign'}
    
    # Сортируем ключи по алфавиту и формируем строку key=value
    sorted_params = sorted(data_to_check.items())
    data_string = "\n".join([f"{k}={v}" for k, v in sorted_params])
    
    # Вычисляем HMAC-SHA256 с использованием секретного ключа приложения
    secret_key = settings.VK_CLIENT_SECRET.encode('utf-8')
    expected_sign = hmac.new(secret_key, data_string.encode('utf-8'), hashlib.sha256).digest()
    
    # Декодируем полученный sign из base64 url-safe формата
    try:
        received_sign = urllib.parse.unquote(sign)
        # Преобразуем строку sign обратно в байты (она приходит в формате base64url)
        # VK использует стандартный base64 заменой символов, но часто приходит просто base64
        # Для надежности используем decode с заменой символов если нужно, но обычно работает так:
        import base64
        # Добавляем паддинг если нужно
        padding = 4 - len(received_sign) % 4
        if padding != 4:
            received_sign += '=' * padding
        received_sign_bytes = base64.urlsafe_b64decode(received_sign)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат подписи"
        )

    # Сравниваем подписи
    if not hmac.compare_digest(expected_sign, received_sign_bytes):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверная подпись VK"
        )

    # Если подпись верна, возвращаем данные (vk_id, first_name, etc.)
    return data_to_check