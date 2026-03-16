-- ============================================
-- КОРОЛЕВСТВА ЭТЕРИИ - Схема базы данных
-- Версия: 1.0
-- PostgreSQL 14+
-- ============================================

-- ============================================
-- ТАБЛИЦА: users (Пользователи)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    vk_id INTEGER PRIMARY KEY,
    username VARCHAR(100) DEFAULT 'Игрок',
    avatar VARCHAR(255) DEFAULT '',
    character_class VARCHAR(50) DEFAULT 'warrior',
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    strength INTEGER DEFAULT 10,
    agility INTEGER DEFAULT 10,
    intelligence INTEGER DEFAULT 10,
    spirit INTEGER DEFAULT 10,
    vitality INTEGER DEFAULT 10,
    hp INTEGER DEFAULT 150,
    max_hp INTEGER DEFAULT 150,
    mana INTEGER DEFAULT 50,
    max_mana INTEGER DEFAULT 50,
    stamina INTEGER DEFAULT 150,
    max_stamina INTEGER DEFAULT 150,
    stamina_last_regen TIMESTAMP DEFAULT NOW(),
    fatigue_state VARCHAR(20) DEFAULT 'fit',
    fatigue_penalty JSONB DEFAULT '{}',
    stamina_warnings_sent JSONB DEFAULT '[]',
    gold INTEGER DEFAULT 0,
    location VARCHAR(50) DEFAULT 'village',
    story_context JSONB DEFAULT '[]',
    in_combat BOOLEAN DEFAULT FALSE,
    combat_opponent_id INTEGER,
    inventory_slots INTEGER DEFAULT 20,
    equipment JSONB DEFAULT '{}',
    active_buffs JSONB DEFAULT '[]',
    active_debuffs JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- ТАБЛИЦА: items (Предметы)
-- ============================================
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    item_type VARCHAR(50) NOT NULL,
    rarity VARCHAR(20) DEFAULT 'common',
    slot VARCHAR(50),
    stats JSONB DEFAULT '{}',
    min_level INTEGER DEFAULT 1,
    durability INTEGER DEFAULT 100,
    max_durability INTEGER DEFAULT 100,
    value INTEGER DEFAULT 0,
    buy_price INTEGER DEFAULT 0,
    effects JSONB DEFAULT '[]',
    soulbound BOOLEAN DEFAULT FALSE,
    tradeable BOOLEAN DEFAULT TRUE,
    icon VARCHAR(10) DEFAULT '📦',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- ТАБЛИЦА: user_items (Инвентарь пользователя)
-- ============================================
CREATE TABLE IF NOT EXISTS user_items (
    id SERIAL PRIMARY KEY,
    vk_id INTEGER REFERENCES users(vk_id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id),
    quantity INTEGER DEFAULT 1,
    equipped BOOLEAN DEFAULT FALSE,
    bonus_stats JSONB DEFAULT '{}',
    enchantment_level INTEGER DEFAULT 0,
    acquired_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- ТАБЛИЦА: combats (Боги)
-- ============================================
CREATE TABLE IF NOT EXISTS combats (
    id SERIAL PRIMARY KEY,
    player1_id INTEGER NOT NULL,
    player2_id INTEGER NOT NULL,
    player1_hp INTEGER DEFAULT 100,
    player2_hp INTEGER DEFAULT 100,
    turn INTEGER DEFAULT 1,
    log JSONB DEFAULT '[]',
    winner_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP
);

-- ============================================
-- ТАБЛИЦА: stamina_logs (История выносливости)
-- ============================================
CREATE TABLE IF NOT EXISTS stamina_logs (
    id SERIAL PRIMARY KEY,
    vk_id INTEGER REFERENCES users(vk_id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    stamina_change INTEGER NOT NULL,
    stamina_before INTEGER NOT NULL,
    stamina_after INTEGER NOT NULL,
    warning_triggered VARCHAR(10),
    location VARCHAR(50) DEFAULT 'unknown',
    timestamp TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- ИНДЕКСЫ
-- ============================================
CREATE INDEX IF NOT EXISTS idx_users_vk_id ON users(vk_id);
CREATE INDEX IF NOT EXISTS idx_users_location ON users(location);
CREATE INDEX IF NOT EXISTS idx_users_in_combat ON users(in_combat);
CREATE INDEX IF NOT EXISTS idx_users_level ON users(level);
CREATE INDEX IF NOT EXISTS idx_user_items_vk_id ON user_items(vk_id);
CREATE INDEX IF NOT EXISTS idx_user_items_item_id ON user_items(item_id);
CREATE INDEX IF NOT EXISTS idx_combats_active ON combats(is_active);
CREATE INDEX IF NOT EXISTS idx_combats_player1 ON combats(player1_id);
CREATE INDEX IF NOT EXISTS idx_combats_player2 ON combats(player2_id);
CREATE INDEX IF NOT EXISTS idx_stamina_logs_vk_id ON stamina_logs(vk_id);
CREATE INDEX IF NOT EXISTS idx_stamina_logs_timestamp ON stamina_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_items_type ON items(item_type);
CREATE INDEX IF NOT EXISTS idx_items_rarity ON items(rarity);

-- ============================================
-- НАЧАЛЬНЫЕ ДАННЫЕ: Базовые предметы
-- ============================================
INSERT INTO items (name, description, item_type, rarity, slot, stats, min_level, value, icon) VALUES
-- Оружие
('Ржавый меч', 'Старый меч новичка', 'weapon', 'common', 'main_hand', '{"damage": 5}', 1, 10, '⚔️'),
('Железный меч', 'Надёжное оружие воина', 'weapon', 'uncommon', 'main_hand', '{"damage": 10}', 3, 50, '⚔️'),
('Стальной меч', 'Острое оружие мастера', 'weapon', 'rare', 'main_hand', '{"damage": 20}', 7, 150, '⚔️'),
('Посох ученика', 'Простой магический посох', 'weapon', 'common', 'main_hand', '{"magic_damage": 8}', 1, 15, '🪄'),
('Лук охотника', 'Точный лук для дальних атак', 'weapon', 'uncommon', 'main_hand', '{"damage": 12, "crit": 5}', 3, 60, '🏹'),
-- Броня
('Тряпичная одежда', 'Базовая защита', 'armor', 'common', 'chest', '{"defense": 2}', 1, 5, '👕'),
('Кожаная броня', 'Лёгкая защита', 'armor', 'common', 'chest', '{"defense": 5}', 2, 25, '️'),
('Кольчуга', 'Средняя защита', 'armor', 'uncommon', 'chest', '{"defense": 10}', 5, 75, '🛡️'),
('Лавровый венок', 'Украшение для головы', 'accessory', 'common', 'head', '{"spirit": 1}', 1, 10, '👑'),
-- Расходники
('Зелье здоровья', 'Восстанавливает 30 HP', 'consumable', 'common', NULL, '{"heal": 30}', 1, 20, '🧪'),
('Зелье маны', 'Восстанавливает 20 маны', 'consumable', 'common', NULL, '{"mana": 20}', 1, 20, '🧪'),
('Зелье выносливости', 'Восстанавливает 25 выносливости', 'consumable', 'common', NULL, '{"stamina": 25}', 1, 15, '🧪'),
('Свиток телепортации', 'Возвращает в деревню', 'consumable', 'rare', NULL, '{"teleport": true}', 5, 100, '📜');

-- ============================================
-- ФУНКЦИЯ: Обновление last_login при входе
-- ============================================
CREATE OR REPLACE FUNCTION update_last_login()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_login = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- ТРИГГЕР: Автообновление last_login
-- ============================================
CREATE TRIGGER trigger_update_last_login
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_last_login();