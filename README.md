# Telegram-бот для аналитики по видео

Telegram-бот, который принимает запросы на естественном русском языке и возвращает числовые ответы на основе данных о видео из базы данных PostgreSQL.

## Архитектура

Бот использует следующую архитектуру:

```
Пользователь → Telegram бот (aiogram) → Ollama LLM (NL→SQL) → PostgreSQL → Числовой ответ → Пользователь
```

### Компоненты:

1. **PostgreSQL** - база данных с таблицами `videos` и `video_snapshots`
2. **Ollama** - локальная LLM для преобразования естественного языка в SQL запросы
3. **aiogram** - асинхронный фреймворк для Telegram бота
4. **SQLAlchemy** - ORM для работы с базой данных

### Преобразование запросов в SQL

Бот использует Ollama (локальная LLM) для преобразования запросов на русском языке в SQL запросы. Промпт содержит:

- Подробное описание схемы базы данных (таблицы `videos` и `video_snapshots`)
- Примеры запросов на русском и соответствующие SQL запросы
- Инструкции по обработке дат в разных форматах
- Правила безопасности (только SELECT запросы)

Промпт находится в `src/llm/prompts.py` и автоматически формируется для каждого запроса пользователя.

## Структура проекта

```
LRT1/
├── README.md
├── pyproject.toml          # Зависимости Poetry
├── docker-compose.yml      # PostgreSQL в Docker
├── alembic/               # Миграции базы данных
│   ├── env.py
│   ├── versions/
│   └── script.py.mako
├── src/
│   ├── bot/              # Telegram бот
│   │   ├── main.py       # Точка входа бота
│   │   └── handlers.py   # Обработчики сообщений
│   ├── db/               # Работа с БД
│   │   ├── models.py     # SQLAlchemy модели
│   │   └── database.py   # Подключение к БД
│   ├── llm/              # LLM интеграция
│   │   ├── prompts.py    # Промпты для LLM
│   │   └── sql_generator.py  # Генерация SQL через Ollama
│   └── config.py         # Конфигурация
├── scripts/
│   ├── download_data.py  # Скачивание JSON с Google Drive
│   └── load_data.py      # Загрузка данных в БД
└── run_bot.py            # Скрипт запуска бота
```

## Установка и запуск

### Требования

- Python 3.10+
- Poetry (для управления зависимостями)
- Docker и Docker Compose (для PostgreSQL)
- Ollama (локальная LLM)

### Шаг 1: Установка зависимостей

```bash
# Установка Poetry (если еще не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# Клонирование репозитория
git clone https://github.com/Skvorcmen/RLT_test1.git
cd RLT_test1

# Установка зависимостей
poetry install
```

### Шаг 2: Установка и настройка Ollama

```bash
# Установка Ollama (macOS)
brew install ollama

# Или скачать с https://ollama.ai

# Загрузка модели (рекомендуется llama3.1:8b)
ollama pull llama3.1:8b

# Запуск Ollama сервера (в отдельном терминале)
ollama serve
```

Ollama будет доступен по адресу `http://localhost:11434` (по умолчанию).

### Шаг 3: Настройка базы данных

```bash
# Запуск PostgreSQL в Docker
docker-compose up -d

# Применение миграций
poetry run alembic upgrade head
```

### Шаг 4: Загрузка данных

```bash
# Активация виртуального окружения
poetry shell

# Скачивание JSON файла с Google Drive
python scripts/download_data.py

# Загрузка данных в базу
python scripts/load_data.py
```

### Шаг 5: Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` и укажите токен Telegram бота:

```env
TELEGRAM_BOT_TOKEN=8122457255:AAGbGQ9bb_w03PoGV5iXFsngxHxBoZG4hbM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/video_analytics
```

### Шаг 6: Запуск бота

```bash
# В активированном виртуальном окружении
poetry run python run_bot.py

# Или через Poetry напрямую
poetry run python run_bot.py
```

## Использование

После запуска бота отправьте ему сообщение в Telegram с вопросом на русском языке. Примеры:

- "Сколько всего видео есть в системе?"
- "Сколько видео у креатора с id '123' вышло с 1 ноября 2025 по 5 ноября 2025 включительно?"
- "Сколько видео набрало больше 100000 просмотров за всё время?"
- "На сколько просмотров в сумме выросли все видео 28 ноября 2025?"
- "Сколько разных видео получали новые просмотры 27 ноября 2025?"

Бот вернет одно число - ответ на ваш вопрос.

## Структура базы данных

### Таблица `videos`

Итоговая статистика по каждому видео:

- `id` - идентификатор видео
- `creator_id` - идентификатор креатора
- `video_created_at` - дата и время публикации видео
- `views_count` - финальное количество просмотров
- `likes_count` - финальное количество лайков
- `comments_count` - финальное количество комментариев
- `reports_count` - финальное количество жалоб
- `created_at`, `updated_at` - служебные поля

### Таблица `video_snapshots`

Почасовые замеры статистики по каждому видео:

- `id` - идентификатор снапшота
- `video_id` - ссылка на видео (FK к `videos.id`)
- `views_count`, `likes_count`, `comments_count`, `reports_count` - текущие значения на момент замера
- `delta_views_count`, `delta_likes_count`, `delta_comments_count`, `delta_reports_count` - приращения с прошлого замера
- `created_at` - время замера (раз в час)
- `updated_at` - служебное поле

## Технические детали

### Асинхронность

Все операции выполняются асинхронно:
- Запросы к базе данных через `asyncpg` и SQLAlchemy async
- Запросы к Ollama через `httpx` (асинхронный HTTP клиент)
- Telegram бот на `aiogram 3.x` (полностью асинхронный)

### Безопасность SQL

- Валидация: разрешены только SELECT запросы
- Парсинг SQL перед выполнением
- Обработка ошибок SQL

### Обработка дат

LLM автоматически преобразует русские даты в SQL формат:
- "28 ноября 2025" → `'2025-11-28'`
- "с 1 по 5 ноября 2025" → `>= '2025-11-01' AND <= '2025-11-05'`

## Проверка бота

После запуска бота проверьте его через служебного бота `@rlt_test_checker_bot`:

```
/check @yourbotnickname https://github.com/Skvorcmen/RLT_test1
```

Где `@yourbotnickname` - никнейм вашего Telegram-бота.

## Разработка

### Применение миграций

```bash
poetry run alembic upgrade head
```

### Создание новой миграции

```bash
poetry run alembic revision --autogenerate -m "Описание миграции"
```

### Запуск в режиме разработки

```bash
poetry shell
python run_bot.py
```

## Лицензия

Проект создан в рамках тестового задания.
