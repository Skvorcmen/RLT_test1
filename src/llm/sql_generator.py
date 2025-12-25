"""
Генератор SQL запросов из естественного языка через Ollama
"""
import re
import httpx
from typing import Optional
from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from src.llm.prompts import get_sql_generation_prompt


def validate_sql(sql: str) -> bool:
    """
    Валидирует SQL запрос - разрешает только SELECT
    """
    sql_upper = sql.strip().upper()
    
    # Запрещенные ключевые слова
    forbidden = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
    
    for keyword in forbidden:
        if keyword in sql_upper:
            return False
    
    # Должен начинаться с SELECT
    if not sql_upper.startswith('SELECT'):
        return False
    
    return True


def extract_sql_from_response(response_text: str) -> Optional[str]:
    """
    Извлекает SQL запрос из ответа LLM
    """
    # Убираем markdown код блоки если есть
    response_text = response_text.strip()
    
    # Ищем SQL в markdown блоке
    sql_match = re.search(r'```(?:sql)?\s*(SELECT.*?)(?:```|$)', response_text, re.IGNORECASE | re.DOTALL)
    if sql_match:
        sql = sql_match.group(1).strip()
        # Убираем точку с запятой в конце если есть
        sql = sql.rstrip(';').strip()
        return sql
    
    # Ищем SQL напрямую (до точки с запятой или конца строки)
    sql_match = re.search(r'(SELECT.*?)(?:;|$)', response_text, re.IGNORECASE | re.DOTALL)
    if sql_match:
        sql = sql_match.group(1).strip()
        # Убираем точку с запятой в конце если есть
        sql = sql.rstrip(';').strip()
        return sql
    
    # Если весь ответ похож на SQL
    if response_text.upper().startswith('SELECT'):
        sql = response_text.strip()
        sql = sql.rstrip(';').strip()
        return sql
    
    return None


async def generate_sql(user_query: str) -> Optional[str]:
    """
    Генерирует SQL запрос из естественного языка через Ollama
    
    Args:
        user_query: Запрос пользователя на русском языке
        
    Returns:
        SQL запрос или None в случае ошибки
    """
    prompt = get_sql_generation_prompt(user_query)
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Низкая температура для более точных SQL запросов
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Извлекаем SQL из ответа
            response_text = data.get("response", "").strip()
            sql = extract_sql_from_response(response_text)
            
            if not sql:
                print(f"Не удалось извлечь SQL из ответа: {response_text}")
                return None
            
            # Валидация SQL
            if not validate_sql(sql):
                print(f"SQL запрос не прошел валидацию: {sql}")
                return None
            
            return sql
            
    except httpx.TimeoutException:
        print("Таймаут при обращении к Ollama")
        return None
    except httpx.RequestError as e:
        print(f"Ошибка подключения к Ollama: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при генерации SQL: {e}")
        return None

