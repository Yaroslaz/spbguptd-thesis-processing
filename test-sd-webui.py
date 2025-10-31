"""
test_sd_direct.py - прямой тест отправки в SD WebUI
Проверяет ЧТО возвращает SD WebUI
"""

import requests
import json
import base64
from pathlib import Path

SD_WEBUI_URL = "http://127.0.0.1:7860"

print("="*60)
print("🧪 ПРЯМОЙ ТЕСТ SD WebUI")
print("="*60)

# Шаг 1: Проверяем соединение
print("\n1️⃣ Проверка соединения...")
try:
    response = requests.get(f"{SD_WEBUI_URL}/config", timeout=5)
    print(f"✅ Соединение OK (статус {response.status_code})")
except Exception as e:
    print(f"❌ Нет соединения: {e}")
    exit()

# Шаг 2: Отправляем простой запрос
print("\n2️⃣ Отправка простого запроса...")

payload = {
    "prompt": "beautiful landscape, mountains, 4k",
    "negative_prompt": "ugly, blurry",
    "steps": 5,  # Минимум для теста
    "cfg_scale": 7,
    "width": 512,
    "height": 512,
    "sampler_name": "Euler",
}

print(f"   Промпт: {payload['prompt']}")
print(f"   Шаги: {payload['steps']}")

try:
    response = requests.post(
        f"{SD_WEBUI_URL}/sdapi/v1/txt2img",
        json=payload,
        timeout=300
    )
    
    print(f"   Статус: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Ответ получен")
        print(f"   Ключи: {list(result.keys())}")
        
        if 'images' in result:
            print(f"   Изображений: {len(result['images'])}")
            if result['images']:
                print(f"   Размер первого: {len(result['images'][0])} символов base64")
        else:
            print(f"   ⚠️ Нет ключа 'images'!")
            print(f"   Полный ответ: {json.dumps(result, indent=2)[:500]}")
    else:
        print(f"   ❌ Ошибка статуса!")
        print(f"   Ответ: {response.text[:300]}")
        
except Exception as e:
    print(f"❌ Ошибка запроса: {e}")
    import traceback
    traceback.print_exc()

# Шаг 3: Проверяем папку
print("\n3️⃣ Проверка папки SD WebUI...")

output_dir = r"C:\Users\Joros\Desktop\career-vibe-generator\stable-diffusion-webui-1.10.1\outputs\txt2img-images"

try:
    path = Path(output_dir)
    
    if path.exists():
        print(f"✅ Папка найдена")
        
        # Считаем папки
        folders = list(path.iterdir())
        print(f"   Подпапок: {len(folders)}")
        
        if folders:
            # Ищем последнюю папку
            latest = sorted([d for d in folders if d.is_dir()], 
                          key=lambda x: x.stat().st_mtime, reverse=True)[0]
            
            print(f"   Последняя: {latest.name}")
            
            # Ищем PNG
            pngs = list(latest.glob("*.png"))
            print(f"   PNG файлов: {len(pngs)}")
            
            if pngs:
                latest_png = sorted(pngs, key=lambda x: x.stat().st_mtime, reverse=True)[0]
                print(f"   Последний PNG: {latest_png.name}")
                print(f"   Размер: {latest_png.stat().st_size} bytes")
                print(f"   Время: {latest_png.stat().st_mtime}")
            else:
                print(f"   ⚠️ PNG файлов не найдено!")
                print(f"   Что в папке: {list(latest.iterdir())}")
    else:
        print(f"❌ Папка не найдена: {output_dir}")
        
except Exception as e:
    print(f"❌ Ошибка проверки папки: {e}")

print("\n" + "="*60)
print("Чек завершён")
print("="*60)
