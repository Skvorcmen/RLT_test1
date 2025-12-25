"""
Промпты для генерации SQL запросов из естественного языка
"""

SCHEMA_DESCRIPTION = """
База данных содержит две таблицы:

1. Таблица 'videos' (итоговая статистика по видео):
   - id (String) - идентификатор видео
   - creator_id (String) - идентификатор креатора
   - video_created_at (DateTime) - дата и время публикации видео
   - views_count (BigInteger) - финальное количество просмотров
   - likes_count (BigInteger) - финальное количество лайков
   - comments_count (BigInteger) - финальное количество комментариев
   - reports_count (BigInteger) - финальное количество жалоб
   - created_at (DateTime) - служебное поле
   - updated_at (DateTime) - служебное поле

2. Таблица 'video_snapshots' (почасовые замеры статистики):
   - id (String) - идентификатор снапшота
   - video_id (String) - ссылка на видео (внешний ключ к videos.id)
   - views_count (BigInteger) - текущее количество просмотров на момент замера
   - likes_count (BigInteger) - текущее количество лайков
   - comments_count (BigInteger) - текущее количество комментариев
   - reports_count (BigInteger) - текущее количество жалоб
   - delta_views_count (BigInteger) - приращение просмотров с прошлого замера
   - delta_likes_count (BigInteger) - приращение лайков
   - delta_comments_count (BigInteger) - приращение комментариев
   - delta_reports_count (BigInteger) - приращение жалоб
   - created_at (DateTime) - время замера (раз в час)
   - updated_at (DateTime) - служебное поле

Важно:
- Для подсчета общего количества видео используй таблицу videos
- Для подсчета прироста/изменений используй таблицу video_snapshots и поля delta_*
- Для фильтрации по датам используй video_created_at в videos или created_at в video_snapshots
- Даты могут быть в формате 'YYYY-MM-DD' или диапазоном
- Все запросы должны быть только SELECT (без INSERT, UPDATE, DELETE, DROP)
"""

EXAMPLES = """
Примеры запросов:

1. "Сколько всего видео есть в системе?"
   SQL: SELECT COUNT(*) FROM videos;

2. "Сколько видео у креатора с id '123' вышло с 1 ноября 2025 по 5 ноября 2025 включительно?"
   SQL: SELECT COUNT(*) FROM videos 
        WHERE creator_id = '123' 
        AND video_created_at >= '2025-11-01' 
        AND video_created_at <= '2025-11-05 23:59:59';

3. "Сколько видео набрало больше 100000 просмотров за всё время?"
   SQL: SELECT COUNT(*) FROM videos WHERE views_count > 100000;

4. "На сколько просмотров в сумме выросли все видео 28 ноября 2025?"
   SQL: SELECT COALESCE(SUM(delta_views_count), 0) FROM video_snapshots 
        WHERE DATE(created_at) = '2025-11-28';

5. "Сколько разных видео получали новые просмотры 27 ноября 2025?"
   SQL: SELECT COUNT(DISTINCT video_id) FROM video_snapshots 
        WHERE DATE(created_at) = '2025-11-27' 
        AND delta_views_count > 0;

6. "Сколько видео у креатора с id 'aca1061a9d324ecf8c3fa2bb32d7be63' набрали больше 10000 просмотров по итоговой статистике?"
   SQL: SELECT COUNT(*) FROM videos 
        WHERE creator_id = 'aca1061a9d324ecf8c3fa2bb32d7be63' 
        AND views_count > 10000;

7. "Сколько всего есть замеров статистики, в которых число просмотров за час оказалось отрицательным?"
   SQL: SELECT COUNT(*) FROM video_snapshots 
        WHERE delta_views_count < 0;

8. "Какое суммарное количество просмотров набрали все видео, опубликованные в июне 2025 года?"
   SQL: SELECT SUM(views_count) FROM videos 
        WHERE video_created_at >= '2025-06-01' 
        AND video_created_at < '2025-07-01';

9. "На сколько просмотров суммарно выросли все видео креатора с id 'cd87be38b50b4fdd8342bb3c383f3c7d' в промежутке с 10:00 до 15:00 28 ноября 2025 года?"
   SQL: SELECT COALESCE(SUM(vs.delta_views_count), 0) 
        FROM video_snapshots vs
        JOIN videos v ON vs.video_id = v.id
        WHERE v.creator_id = 'cd87be38b50b4fdd8342bb3c383f3c7d'
        AND DATE(vs.created_at) = '2025-11-28'
        AND EXTRACT(HOUR FROM vs.created_at) >= 10
        AND EXTRACT(HOUR FROM vs.created_at) < 15;

Важно различать:
- "Сколько замеров/видео/записей" → используй COUNT(*)
- "На сколько в сумме/сколько всего" (про сумму значений) → используй SUM()
- "Сколько разных" → используй COUNT(DISTINCT ...)
- Для итоговой статистики по видео (просмотры, лайки и т.д.) используй таблицу videos и поля views_count, likes_count и т.д.
- Для прироста/изменений используй таблицу video_snapshots и поля delta_views_count, delta_likes_count и т.д.
- Для фильтрации по дате публикации видео используй video_created_at в таблице videos
- Для фильтрации по дате замера используй created_at в таблице video_snapshots
- Если нужно фильтровать замеры по creator_id, используй JOIN: JOIN videos v ON video_snapshots.video_id = v.id, затем WHERE v.creator_id = '...'
- Для фильтрации по времени используй EXTRACT(HOUR FROM created_at) >= X AND EXTRACT(HOUR FROM created_at) < Y (не используй функцию TIME())
"""


def get_sql_generation_prompt(user_query: str) -> str:
    """
    Формирует промпт для генерации SQL запроса
    """
    prompt = f"""{SCHEMA_DESCRIPTION}

{EXAMPLES}

Запрос пользователя на русском языке: "{user_query}"

Твоя задача: сгенерировать SQL запрос (только SELECT), который отвечает на этот вопрос.

Важные правила:
1. Генерируй ТОЛЬКО SQL запрос, без дополнительных объяснений
2. Используй только SELECT запросы
3. Для дат используй формат 'YYYY-MM-DD' или 'YYYY-MM-DD HH:MM:SS'
4. Для диапазонов дат используй >= и <=
5. Ответ должен быть одним числом (используй COUNT, SUM, AVG и т.д.)
6. Не используй кавычки вокруг SQL запроса, просто верни чистый SQL
7. ВАЖНО: Если вопрос "Сколько замеров/видео/записей" - используй COUNT(*), а не SUM()
8. SUM() используется только когда спрашивают про сумму значений (например "на сколько в сумме")

SQL запрос:
"""
    return prompt

