#!/usr/bin/env python3
"""
Скрипт для запуска Telegram бота
"""
from src.bot.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())

