# 🏰 Королевства Этерии (Aetheria RPG)

Текстовая RPG игра для VK Mini Apps с AI-повествованием и PvP боями.

## 📋 Описание

**Королевства Этерии** — это многопользовательская текстовая ролевая игра в мире классического фэнтези. Исследуйте локации, сражайтесь с монстрами и другими игроками, развивайте своего персонажа.

### Особенности:
- 🤖 AI-генерация повествования (Inference API)
- ⚔️ Пошаговая боевая система d20
- 🛡️ 11 уникальных классов
- 🌍 5 локаций с разным уровнем сложности
- ⚡ Система выносливости
- 🎒 Инвентарь и экипировка
- ⚔️ PvP бои с матчмейкингом

## 🚀 Быстрый старт

### Требования
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000