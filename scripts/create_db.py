"""Скрипт для создания базы данных"""
import asyncio
import asyncpg

async def create_db():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/postgres')
    try:
        await conn.execute('CREATE DATABASE video_analytics')
        print('База данных video_analytics создана')
    except asyncpg.exceptions.DuplicateDatabaseError:
        print('База данных video_analytics уже существует')
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_db())

