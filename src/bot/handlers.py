"""
Обработчики сообщений для Telegram бота
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.db.database import async_session_maker
from src.llm.sql_generator import generate_sql

router = Router()


async def execute_sql_query(sql: str) -> tuple[bool, any]:
    """
    Выполняет SQL запрос к базе данных
    
    Returns:
        (success, result) - успех выполнения и результат
    """
    try:
        async with async_session_maker() as session:
            result = await session.execute(text(sql))
            row = result.fetchone()
            
            if row is None:
                return True, 0
            
            # Извлекаем первое значение из результата
            value = row[0]
            
            # Преобразуем в число
            if value is None:
                return True, 0
            
            # Если это Decimal, преобразуем в int или float
            if hasattr(value, '__int__'):
                try:
                    int_value = int(value)
                    if float(value) == int_value:
                        return True, int_value
                    else:
                        return True, float(value)
                except (ValueError, TypeError):
                    return True, float(value)
            
            return True, value
            
    except Exception as e:
        print(f"Ошибка при выполнении SQL: {e}")
        print(f"SQL запрос: {sql}")
        return False, None


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "Привет! Я бот для аналитики по видео.\n"
        "Задай мне вопрос на русском языке, и я найду ответ в базе данных.\n\n"
        "Примеры вопросов:\n"
        "• Сколько всего видео есть в системе?\n"
        "• Сколько видео у креатора с id '123' вышло с 1 ноября 2025 по 5 ноября 2025?\n"
        "• Сколько видео набрало больше 100000 просмотров?"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "Я умею отвечать на вопросы о видео и статистике.\n\n"
        "Просто напиши вопрос на русском языке, например:\n"
        "• Сколько всего видео есть в системе?\n"
        "• На сколько просмотров в сумме выросли все видео 28 ноября 2025?\n"
        "• Сколько разных видео получали новые просмотры 27 ноября 2025?"
    )


@router.message(F.text)
async def handle_text_message(message: Message):
    """Обработчик текстовых сообщений"""
    user_query = message.text.strip()
    
    if not user_query:
        await message.answer("Пожалуйста, задай вопрос на русском языке.")
        return
    
    # Отправляем сообщение о том, что обрабатываем запрос
    processing_msg = await message.answer("Обрабатываю запрос...")
    
    try:
        # Генерируем SQL запрос
        print(f"Генерация SQL для запроса: {user_query}")
        sql = await generate_sql(user_query)
        
        if not sql:
            print("Не удалось сгенерировать SQL")
            await processing_msg.edit_text(
                "Извините, не удалось сформировать запрос к базе данных. "
                "Попробуйте переформулировать вопрос."
            )
            return
        
        print(f"Сгенерированный SQL: {sql}")
        
        # Выполняем SQL запрос
        success, result = await execute_sql_query(sql)
        
        if not success:
            print(f"Ошибка при выполнении SQL: {sql}")
            await processing_msg.edit_text(
                "Произошла ошибка при выполнении запроса. "
                "Попробуйте переформулировать вопрос."
            )
            return
        
        print(f"Результат запроса: {result}")
        
        # Форматируем ответ - только число
        if isinstance(result, (int, float)):
            if isinstance(result, float) and result.is_integer():
                answer = str(int(result))
            else:
                answer = str(result)
        else:
            answer = str(result)
        
        print(f"Отправка ответа: {answer}")
        try:
            await processing_msg.edit_text(answer)
        except Exception as e:
            print(f"Ошибка при редактировании сообщения: {e}")
            # Если не удалось отредактировать, отправляем новое сообщение
            await message.answer(answer)
        
    except Exception as e:
        import traceback
        print(f"Ошибка при обработке сообщения: {e}")
        print(traceback.format_exc())
        try:
            await processing_msg.edit_text(
                "Произошла ошибка при обработке запроса. Попробуйте позже."
            )
        except:
            await message.answer(
                "Произошла ошибка при обработке запроса. Попробуйте позже."
            )

