import requests
import os

LASTFM_API_KEY = os.getenv('LASTFM_API_KEY', '62fcb3c12d37e0b2d84b6dd5e6a5c8d9')
LASTFM_BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# ✅ МАППИНГ ПРОФЕССИЙ С ЖАНРОМ, MOOD И DESCRIPTION
PROFESSION_MUSIC = {
    "программист": {
        "genre": "Электроника",
        "mood": "Концентрация",
        "description": "Электроника для фокуса и творчества",
        "tags": ["electronic", "synthwave", "ambient", "tech house"],
        "artists": ["Daft Punk", "Avicii", "Martin Garrix", "Deadmau5", "Skrillex"]
    },
    "frontend-разработчик": {
        "genre": "Электроника / EDM",
        "mood": "Энергия",
        "description": "Электронная музыка для продуктивности",
        "tags": ["electronic", "synthwave", "edm", "tech house"],
        "artists": ["Daft Punk", "Disclosure", "Deadmau5", "Avicii", "Calvin Harris"]
    },
    "backend-разработчик": {
        "genre": "Ambient / Электроника",
        "mood": "Сосредоточенность",
        "description": "Спокойная электроника для долгих кодинг-сессий",
        "tags": ["ambient", "electronic", "industrial", "experimental"],
        "artists": ["Vangelis", "Tangerine Dream", "Thom Yorke", "Jon Hopkins", "Amon Tobin"]
    },
    "data scientist": {
        "genre": "Experimental / Глитч",
        "mood": "Аналитика",
        "description": "Экспериментальная музыка для глубокого анализа",
        "tags": ["electronic", "experimental", "ambient", "glitch"],
        "artists": ["Autechre", "Aphex Twin", "Boards of Canada", "Four Tet", "Oneohtrix Point Never"]
    },
    "повар": {
        "genre": "Jazz / Funk / Soul",
        "mood": "Творчество",
        "description": "Джаз и фанк для вдохновения на кухне",
        "tags": ["jazz", "funk", "soul", "world"],
        "artists": ["Miles Davis", "Herbie Hancock", "Earth Wind & Fire", "Stevie Wonder", "Canned Heat"]
    },
    "шеф-повар": {
        "genre": "Jazz / Classical / Ambient",
        "mood": "Элегантность",
        "description": "Классическая и джазовая музыка для утончённой кухни",
        "tags": ["jazz", "classical", "ambient", "world"],
        "artists": ["Miles Davis", "Bill Evans", "Claude Debussy", "Erik Satie", "Ludovico Einaudi"]
    },
    "кондитер": {
        "genre": "Indie / Electropop",
        "mood": "Радость",
        "description": "Позитивная музыка для сладких творений",
        "tags": ["pop", "indie", "electropop", "dream pop"],
        "artists": ["The 1975", "Passion Pit", "MGMT", "Grimes", "FKA twigs"]
    },
    "пожарный": {
        "genre": "Rock / Metal",
        "mood": "Решительность",
        "description": "Энергичный рок для боевого духа",
        "tags": ["rock", "metal", "punk", "hard rock"],
        "artists": ["AC/DC", "The Who", "Queen", "Led Zeppelin", "Black Sabbath"]
    },
    "полицейский": {
        "genre": "Rock / Punk / Reggae",
        "mood": "Стабильность",
        "description": "Динамичная музыка для порядка и справедливости",
        "tags": ["rock", "punk", "ska", "reggae"],
        "artists": ["The Police", "Bob Marley", "The Clash", "Sublime", "Reel Big Fish"]
    },
    "охранник": {
        "genre": "Hip-Hop / Trap",
        "mood": "Внимательность",
        "description": "Хип-хоп для сосредоточенной защиты",
        "tags": ["hip-hop", "trap", "grime", "reggae"],
        "artists": ["Wu-Tang Clan", "Nas", "50 Cent", "Run-DMC", "Public Enemy"]
    },
    "художник": {
        "genre": "Alternative / Experimental / Art Rock",
        "mood": "Вдохновение",
        "description": "Экспериментальная музыка для творческого полёта",
        "tags": ["indie", "alternative", "experimental", "art rock"],
        "artists": ["Radiohead", "Björk", "Laurie Anderson", "Laurens Lilienthal", "Yoko Ono"]
    },
    "музыкант": {
        "genre": "Classical / Jazz / Fusion",
        "mood": "Гармония",
        "description": "Классическая и джазовая музыка для музыкального вдохновения",
        "tags": ["classical", "jazz", "world", "fusion"],
        "artists": ["Ludwig van Beethoven", "Wolfgang Amadeus Mozart", "John Coltrane", "Pat Metheny", "Yo-Yo Ma"]
    },
    "актёр": {
        "genre": "Pop / Rock / Theatrical",
        "mood": "Эмоциональность",
        "description": "Драматическая музыка для воплощения образов",
        "tags": ["pop", "rock", "theatrical", "musical theatre"],
        "artists": ["David Bowie", "Queen", "Meatloaf", "Pink Floyd", "The Beatles"]
    },
    "дизайнер": {
        "genre": "Electronic / Art Pop / Indie",
        "mood": "Креативность",
        "description": "Авангардная музыка для смелых дизайнерских решений",
        "tags": ["electronic", "synthwave", "indie", "art pop"],
        "artists": ["Grimes", "Janelle Monáe", "FKA twigs", "Arca", "Caroline Polachek"]
    },
    "политик": {
        "genre": "Classical / Opera / Orchestral",
        "mood": "Величие",
        "description": "Классическая музыка для государственных решений",
        "tags": ["classical", "opera", "orchestral", "world"],
        "artists": ["Giuseppe Verdi", "Georges Bizet", "Johann Strauss II", "Nile Rodgers", "Stevie Wonder"]
    },
    "дипломат": {
        "genre": "Classical / Jazz / World Music",
        "mood": "Компромисс",
        "description": "Музыка мира для мирного диалога",
        "tags": ["classical", "jazz", "world music", "ambient"],
        "artists": ["Duke Ellington", "Bill Evans", "Ravi Shankar", "Buika", "Seu Jorge"]
    },
    "пресс-секретарь": {
        "genre": "Pop / Rock / Soul / Funk",
        "mood": "Коммуникация",
        "description": "Динамичная музыка для эффективного общения",
        "tags": ["pop", "rock", "soul", "funk"],
        "artists": ["Prince", "Michael Jackson", "The Rolling Stones", "Lizzo", "Anderson .Paak"]
    }
}

def get_artist_info(artist_name):
    """Получить информацию об артисте из Last.fm"""
    try:
        params = {
            'method': 'artist.getinfo',
            'artist': artist_name,
            'api_key': LASTFM_API_KEY,
            'format': 'json'
        }
        response = requests.get(LASTFM_BASE_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'artist' in data:
                artist = data['artist']
                listeners = artist.get('stats', {}).get('listeners', 'N/A')
                playcount = artist.get('stats', {}).get('playcount', 'N/A')
                return {
                    'name': artist.get('name', artist_name),
                    'listeners': listeners,
                    'playcount': playcount,
                    'bio': artist.get('bio', {}).get('summary', '')
                }
    except Exception as e:
        print(f"⚠️  Ошибка получения информации об артисте {artist_name}: {e}")
    return None

def get_artist_top_tracks(artist_name, limit=1):
    """Получить топ треки артиста из Last.fm"""
    try:
        params = {
            'method': 'artist.gettoptracks',
            'artist': artist_name,
            'limit': limit,
            'api_key': LASTFM_API_KEY,
            'format': 'json'
        }
        response = requests.get(LASTFM_BASE_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'toptracks' in data:
                toptracks = data['toptracks'].get('track', [])
                if not isinstance(toptracks, list):
                    toptracks = [toptracks]
                
                tracks = []
                for track in toptracks[:limit]:
                    tracks.append({
                        'name': track.get('name', 'Unknown'),
                        'playcount': track.get('playcount', 'N/A'),
                        'listeners': track.get('listeners', 'N/A'),
                        'url': track.get('url', '')
                    })
                return tracks
    except Exception as e:
        print(f"⚠️  Ошибка получения треков {artist_name}: {e}")
    return []

def get_profession_playlist(profession):
    """✅ Получить плейлист для профессии с description и mood"""
    profession_lower = profession.lower().strip()
    
    if profession_lower not in PROFESSION_MUSIC:
        print(f"⚠️  Профессия '{profession}' не найдена")
        return None
    
    config = PROFESSION_MUSIC[profession_lower]
    print(f"\n🎵 Генерирую плейлист для '{profession}'...")
    print(f"   Жанр: {config['genre']}")
    print(f"   Mood: {config.get('mood', 'N/A')}")
    print(f"   Описание: {config.get('description', 'N/A')}")
    
    tracks = []
    artists_list = config['artists'][:5]
    
    for artist_name in artists_list:
        print(f"   ⏳ Получаю информацию об артисте: {artist_name}")
        artist_info = get_artist_info(artist_name)
        top_tracks = get_artist_top_tracks(artist_name, limit=1)
        
        if top_tracks:
            track = top_tracks[0]
            track_data = {
                'name': track.get('name', 'Unknown Track'),
                'artist': artist_name,
                'artist_info': artist_info,
                'playcount': track.get('playcount', 'N/A'),
                'listeners': track.get('listeners', 'N/A'),
                'url': track.get('url', '')
            }
            tracks.append(track_data)
            if artist_info:
                print(f"      ✅ {track['name']} - {artist_info.get('listeners', 'N/A')} слушателей")
    
    # ✅ ВОЗВРАЩАЕМ DESCRIPTION И MOOD
    result = {
        'profession': profession,
        'genre': config['genre'],
        'mood': config.get('mood', ''),               # ✅ ДОБАВЛЕНО
        'description': config.get('description', ''),  # ✅ ДОБАВЛЕНО
        'tags': config['tags'],
        'tracks': tracks
    }
    
    print(f"   ✅ Плейлист готов! Треков: {len(tracks)}")
    return result
