// Глобальные переменные
let currentExercises = [];
let allExercises = [];

// API URL
const API_URL = 'http://localhost:5000/api';

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    loadExercises();
    setupEventListeners();
});

// Загрузка списка упражнений
async function loadExercises() {
    try {
        const response = await fetch(`${API_URL}/exercises`);
        allExercises = await response.json();
        
        const select = document.getElementById('exercise-select');
        select.innerHTML = '<option value="">Выберите упражнение</option>';
        
        // Группируем по мышечным группам
        const grouped = {};
        allExercises.forEach(ex => {
            if (!grouped[ex.muscle_group]) {
                grouped[ex.muscle_group] = [];
            }
            grouped[ex.muscle_group].push(ex);
        });
        
        // Добавляем опции в select
        for (const [group, exercises] of Object.entries(grouped)) {
            const optgroup = document.createElement('optgroup');
            optgroup.label = group;
            
            exercises.forEach(ex => {
                const option = document.createElement('option');
                option.value = ex.id;
                option.textContent = ex.name;
                optgroup.appendChild(option);
            });
            
            select.appendChild(optgroup);
        }
    } catch (error) {
        console.error('Ошибка загрузки упражнений:', error);
        alert('Не удалось загрузить упражнения. Убедитесь, что сервер запущен.');
    }
}

// Настройка обработчиков событий
function setupEventListeners() {
    document.getElementById('add-exercise-btn').addEventListener('click', addExercise);
    document.getElementById('calculate-btn').addEventListener('click', calculateIntensity);
    document.getElementById('save-btn').addEventListener('click', saveWorkout);
    document.getElementById('clear-btn').addEventListener('click', clearCurrentWorkout);
    document.getElementById('load-history-btn').addEventListener('click', loadHistory);
}

// Добавление упражнения
function addExercise() {
    const exerciseId = document.getElementById('exercise-select').value;
    const weight = document.getElementById('weight-input').value;
    const reps = document.getElementById('reps-input').value;
    
    if (!exerciseId || !weight || !reps) {
        alert('Пожалуйста, заполните все поля');
        return;
    }
    
    const exercise = allExercises.find(ex => ex.id == exerciseId);
    
    currentExercises.push({
        exercise_id: parseInt(exerciseId),
        exercise_name: exercise.name,
        muscle_group: exercise.muscle_group,
        weight: parseFloat(weight),
        reps: parseInt(reps)
    });
    
    updateExercisesList();
    
    // Очистка полей ввода
    document.getElementById('exercise-select').value = '';
    document.getElementById('weight-input').value = '';
    document.getElementById('reps-input').value = '';
}

// Обновление списка текущих упражнений
function updateExercisesList() {
    const list = document.getElementById('exercises-list');
    const card = document.getElementById('current-workout-card');
    
    if (currentExercises.length === 0) {
        card.style.display = 'none';
        return;
    }
    
    card.style.display = 'block';
    list.innerHTML = currentExercises.map((ex, index) => `
        <div class="exercise-item">
            <div class="exercise-info">
                <div class="exercise-name">${ex.exercise_name}</div>
                <div class="exercise-details">${ex.muscle_group} | ${ex.weight} кг × ${ex.reps} повт.</div>
            </div>
            <button class="remove-btn" onclick="removeExercise(${index})">Удалить</button>
        </div>
    `).join('');
}

// Удаление упражнения из списка
function removeExercise(index) {
    currentExercises.splice(index, 1);
    updateExercisesList();
}

// Расчет интенсивности
async function calculateIntensity() {
    if (currentExercises.length === 0) {
        alert('Добавьте хотя бы одно упражнение');
        return;
    }
    
    const resultsCard = document.getElementById('results-card');
    const resultsList = document.getElementById('results-list');
    
    resultsList.innerHTML = '<div class="empty-state">Расчет...</div>';
    resultsCard.style.display = 'block';
    
    try {
        const results = [];
        
        for (const entry of currentExercises) {
            const response = await fetch(`${API_URL}/calculate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    exercise_id: entry.exercise_id,
                    weight: entry.weight,
                    reps: entry.reps
                })
            });
            
            const result = await response.json();
            results.push(result);
        }
        
        // Отображение результатов
        resultsList.innerHTML = results.map(r => `
            <div class="result-item">
                <div class="result-muscle">${r.muscle_group}</div>
                <div>${r.exercise_name}</div>
                <div class="result-intensity">
                    <div class="intensity-value">${r.intensity}</div>
                    <div class="intensity-level">${r.level}</div>
                </div>
                <div style="margin-top: 10px; font-size: 0.9em;">
                    ${r.weight} кг × ${r.reps} повт.
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Ошибка расчета:', error);
        resultsList.innerHTML = '<div class="empty-state">Ошибка расчета</div>';
    }
}

// Сохранение тренировки
async function saveWorkout() {
    if (currentExercises.length === 0) {
        alert('Нет упражнений для сохранения');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/workout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                entries: currentExercises
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Тренировка сохранена!');
            clearCurrentWorkout();
        } else {
            alert('Ошибка сохранения: ' + result.error);
        }
    } catch (error) {
        console.error('Ошибка сохранения:', error);
        alert('Не удалось сохранить тренировку');
    }
}

// Очистка текущей тренировки
function clearCurrentWorkout() {
    currentExercises = [];
    updateExercisesList();
    document.getElementById('results-card').style.display = 'none';
}

// Загрузка истории тренировок
async function loadHistory() {
    const historyList = document.getElementById('history-list');
    historyList.innerHTML = '<div class="empty-state">Загрузка...</div>';
    
    try {
        const response = await fetch(`${API_URL}/workout/history`);
        const history = await response.json();
        
        if (history.length === 0) {
            historyList.innerHTML = '<div class="empty-state">История пуста</div>';
            return;
        }
        
        historyList.innerHTML = history.map(h => `
            <div class="history-item">
                <strong>${h.exercise_name}</strong> (${h.muscle_group})<br>
                ${h.weight} кг × ${h.reps} повт.
                <div class="history-date">${h.created_at}</div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Ошибка загрузки истории:', error);
        historyList.innerHTML = '<div class="empty-state">Ошибка загрузки</div>';
    }
}
