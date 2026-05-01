import psycopg2
from psycopg2.extras import RealDictCursor

# Конфигурация подключения к PostgreSQL
DB_CONFIG = {
    'dbname': 'gym_tracker',
    'user': 'postgres',
    'password': 'pass1234',
    'host': 'localhost',
    'port': '5432'
}

def get_connection():
    """Получение соединения с базой данных"""
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Инициализация базы данных и создание таблиц"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Таблица упражнений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            muscle_group VARCHAR(50) NOT NULL,
            intensity_factor FLOAT NOT NULL DEFAULT 1.0
        )
    ''')
    
    # Таблица записей тренировок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_entries (
            id SERIAL PRIMARY KEY,
            exercise_id INTEGER REFERENCES exercises(id),
            weight FLOAT NOT NULL,
            reps INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Добавляем базовые упражнения если таблица пуста
    cursor.execute('SELECT COUNT(*) FROM exercises')
    count = cursor.fetchone()[0]
    
    if count == 0:
        base_exercises = [
            ('Жим штанги лежа', 'Грудь', 1.0),
            ('Жим гантелей на наклонной скамье', 'Грудь', 0.9),
            ('Разведение гантелей', 'Грудь', 0.7),
            ('Приседания со штангой', 'Ноги', 1.2),
            ('Жим ногами', 'Ноги', 1.0),
            ('Выпады', 'Ноги', 0.8),
            ('Становая тяга', 'Спина', 1.3),
            ('Подтягивания', 'Спина', 1.0),
            ('Тяга штанги в наклоне', 'Спина', 0.95),
            ('Армейский жим', 'Плечи', 0.9),
            ('Махи гантелями в стороны', 'Плечи', 0.6),
            ('Жим на плечи в тренажере', 'Плечи', 0.85),
            ('Подъем штанги на бицепс', 'Бицепс', 0.7),
            ('Молотки', 'Бицепс', 0.65),
            ('Французский жим', 'Трицепс', 0.75),
            ('Отжимания на брусьях', 'Трицепс', 0.9),
            ('Скручивания', 'Пресс', 0.5),
            ('Планка', 'Пресс', 0.6)
        ]
        
        for exercise in base_exercises:
            cursor.execute(
                'INSERT INTO exercises (name, muscle_group, intensity_factor) VALUES (%s, %s, %s)',
                exercise
            )
    
    conn.commit()
    cursor.close()
    conn.close()
