import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Last.fm API ключ
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY", "2cfda79e10f38f888f3b093f3359f226")
LASTFM_BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# ════════════════════════════════════════════════════════════════════════════════
# ПРОФЕССИИ И ИХ МУЗЫКАЛЬНЫЕ ПРЕДПОЧТЕНИЯ (ТЕГИ)
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
    "devops": {
        "genre": "Электроника",
        "mood": "Концентрация",
        "description": "Электроника для системного администрирования",
        "artists": ["Daft Punk", "Deadmau5", "Skrillex", "Knife Party", "Pendulum"]
    },
    "шеф-повар": {
        "genre": "Джаз",
        "mood": "Творчество",
        "description": "Джаз для кулинарного мастерства",
        "artists": ["Miles Davis", "Dave Brubeck", "Herbie Hancock", "Bill Evans", "Thelonious Monk"]
    },
    "ui/ux дизайнер": {
        "genre": "Инди",
        "mood": "Вдохновение",
        "description": "Инди для дизайнерского вдохновения",
        "artists": ["Tame Impala", "Arcade Fire", "Phoenix", "The National", "MGMT"]
    },
}

# ════════════════════════════════════════════════════════════════════════════════
# ФУНКЦИЯ 1: ПОЛУЧИТЬ ИНФОРМАЦИЮ ОБ АРТИСТЕ
# ════════════════════════════════════════════════════════════════════════════════

def get_artist_info(artist_name):
    """
    Получить информацию об артисте из Last.fm
    
    Returns:
        {\"name\": str, \"bio\": str, \"listeners\": str, \"playcount\": str, \"image\": str, \"url\": str}
    """
    try:
        params = {
            "method": "artist.getinfo",
            "artist": artist_name,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        }

        response = requests.get(LASTFM_BASE_URL, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if "artist" in data:
                artist = data["artist"]
                
                # Получаем краткое описание (первые 200 символов)
                bio_text = ""
                if "bio" in artist and "summary" in artist["bio"]:
                    bio_text = artist["bio"]["summary"].split("<")[0].strip()
                    if len(bio_text) > 150:
                        bio_text = bio_text[:150] + "..."

                return {
                    "name": artist.get("name", artist_name),
                    "bio": bio_text,
                    "listeners": artist.get("stats", {}).get("listeners", "0"),
                    "playcount": artist.get("stats", {}).get("playcount", "0"),
                    "image": artist.get("image", [{}])[-1].get("#text", "") if artist.get("image") else "",
                    "url": artist.get("url", "")
                }

        return None

    except Exception as e:
        print(f"❌ Ошибка Last.fm Artist Info: {e}")
        return None

# ════════════════════════════════════════════════════════════════════════════════
# ФУНКЦИЯ 2: ПОЛУЧИТЬ ТОП ТРЕКИ АРТИСТА
# ════════════════════════════════════════════════════════════════════════════════

def get_artist_top_tracks(artist_name, limit=1):
    """
    Получить топ треки артиста из Last.fm
    
    Returns:
        [{\"name\": str, \"url\": str, \"listeners\": str, \"playcount\": str}]
    """
    try:
        params = {
            "method": "artist.gettoptracks",
            "artist": artist_name,
            "api_key": LASTFM_API_KEY,
            "format": "json",
            "limit": limit
        }

        response = requests.get(LASTFM_BASE_URL, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if "toptracks" in data and "track" in data["toptracks"]:
                tracks = data["toptracks"]["track"]
                
                if not isinstance(tracks, list):
                    tracks = [tracks]

                result_tracks = []
                for track in tracks[:limit]:
                    result_tracks.append({
                        "name": track.get("name", ""),
                        "artist": track.get("artist", {}).get("name", artist_name),
                        "url": track.get("url", ""),
                        "listeners": track.get("listeners", "0"),
                        "playcount": track.get("playcount", "0")
                    })

                return result_tracks

        return []

    except Exception as e:
        print(f"❌ Ошибка Last.fm Tracks: {e}")
        return []

# ════════════════════════════════════════════════════════════════════════════════
# ФУНКЦИЯ 3: ПОЛУЧИТЬ ПЛЕЙЛИСТ ДЛЯ ПРОФЕССИИ
# ════════════════════════════════════════════════════════════════════════════════

def get_profession_playlist(profession):
    """
    Получить плейлист для профессии (5 треков + информация об артистах)
    
    Args:
        profession: str - название профессии
        
    Returns:
        {
            \"profession\": str,
            \"genre\": str,
            \"mood\": str,
            \"description\": str,
            \"tracks\": [
                {
                    \"name\": str,
                    \"artist\": str,
                    \"url\": str,
                    \"listeners\": int,
                    \"playcount\": str,
                    \"artist_info\": {...}
                }
            ]
        }
    """
    profession_lower = profession.lower().strip()
    
    # Поиск конфига профессии
    config = None
    for key, prof_config in PROFESSION_MUSIC.items():
        if key in profession_lower or profession_lower in key:
            config = prof_config
            break
    
    if not config:
        print(f"⚠️ Профессия '{profession}' не найдена в PROFESSION_MUSIC")
        return None

    print(f"\n🎵 Генерирую плейлист для {profession}...")
    print(f" Жанр: {config['genre']}")
    print(f" Настроение: {config['mood']}")

    all_tracks = []

    # Для каждого артиста получаем его информацию и топ трек
    for i, artist_name in enumerate(config['artists'], 1):
        print(f"\n {i}. Получаю данные: {artist_name}...")

        # Информация об артисте
        artist_info = get_artist_info(artist_name)

        # Топ трек артиста
        tracks = get_artist_top_tracks(artist_name, limit=1)

        if tracks:
            track = tracks[0]
            all_tracks.append({
                "name": track["name"],
                "artist": track["artist"],
                "url": track["url"],
                "listeners": int(track.get("listeners", 0) or 0),
                "playcount": track.get("playcount", "0"),
                "artist_info": artist_info if artist_info else {}
            })

    # Сортируем по количеству слушателей и берем лучшие 5
    all_tracks = sorted(all_tracks, key=lambda x: x['listeners'], reverse=True)[:5]

    print(f"\n✅ Плейлист готов: {len(all_tracks)} треков")

    return {
        "profession": profession,
        "genre": config["genre"],
        "mood": config["mood"],
        "description": config["description"],
        "tracks": all_tracks
    }

# ════════════════════════════════════════════════════════════════════════════════
# ТЕСТИРОВАНИЕ МОДУЛЯ
# ════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ MUSIC INTEGRATION")
    print("="*60)
    
    result = get_profession_playlist("программист")
    
    if result:
        print(f"\n✅ {result['profession']}")
        print(f" Жанр: {result['genre']}")
        print(f" Настроение: {result['mood']}")
        print(f" Описание: {result['description']}")
        
        for i, track in enumerate(result['tracks'], 1):
            print(f"\n {i}. {track['name']}")
            print(f" Артист: {track['artist']}")
            print(f" Last.fm: {track['url']}")
            
            if track['artist_info']:
                info = track['artist_info']
                print(f" 👥 Слушателей: {info.get('listeners', 'N/A')}")
                print(f" ▶️  Проигрываний: {info.get('playcount', 'N/A')}")
                
                if info.get('bio'):
                    print(f" 📝 {info['bio']}")
    
    print("\n" + "="*60)
