"""
Скрипт для загрузки JSON данных в базу данных
"""
import asyncio
import json
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import async_session_maker, init_db
from src.db.models import Video, VideoSnapshot


def parse_datetime(dt_str: str) -> datetime:
    """Парсит строку даты в datetime объект (без timezone)"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        # Убираем timezone для PostgreSQL TIMESTAMP WITHOUT TIME ZONE
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt
    except:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt


async def load_videos_data(session: AsyncSession, json_file: str):
    """Загружает данные из JSON файла в базу данных"""
    print(f"Загрузка данных из {json_file}...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Поддержка разных форматов: массив напрямую или объект с ключом 'videos'
    if isinstance(data, list):
        videos_data = data
    else:
        videos_data = data.get('videos', [])
    total_videos = len(videos_data)
    print(f"Найдено видео: {total_videos}")
    
    videos_created = 0
    snapshots_created = 0
    
    for idx, video_data in enumerate(videos_data, 1):
        try:
            # Создаем видео
            video = Video(
                id=video_data['id'],
                creator_id=video_data['creator_id'],
                video_created_at=parse_datetime(video_data['video_created_at']),
                views_count=video_data.get('views_count', 0),
                likes_count=video_data.get('likes_count', 0),
                comments_count=video_data.get('comments_count', 0),
                reports_count=video_data.get('reports_count', 0),
                created_at=parse_datetime(video_data.get('created_at', video_data['video_created_at'])),
                updated_at=parse_datetime(video_data.get('updated_at', video_data['video_created_at']))
            )
            session.add(video)
            videos_created += 1
            
            # Создаем снапшоты
            snapshots = video_data.get('snapshots', [])
            for snapshot_data in snapshots:
                snapshot = VideoSnapshot(
                    id=snapshot_data['id'],
                    video_id=video_data['id'],
                    views_count=snapshot_data.get('views_count', 0),
                    likes_count=snapshot_data.get('likes_count', 0),
                    comments_count=snapshot_data.get('comments_count', 0),
                    reports_count=snapshot_data.get('reports_count', 0),
                    delta_views_count=snapshot_data.get('delta_views_count', 0),
                    delta_likes_count=snapshot_data.get('delta_likes_count', 0),
                    delta_comments_count=snapshot_data.get('delta_comments_count', 0),
                    delta_reports_count=snapshot_data.get('delta_reports_count', 0),
                    created_at=parse_datetime(snapshot_data['created_at']),
                    updated_at=parse_datetime(snapshot_data.get('updated_at', snapshot_data['created_at']))
                )
                session.add(snapshot)
                snapshots_created += 1
            
            if idx % 100 == 0:
                await session.commit()
                print(f"Обработано {idx}/{total_videos} видео...")
                
        except Exception as e:
            print(f"Ошибка при обработке видео {video_data.get('id', 'unknown')}: {e}")
            await session.rollback()
            continue
    
    # Финальный коммит
    await session.commit()
    print(f"\nЗагрузка завершена!")
    print(f"Видео создано: {videos_created}")
    print(f"Снапшотов создано: {snapshots_created}")


async def main():
    """Основная функция"""
    json_file = os.getenv("JSON_FILE", "data/videos_data.json")
    
    if not os.path.exists(json_file):
        print(f"Файл {json_file} не найден!")
        print("Сначала запустите scripts/download_data.py для скачивания данных")
        return
    
    # Инициализация БД
    await init_db()
    print("База данных инициализирована")
    
    # Загрузка данных
    async with async_session_maker() as session:
        await load_videos_data(session, json_file)
    
    print("Готово!")


if __name__ == "__main__":
    asyncio.run(main())

