import os
import requests
from PIL import Image
from io import BytesIO
import time
import json

def generate_moodboard_composite(sd_prompts, profession):
    """
    Генерирует 6 изображений через Stable Diffusion и создает коллаж 2x3
    Сохраняет в /static/images/
    """
    print(f"\n{'='*60}")
    print(f"🎨 ГЕНЕРАЦИЯ МУДБОРДА для {profession}")
    print(f"{'='*60}")
    
    if not sd_prompts or len(sd_prompts) == 0:
        print(f"❌ Нет SD промптов для {profession}")
        return None
    
    prompts_to_use = sd_prompts[:6]
    print(f"📋 Буду генерировать {len(prompts_to_use)} изображений\n")
    
    images = []
    for i, prompt in enumerate(prompts_to_use, 1):
        print(f"🖼️  Генерирую изображение {i}/6...")
        print(f"   Промпт: {prompt[:80]}...")
        
        img = _generate_image_sd(prompt)
        if img:
            images.append(img)
            print(f"   ✅ Готово")
        else:
            print(f"   ❌ Ошибка генерации")
            placeholder = Image.new('RGB', (512, 512), color=(200, 200, 200))
            images.append(placeholder)
        
        time.sleep(1)
    
    if len(images) < 6:
        print(f"⚠️ Удалось сгенерировать только {len(images)}/6 изображений")
    
    print(f"\n🔗 Создаю коллаж из {len(images)} изображений...")
    collage_path = _create_collage_2x3(images, profession)
    
    if collage_path:
        print(f"✅ Коллаж сохранён: {collage_path}")
        return collage_path
    else:
        print(f"❌ Ошибка при создании коллажа")
        return None

def _generate_image_sd(prompt):
    """
    Генерирует одно изображение через Stable Diffusion WebUI API
    """
    sd_api_url = os.getenv('SD_API_URL', 'http://127.0.0.1:7860')
    
    try:
        url = f"{sd_api_url}/sdapi/v1/txt2img"
        
        payload = {
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, distorted, ugly, bad anatomy",
            "steps": 20,
            "cfg_scale": 7,
            "width": 512,
            "height": 512,
            "sampler_name": "Euler a",
            "seed": -1
        }
        
        print(f"   📤 Отправляю запрос к SD API...")
        
        response = requests.post(url, json=payload, timeout=120)
        
        print(f"   🔍 SD API ответ: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if 'images' in result and len(result['images']) > 0:
                import base64
                img_data = base64.b64decode(result['images'][0])
                img = Image.open(BytesIO(img_data))
                print(f"   ✅ Изображение получено (512x512)")
                return img
            else:
                print(f"   ❌ Нет изображений в ответе")
                return None
        elif response.status_code == 404:
            print(f"   ❌ SD API ошибка 404 - endpoint не найден")
            return None
        elif response.status_code == 500:
            print(f"   ❌ SD API ошибка 500 - ошибка сервера")
            return None
        elif response.status_code == 422:
            print(f"   ❌ SD API ошибка 422 - неправильный формат запроса")
            return None
        else:
            print(f"   ❌ SD API ошибка {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout: SD API не ответил за 120 сек")
        return None
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Ошибка подключения: SD API недоступен")
        return None
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return None

def _create_collage_2x3(images, profession):
    """
    Создаёт коллаж из 6 изображений в формате 2 строки x 3 колонки
    Сохраняет в /static/images/
    """
    try:
        # Убедимся, что директория существует
        os.makedirs('static/images', exist_ok=True)
        
        if len(images) < 6:
            print(f"⚠️ Недостаточно изображений: {len(images)}/6")
            while len(images) < 6:
                images.append(Image.new('RGB', (512, 512), color=(100, 100, 100)))
        
        img_size = 512
        collage_width = img_size * 3
        collage_height = img_size * 2
        
        collage = Image.new('RGB', (collage_width, collage_height), color=(255, 255, 255))
        
        positions = [
            (0, 0), (1, 0), (2, 0),
            (0, 1), (1, 1), (2, 1),
        ]
        
        for i, (col, row) in enumerate(positions):
            if i < len(images):
                img = images[i]
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                if img.size != (img_size, img_size):
                    img = img.resize((img_size, img_size), Image.Resampling.LANCZOS)
                
                x = col * img_size
                y = row * img_size
                collage.paste(img, (x, y))
        
        print(f"✅ Коллаж создан: {collage_width}x{collage_height}")
        
        # Сохраняем с правильным путём
        profession_slug = profession.lower().replace(' ', '_').replace('-', '_')
        filename = f"moodboard_{profession_slug}.jpg"
        filepath = os.path.join('static', 'images', filename)
        
        collage.save(filepath, quality=95)
        print(f"💾 Сохранён: {filepath}")
        
        # Возвращаем ОТНОСИТЕЛЬНЫЙ путь для браузера
        web_path = f"/static/images/{filename}"
        print(f"🌐 Web путь: {web_path}")
        
        return web_path
        
    except Exception as e:
        print(f"❌ Ошибка при создании коллажа: {e}")
        import traceback
        traceback.print_exc()
        return None
