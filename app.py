from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import os
import json
import time
import sys
import requests

# ════════════════════════════════════════════════════════════════════════════════
# ИМПОРТЫ ИЗ ПЕРВОЙ ЧАСТИ
# ════════════════════════════════════════════════════════════════════════════════

from utils.text_generator import (
    generate_profession_card,
    generate_clarifying_questions,
    check_profession_exists_simple
)

from utils.image_generator import generate_moodboard_composite

# ИМПОРТЫ ВТОРОЙ ЧАСТИ - MUSIC INTEGRATION
from utils.lastfm_music_integration import get_profession_playlist as get_lastfm_playlist

try:
    from utils.hh_api import get_vacancy_stats_multi_source
except ImportError:
    def get_vacancy_stats_multi_source(profession, area=113):
        return {
            "total": "Н/Д",
            "avg_salary": None,
            "avg_salary_formatted": "Не доступно",
            "competition": "Данные недоступны",
            "competition_level": "unknown",
            "top_vacancies": [],
            "perspective": "Статистика временно недоступна",
            "source": "Fallback"
        }

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

generated_cards = {}

# ════════════════════════════════════════════════════════════════════════════════
# ВТОРАЯ ЧАСТЬ - ПРОФЕССИИ И ИХ МУЗЫКА + АУДИО (со second части + расширения)
# ════════════════════════════════════════════════════════════════════════════════

PROFESSION_MUSIC = {
    "программист": {
        "genre": "Электроника",
        "mood": "Концентрация",
        "description": "Электроника для фокуса и творчества",
        "artists": ["Daft Punk", "Avicii", "Martin Garrix", "Deadmau5", "Skrillex"]
    },
    "frontend-разработчик": {
        "genre": "Синтвейв",
        "mood": "Вдохновение",
        "description": "Синтвейв для креативного процесса",
        "artists": ["Perturbator", "M83", "Kavinsky", "Lazerhawk", "Le Knight Club"]
    },
    "backend-разработчик": {
        "genre": "Прогрессив-метал",
        "mood": "Энергия",
        "description": "Мощная музыка для сложных задач",
        "artists": ["Dream Theater", "Tool", "Meshuggah", "Between the Buried and Me", "Opeth"]
    },
    "data scientist": {
        "genre": "Lo-fi Hip Hop",
        "mood": "Анализ",
        "description": "Lo-fi для долгих часов анализа данных",
        "artists": ["Nujabes", "Uyama Hiroto", "J Dilla", "Qveen", "Apollo XO"]
    },
    "повар": {
        "genre": "Джаз",
        "mood": "Творчество",
        "description": "Джаз - музыка для творческого процесса готовки",
        "artists": ["Miles Davis", "Dave Brubeck", "John Coltrane", "Bill Evans", "Thelonious Monk"]
    },
    "пожарный": {
        "genre": "Рок",
        "mood": "Мужество",
        "description": "Мощный рок для смелого сердца",
        "artists": ["Queen", "Led Zeppelin", "AC/DC", "The Who", "Deep Purple"]
    },
    "художник": {
        "genre": "Амбиент",
        "mood": "Вдохновение",
        "description": "Атмосферная музыка для творчества",
        "artists": ["Brian Eno", "Ólafur Arnalds", "Nils Frahm", "Tycho", "Bonobo"]
    },
    "менеджер": {
        "genre": "Поп",
        "mood": "Энергия",
        "description": "Позитивная музыка для мотивации команды",
        "artists": ["The Chainsmokers", "Kygo", "Calvin Harris", "Zayn", "Imogen Heap"]
    },
    "дизайнер": {
        "genre": "Инди",
        "mood": "Вдохновение",
        "description": "Инди-рок для креативных процессов",
        "artists": ["Tame Impala", "Arcade Fire", "Phoenix", "The Strokes", "MGMT"]
    },
    "маркетолог": {
        "genre": "Хип-хоп",
        "mood": "Вдохновение",
        "description": "Хип-хоп для инновативного мышления",
        "artists": ["Kendrick Lamar", "J. Cole", "Nas", "The Roots", "MF DOOM"]
    },
}

PROFESSION_AUDIO_MAPPING = {
    "программист": "Algorithm.mp3",
    "frontend-разработчик": "Algorithm.mp3",
    "backend-разработчик": "Algorithm.mp3",
    "data scientist": "Algorithm.mp3",
    "повар": "Culinary.mp3",
    "шеф-повар": "Culinary.mp3",
    "кондитер": "Culinary.mp3",
    "пожарный": "Police.mp3",
    "полицейский": "Police.mp3",
    "охранник": "Police.mp3",
    "художник": "Culture.mp3",
    "музыкант": "Culture.mp3",
    "актёр": "Culture.mp3",
    "дизайнер": "Culture.mp3",
    "менеджер": "Management.mp3",
    "маркетолог": "Marketing.mp3",
    "политик": "Politic.mp3",
    "дипломат": "Politic.mp3",
    "пресс-секретарь": "Politic.mp3",
}

def get_audio_file_for_profession(profession):
    """Получить MP3 файл для профессии (вторая часть)"""
    profession_lower = profession.lower().strip()
    
    if profession_lower in PROFESSION_AUDIO_MAPPING:
        return PROFESSION_AUDIO_MAPPING[profession_lower]
    
    for key, audio_file in PROFESSION_AUDIO_MAPPING.items():
        if key in profession_lower or profession_lower in key:
            return audio_file
    
    return None

def get_music_for_profession(profession):
    """Получить конфиг музыки для профессии"""
    profession_lower = profession.lower().strip()
    
    for key, config in PROFESSION_MUSIC.items():
        if key in profession_lower or profession_lower in key:
            return config
    
    return None

# ════════════════════════════════════════════════════════════════════════════════
# ПЕРВАЯ ЧАСТЬ - ОСНОВНЫЕ МАРШРУТЫ
# ════════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/check-profession', methods=['POST'])
def check_profession():
    """ПРОВЕРЯЕТ СУЩЕСТВОВАНИЕ ПРОФЕССИИ НА HH.RU"""
    data = request.json
    profession = data.get('profession', '').strip()

    if not profession:
        return jsonify({
            'success': False,
            'error': 'Пожалуйста, введите название профессии'
        }), 400

    if len(profession) < 2:
        return jsonify({
            'success': False,
            'error': 'Название профессии слишком короткое'
        }), 400

    session['profession'] = profession

    print(f"\n📋 Проверка профессии: {profession}")
    exists = check_profession_exists_simple(profession)

    if not exists:
        return jsonify({
            'success': False,
            'error': f'Профессия "{profession}" не найдена на HH.ru'
        }), 404

    print(f"✅ Профессия найдена на HH.ru")
    return jsonify({
        'success': True,
        'profession': profession,
        'message': f'✅ Профессия "{profession}" найдена на HH.ru!'
    })

@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    """ГЕНЕРИРУЕТ ВОПРОСЫ ПОСЛЕ НАЖАТИЯ "ДАЛЕЕ" """
    data = request.json
    profession = session.get('profession') or data.get('profession')

    if not profession:
        return jsonify({
            'success': False,
            'error': 'Профессия не указана'
        }), 400

    print(f"\n📝 Генерация вопросов для: {profession}")

    try:
        questions_data = generate_clarifying_questions(profession)
        return jsonify({
            'success': True,
            'profession': profession,
            'questions': questions_data if questions_data else []
        })

    except Exception as e:
        print(f"❌ Ошибка генерации вопросов: {e}")
        return jsonify({
            'success': True,
            'profession': profession,
            'questions': [
                {
                    "question": f"Какой опыт в {profession}?",
                    "field": "experience",
                    "options": ["Новичок", "Опыт есть", "Профессионал"]
                },
                {
                    "question": f"Размер компании для {profession}?",
                    "field": "company_size",
                    "options": ["Маленькая", "Средняя", "Большая"]
                },
                {
                    "question": f"Что важно для {profession}?",
                    "field": "priority",
                    "options": ["Зарплата", "Интерес", "Комфорт"]
                }
            ]
        })

@app.route('/api/generate', methods=['POST'])
def generate_card():
    """ПОЛНАЯ ГЕНЕРАЦИЯ КАРТОЧКИ С МУЗЫКОЙ"""
    data = request.json
    profession = session.get('profession') or data.get('profession')
    answers = data.get('answers', {})

    if not profession:
        return jsonify({
            'success': False,
            'error': 'Профессия не указана'
        }), 400

    try:
        print(f"\n🚀 Начинаем генерацию для профессии: {profession}")
        print(f"📝 Ответы пользователя: {answers}")

        # 1. ПРОВЕРКА СУЩЕСТВОВАНИЯ ПРОФЕССИИ
        print("\n1️⃣ Проверка существования профессии...")
        exists = check_profession_exists_simple(profession)

        if not exists:
            return jsonify({
                'success': False,
                'error': f'Профессия "{profession}" не найдена'
            }), 404

        print(f"✅ Профессия найдена")

        # 2. ГЕНЕРАЦИЯ ТЕКСТОВОГО КОНТЕНТА ЧЕРЕЗ YANDEX GPT
        print("\n2️⃣ Генерация текстового контента...")
        card_data = generate_profession_card(profession, answers)

        if not card_data or 'error' in card_data:
            return jsonify({
                'success': False,
                'error': card_data.get('message', 'Не удалось сгенерировать карточку профессии')
            }), 500

        print(f"✅ Контент сгенерирован успешно")

        # 3. ПОЛУЧЕНИЕ СТАТИСТИКИ ВАКАНСИЙ
        print("\n3️⃣ Получение статистики вакансий...")
        vacancy_stats = get_vacancy_stats_multi_source(profession, area=113)

        if not vacancy_stats:
            print("⚠️ Статистика не найдена, используем fallback")
            vacancy_stats = {
                "total": "Н/Д",
                "avg_salary": None,
                "avg_salary_formatted": "Н/Д",
                "competition": "Данные недоступны",
                "competition_level": "unknown",
                "top_vacancies": [],
                "perspective": "Статистика временно недоступна",
                "source": "Fallback"
            }

        print(f"✅ Статистика получена")

        # 4. ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЯ (МУДБОРД)
        print("\n4️⃣ Генерирую мудборд (изображение)...")
        sd_prompts = card_data.get('sd_prompts', [])
        image_url = None

        if sd_prompts:
            image_url = generate_moodboard_composite(
                sd_prompts=sd_prompts,
                profession=profession
            )

        if image_url:
            print(f"✅ Мудборд сгенерирован: {image_url}")
        else:
            print("⚠️ Не удалось сгенерировать изображение, используем placeholder")
            profession_slug = profession.lower().replace(' ', '_').replace('-', '_')
            image_url = f"/static/images/placeholder_{profession_slug}.png"

        # 5. AUDIO ВАЙБ (вторая часть)
        print("\n5️⃣ Получаю аудио вайб...")
        audio_file = get_audio_file_for_profession(profession)
        audio_url = f"/static/audio/{audio_file}" if audio_file else None

        # 6. ПЛЕЙЛИСТ Last.fm (5 ПЕСЕН + ИНФОРМАЦИЯ АРТИСТОВ) - ВТОРАЯ ЧАСТЬ
        print("\n6️⃣ Генерирую плейлист Last.fm (5 песен + информация)...")
        music_playlist = None

        try:
            music_playlist = get_lastfm_playlist(profession)
            
            if music_playlist:
                print(f"\n✅ ПЛЕЙЛИСТ ИЗ Last.fm:")
                print(f" Профессия: {music_playlist['profession']}")
                print(f" Жанр: {music_playlist['genre']}")
                print(f" Песен: {len(music_playlist['tracks'])}")
                
                for i, track in enumerate(music_playlist['tracks'], 1):
                    print(f"\n {i}. {track['name']}")
                    print(f" Артист: {track['artist']}")
                    if track['artist_info']:
                        print(f" 👥 Слушателей: {track['artist_info'].get('listeners', 'N/A')}")
            else:
                print("⚠️ Не удалось получить плейлист")

        except Exception as e:
            print(f"⚠️ Ошибка Last.fm: {e}")
            import traceback
            traceback.print_exc()

        # 7. РАСЧЁТ ПОДХОДЯЩЕСТИ
        print("\n7️⃣ Расчёт подходящести профессии...")
        suitability_score = calculate_suitability_score(profession, answers, vacancy_stats)
        print(f"✅ Подходящесть: {suitability_score}/10")

        # 8. ФОРМИРУЕМ ПОЛНЫЙ РЕЗУЛЬТАТ
        print("\n8️⃣ Формирование результата...")
        result = {
            'success': True,
            'profession': profession,
            'daily_schedule': card_data.get('daily_schedule', []),
            'tech_stack': card_data.get('tech_stack', []),
            'benefits': card_data.get('benefits', ''),
            'company_value': card_data.get('company_value', ''),
            'career_path': card_data.get('career_path', ''),
            'chat_examples': card_data.get('chat_examples', []),
            'image_url': image_url,
            'vacancy_stats': vacancy_stats,
            'audio_url': audio_url,
            'music_playlist': music_playlist,  # ВТОРАЯ ЧАСТЬ - плейлист Last.fm
            'suitability_score': suitability_score
        }

        # 9. СОХРАНЯЕМ РЕЗУЛЬТАТ ДЛЯ ИСТОРИИ
        profession_slug = profession.lower().replace(' ', '_').replace('-', '_')
        card_id = f"{profession_slug}_{len(generated_cards)}_{int(time.time())}"

        generated_cards[card_id] = result
        result['card_id'] = card_id

        print(f"✅ Результат готов! ID: {card_id}")
        print("🎉 Генерация завершена успешно!\n")

        return jsonify(result)

    except Exception as e:
        print(f"\n❌ ОШИБКА при генерации: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': f'Произошла ошибка при генерации: {str(e)}'
        }), 500

@app.route('/result/<card_id>')
def show_result(card_id):
    """Отображение сгенерированной карточки профессии"""
    print(f"📍 Запрос карточки: {card_id}")
    print(f"📊 Доступные карточки: {list(generated_cards.keys())}")
    
    card = generated_cards.get(card_id)
    
    if not card:
        print(f"❌ Карточка '{card_id}' не найдена")
        return render_template('error.html', 
                             error="Карточка не найдена",
                             message=f"ID: '{card_id}'"), 404
    
    print(f"✅ Карточка найдена!")
    return render_template('result.html', card=card)

@app.route('/api/health')
def health_check():
    """Проверка статуса всех сервисов"""
    ollama_status = "unknown"
    try:
        import ollama
        models = ollama.list()
        if models.get('models'):
            ollama_status = "running"
        else:
            ollama_status = "no_models"
    except:
        ollama_status = "not_running"

    sd_status = "unknown"
    try:
        response = requests.get("http://127.0.0.1:7860/config", timeout=10)
        if response.status_code == 200 or response.status_code == 401:
            sd_status = "running"
        else:
            sd_status = "error"
    except:
        sd_status = "not_installed"

    return jsonify({
        'status': 'ok',
        'ollama': ollama_status,
        'sd_webui': sd_status,
        'timestamp': time.time()
    })

@app.route('/demo/')
def demo_profession(profession_type):
    """Демо маршруты для различных профессий"""
    demos = {
        'devops': 'DevOps инженер',
        'cook': 'Повар-кондитер',
        'designer': 'UX/UI дизайнер',
        'python': 'Python разработчик',
        'frontend': 'Frontend разработчик',
        'manager': 'Менеджер проектов'
    }

    profession = demos.get(profession_type)

    if profession:
        session['profession'] = profession
        return render_template('index.html', demo_profession=profession)
    else:
        return "Демо не найдено", 404

def calculate_suitability_score(profession, answers, vacancy_stats):
    """Рассчитывает подходящесть профессии от 0 до 10"""
    score = 0

    # 1. ОПЫТ (0-2 балла)
    experience = answers.get('experience', '').lower()
    if 'junior' in experience or 'новичок' in experience:
        score += 1
    elif 'middle' in experience or 'опыт' in experience:
        score += 1.5
    elif 'senior' in experience or 'профессионал' in experience:
        score += 2
    else:
        score += 1

    # 2. ЗАРПЛАТА (0-3 балла)
    salary_importance = answers.get('priority', '').lower()
    avg_salary = vacancy_stats.get('avg_salary')

    if 'зарплата' in salary_importance or 'деньги' in salary_importance:
        if avg_salary and avg_salary > 150000:
            score += 3
        elif avg_salary and avg_salary > 100000:
            score += 2.5
        elif avg_salary and avg_salary > 50000:
            score += 2
        else:
            score += 1
    else:
        if avg_salary and avg_salary > 150000:
            score += 2
        elif avg_salary and avg_salary > 100000:
            score += 1.5
        else:
            score += 1

    # 3. КОНКУРЕНЦИЯ / СПРОС (0-3 балла)
    competition_level = vacancy_stats.get('competition_level', 'unknown')
    total_vacancies = vacancy_stats.get('total', 0)

    if competition_level == 'very_high' or total_vacancies > 3000:
        score += 3
    elif competition_level == 'high' or total_vacancies > 1500:
        score += 2.5
    elif competition_level == 'medium' or total_vacancies > 500:
        score += 2.2
    elif competition_level == 'moderate' or total_vacancies > 100:
        score += 1.8
    elif competition_level == 'low' or total_vacancies > 20:
        score += 1.3
    else:
        score += 0.5

    # 4. СООТВЕТСТВИЕ ПРЕДПОЧТЕНИЯМ (0-2 балла)
    company_type = answers.get('company_type', '').lower()
    priority = answers.get('priority', '').lower()

    if company_type or priority:
        score += 1.5
    else:
        score += 0.5

    max_possible = 2 + 3 + 3 + 2
    normalized_score = min(10, (score / max_possible) * 10)

    return round(normalized_score, 1)

if __name__ == '__main__':
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('static/audio', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

    if not os.path.exists('.env'):
        print("⚠️ ВНИМАНИЕ: Файл .env не найден!")
        print("📝 Создайте файл .env и добавьте необходимые переменные")

    print("\n🔍 Проверка Ollama...")
    try:
        import ollama
        models = ollama.list()
        print("✅ Ollama запущен и работает")
    except Exception as e:
        print(f"❌ Ollama не запущен!")
        print(f" Запустите: ollama serve")

    print("\n" + "="*60)
    print("🚀 ЗАПУСК CAREER VIBE GENERATOR")
    print("="*60)
    print("📍 Откройте браузер: http://localhost:5000")
    print("🎵 Интеграция Last.fm АКТИВНА")
    print("🎶 5 ПЕСЕН + ИНФОРМАЦИЯ АРТИСТОВ")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
