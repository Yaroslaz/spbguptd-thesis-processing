"""
profession_validator.py - ПЕРЕРАБОТАННАЯ версия v10
Проверка профессий через HH.ru API и локальную базу
"""

import requests
from typing import Tuple, Dict

class ProfessionValidator:
    def __init__(self):
        self.known_professions = {
            # IT
            'программист', 'разработчик', 'devops', 'devops-инженер',
            'тестировщик', 'аналитик', 'дизайнер', 'ux/ui дизайнер',
            'фронтенд', 'бэкенд', 'fullstack', 'java', 'python',
            'javascript', 'react', 'data scientist', 'ml engineer',
            # Кулинария
            'повар', 'кондитер', 'пекарь', 'шеф-повар', 'бармен', 'официант',
            # Другие
            'учитель', 'врач', 'медсестра', 'юрист', 'бухгалтер',
            'менеджер', 'инженер', 'архитектор', 'маркетолог',
            'электрик', 'сантехник', 'строитель', 'водитель',
            'фотограф', 'видеограф', 'журналист', 'копирайтер',
            'hr', 'pm', 'рекрутер', 'логист', 'финансист'
        }

    def validate_profession(self, profession: str) -> Tuple[bool, str, Dict]:
        """Проверяет существование профессии"""
        profession = profession.strip().lower()
        
        if not profession or len(profession) < 2:
            return False, "Слишком короткое название", {}
        
        # Проверяем локальную базу
        if self._is_known_real(profession):
            return True, "Профессия найдена в базе", {"source": "known_db"}
        
        # Проверяем на HH.ru
        if self._check_hh_ru(profession):
            return True, "Профессия найдена на HH.ru", {"source": "hh_ru"}
        
        return False, "Профессия не найдена", {}

    def _is_known_real(self, profession: str) -> bool:
        """Проверяет наличие в базе известных профессий"""
        profession_lower = profession.lower()
        
        # Прямое совпадение
        if profession_lower in self.known_professions:
            return True
        
        # Частичное совпадение
        for known in self.known_professions:
            if known in profession_lower or profession_lower in known:
                return True
        
        return False

    def _check_hh_ru(self, profession: str) -> bool:
        """Проверяет профессию на HH.ru"""
        try:
            response = requests.get(
                'https://api.hh.ru/vacancies',
                params={
                    'text': profession,
                    'area': 1,
                    'per_page': 1
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('found', 0) > 0
            
            return False
        except:
            return False

# Глобальный экземпляр
validator = ProfessionValidator()

def validate_profession_smart(profession):
    """Быстрая проверка профессии"""
    exists, reason, details = validator.validate_profession(profession)
    return exists, reason

def check_profession_exists(profession):
    """Проверка существования профессии"""
    exists, _, _ = validator.validate_profession(profession)
    return exists