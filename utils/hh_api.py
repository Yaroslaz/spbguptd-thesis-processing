import requests
import time
from typing import Dict, List, Optional

def get_vacancy_stats_multi_source(profession: str, area: int = 113) -> Dict:
    """
    Получает статистику по профессии с HH.ru API
    
    Args:
        profession: Название профессии
        area: Регион (113 = Россия)
    
    Returns:
        Dict с статистикой
    """
    print(f"\n📊 Получаю статистику для профессии: {profession}")
    print(f" Запрашиваю данные с HH.ru...")

    try:
        # Этап 1: Получаем список вакансий
        search_url = "https://api.hh.ru/vacancies"
        
        search_params = {
            'text': profession,
            'area': area,
            'per_page': 100,
            'order_by': 'publication_time'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(search_url, params=search_params, headers=headers, timeout=15)
        response.raise_for_status()

        data = response.json()

        # Этап 2: Анализируем данные
        vacancies = data.get('items', [])
        total_vacancies = data.get('found', 0)

        print(f" ✓ Найдено вакансий: {total_vacancies}")

        # Сбор зарплат
        salaries_from = []
        salaries_to = []
        salaries_all = []

        for vacancy in vacancies:
            salary_info = vacancy.get('salary')
            if salary_info:
                if salary_info.get('from'):
                    salaries_from.append(salary_info['from'])
                    salaries_all.append(salary_info['from'])
                if salary_info.get('to'):
                    salaries_to.append(salary_info['to'])
                    salaries_all.append(salary_info['to'])

        # Расчет статистики
        avg_salary = None
        min_salary = None
        max_salary = None
        salary_count = 0

        if salaries_all:
            avg_salary = int(sum(salaries_all) / len(salaries_all))
            min_salary = int(min(salaries_all))
            max_salary = int(max(salaries_all))
            salary_count = len(set(salaries_all))

            print(f" ✓ Средняя зарплата: {avg_salary:,} руб")
            print(f" ✓ Диапазон: {min_salary:,} - {max_salary:,} руб")
            print(f" ✓ Вакансий с зарплатой: {salary_count}")
        else:
            print(f" ⚠ Информация о зарплате отсутствует")

        # Определение уровня конкуренции
        competition = "Неизвестно"
        competition_level = "unknown"

        if total_vacancies > 0:
            if total_vacancies > 3000:
                competition = "Очень высокая конкуренция"
                competition_level = "very_high"
            elif total_vacancies > 1500:
                competition = "Высокая конкуренция"
                competition_level = "high"
            elif total_vacancies > 500:
                competition = "Средняя конкуренция"
                competition_level = "medium"
            elif total_vacancies > 100:
                competition = "Умеренная конкуренция"
                competition_level = "moderate"
            elif total_vacancies > 20:
                competition = "Низкая конкуренция"
                competition_level = "low"
            else:
                competition = "Очень низкая конкуренция"
                competition_level = "very_low"

        print(f" ✓ Конкуренция: {competition}")

        # Форматируем среднюю зарплату
        avg_salary_formatted = "Не доступно"
        if avg_salary:
            if avg_salary >= 1000000:
                avg_salary_formatted = f"{avg_salary // 1000000} млн руб"
            elif avg_salary >= 1000:
                avg_salary_formatted = f"{avg_salary // 1000:,} тыс руб"
            else:
                avg_salary_formatted = f"{avg_salary:,} руб"

        # Получаем топ вакансии
        top_vacancies = []
        for vacancy in vacancies[:5]:
            company_name = vacancy.get('employer', {}).get('name', 'Компания')
            position_title = vacancy.get('name', 'Вакансия')
            top_vacancies.append({
                'position': position_title,
                'company': company_name
            })

        print(f" ✓ Статистика получена успешно\n")

        # Итоговая статистика
        stats = {
            'total': total_vacancies,
            'avg_salary': avg_salary,
            'avg_salary_formatted': avg_salary_formatted,
            'min_salary': min_salary,
            'max_salary': max_salary,
            'salary_info_count': salary_count,
            'competition': competition,
            'competition_level': competition_level,
            'top_vacancies': top_vacancies,
            'perspective': _get_perspective(total_vacancies),
            'source': 'HH.ru API'
        }

        return stats

    except requests.exceptions.Timeout:
        print(f" ❌ Timeout при запросе к HH.ru")
        return _get_fallback_stats(profession)

    except requests.exceptions.ConnectionError:
        print(f" ❌ Ошибка подключения к HH.ru")
        return _get_fallback_stats(profession)

    except Exception as e:
        print(f" ❌ Ошибка: {e}")
        return _get_fallback_stats(profession)

def search_related_vacancies(profession: str, area: int = 113, limit: int = 5) -> List[Dict]:
    """
    Получает подходящие вакансии по профессии с HH.ru
    
    Args:
        profession: Название профессии
        area: Регион (113 = Россия)
        limit: Максимум вакансий
    
    Returns:
        List с вакансиями
    """
    print(f"\n🔍 Ищу подходящие вакансии для: {profession}")

    try:
        search_url = "https://api.hh.ru/vacancies"
        
        search_params = {
            'text': profession,
            'area': area,
            'per_page': limit,
            'order_by': 'publication_time'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(search_url, params=search_params, headers=headers, timeout=15)
        response.raise_for_status()

        data = response.json()
        vacancies = data.get('items', [])

        result = []

        for vacancy in vacancies[:limit]:
            vacancy_info = {
                'id': vacancy.get('id'),
                'name': vacancy.get('name', 'Вакансия'),
                'company': vacancy.get('employer', {}).get('name', 'Компания'),
                'area': vacancy.get('area', {}).get('name', 'Неизвестно'),
                'salary': _format_salary(vacancy.get('salary')),
                'url': vacancy.get('alternate_url', '#'),
                'published_at': vacancy.get('published_at', ''),
                'experience': vacancy.get('experience', {}).get('name', 'Не указан')
            }
            
            result.append(vacancy_info)

        print(f" ✓ Найдено подходящих вакансий: {len(result)}")

        return result

    except Exception as e:
        print(f" ❌ Ошибка при поиске вакансий: {e}")
        return []

def _format_salary(salary_info: Optional[Dict]) -> str:
    """Форматирует информацию о зарплате"""
    if not salary_info:
        return "Зарплата не указана"
    
    salary_from = salary_info.get('from')
    salary_to = salary_info.get('to')
    currency = salary_info.get('currency', 'RUB')
    
    if salary_from and salary_to:
        return f"{salary_from:,} - {salary_to:,} {currency}"
    elif salary_from:
        return f"от {salary_from:,} {currency}"
    elif salary_to:
        return f"до {salary_to:,} {currency}"
    else:
        return "Зарплата не указана"

def _get_perspective(vacancy_count: int) -> str:
    """Определяет перспективность профессии"""
    if vacancy_count > 2000:
        return "Очень высокая перспективность - огромный спрос на рынке"
    elif vacancy_count > 1000:
        return "Высокая перспективность - стабильный спрос"
    elif vacancy_count > 300:
        return "Хорошая перспективность - регулярный спрос"
    elif vacancy_count > 50:
        return "Средняя перспективность - существует спрос"
    else:
        return "Низкая перспективность - нишевая профессия"

def _get_fallback_stats(profession: str) -> Dict:
    """Возвращает fallback статистику"""
    print(f" ℹ Используется примерная статистика")
    return {
        'total': 0,
        'avg_salary': None,
        'avg_salary_formatted': 'Не доступно',
        'min_salary': None,
        'max_salary': None,
        'salary_info_count': 0,
        'competition': 'Данные недоступны',
        'competition_level': 'unknown',
        'top_vacancies': [],
        'perspective': 'Статистика временно недоступна',
        'source': 'Fallback'
    }

def get_salary_by_experience_level(profession: str, area: int = 113) -> Dict[str, int]:
    """Получает зарплату по уровню опыта"""
    try:
        salary_by_level = {}

        for level, keywords in [
            ('junior', ['junior', 'junior', 'стажер']),
            ('middle', ['middle', 'middle', 'опытный']),
            ('senior', ['senior', 'senior', 'ведущий'])
        ]:
            search_text = f"{profession} {keywords[0]}"

            response = requests.get(
                "https://api.hh.ru/vacancies",
                params={
                    'text': search_text,
                    'area': area,
                    'per_page': 50
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                vacancies = data.get('items', [])

                salaries = []

                for vacancy in vacancies:
                    salary_info = vacancy.get('salary')
                    if salary_info and salary_info.get('from'):
                        salaries.append(salary_info['from'])

                if salaries:
                    salary_by_level[level] = int(sum(salaries) / len(salaries))

        return salary_by_level

    except Exception as e:
        print(f"Ошибка при получении зарплаты по уровням: {e}")
        return {}
