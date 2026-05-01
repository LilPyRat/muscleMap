from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import get_connection, init_db
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__, static_folder='../static', static_url_path='')
CORS(app)

# Инициализация БД при запуске
init_db()

@app.route('/')
def index():
    """Отдача frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/exercises', methods=['GET'])
def get_exercises():
    """Получение списка всех упражнений"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM exercises ORDER BY muscle_group, name')
    exercises = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Преобразуем Decimal в float для JSON
    for exercise in exercises:
        exercise['intensity_factor'] = float(exercise['intensity_factor'])
    
    return jsonify(exercises)

@app.route('/api/calculate', methods=['POST'])
def calculate_intensity():
    """Расчет нагрузки на мышцы"""
    data = request.json
    exercise_id = data.get('exercise_id')
    weight = float(data.get('weight', 0))
    reps = int(data.get('reps', 0))
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Получаем информацию об упражнении
    cursor.execute('SELECT * FROM exercises WHERE id = %s', (exercise_id,))
    exercise = cursor.fetchone()
    
    if not exercise:
        return jsonify({'error': 'Упражнение не найдено'}), 404
    
    # Расчет интенсивности
    # Интенсивность = вес * повторения * коэффициент упражнения / 100
    intensity = (weight * reps * exercise['intensity_factor']) / 100
    
    # Определяем уровень интенсивности
    if intensity < 30:
        level = "Низкая"
    elif intensity < 60:
        level = "Средняя"
    elif intensity < 90:
        level = "Высокая"
    else:
        level = "Очень высокая"
    
    result = {
        'muscle_group': exercise['muscle_group'],
        'exercise_name': exercise['name'],
        'intensity': round(intensity, 2),
        'level': level,
        'weight': weight,
        'reps': reps
    }

    cursor.close()
    conn.close()
    
    return jsonify(result)

@app.route('/api/workout', methods=['POST'])
def save_workout():
    """Сохранение записи тренировки"""
    data = request.json
    entries = data.get('entries', [])
    
    if not entries:
        return jsonify({'error': 'Нет данных для сохранения'}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        for entry in entries:
            cursor.execute(
                'INSERT INTO workout_entries (exercise_id, weight, reps) VALUES (%s, %s, %s)',
                (entry['exercise_id'], float(entry['weight']), int(entry['reps']))
            )
        
        conn.commit()
        return jsonify({'message': 'Тренировка сохранена'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/workout/history', methods=['GET'])
def get_workout_history():
    """Получение истории тренировок"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('''
        SELECT w.*, e.name as exercise_name, e.muscle_group 
        FROM workout_entries w
        JOIN exercises e ON w.exercise_id = e.id
        ORDER BY w.created_at DESC
        LIMIT 50
    ''')
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Преобразуем datetime в строку
    for entry in history:
        entry['created_at'] = entry['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True, port=5000)