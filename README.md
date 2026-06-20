# Developer Landing API

FastAPI backend для лендинга разработчика: приём заявок с контактной формы, AI-анализ тональности, email-уведомления, метрики.

---

## 1. О проекте

REST API сервис для лендинга разработчика-фрилансера. Принимает заявки с формы обратной связи, валидирует данные, анализирует текст через AI и отправляет уведомления на email — владельцу с AI-анализом и пользователю с подтверждением.

**Ключевые возможности:**

- Валидация входных данных с читаемыми сообщениями об ошибках на русском
- Rate limiting по IP: 5 запросов в час, персистентное хранение в JSON
- AI-анализ тональности и типа обращения через OpenRouter (mistral-7b-instruct)
- Graceful degradation: сервис работает без SMTP и без AI-ключа
- Логирование каждого запроса в файл с timestamp, IP, email и статусом
- Накопительные метрики по дням

---

## 2. Стек технологий

| Компонент       | Технология                          |
|-----------------|-------------------------------------|
| Framework       | FastAPI 0.111                       |
| Runtime         | Python 3.11                         |
| Валидация       | Pydantic v2                         |
| Настройки       | pydantic-settings                   |
| HTTP client     | httpx (async)                       |
| AI              | OpenRouter API / mistral-7b-instruct|
| Email           | smtplib SMTP_SSL                    |
| Контейнер       | Docker + docker-compose             |
| Документация    | Swagger UI (встроен в FastAPI)      |

---

## 3. Структура проекта

```
developer-landing-api/
├── app/
│   ├── main.py                  # FastAPI app, CORS, error handlers
│   ├── config.py                # Настройки через pydantic-settings + .env
│   ├── routers/
│   │   ├── contact.py           # POST /api/contact
│   │   ├── health.py            # GET /api/health
│   │   └── metrics.py           # GET /api/metrics
│   ├── services/
│   │   ├── contact_service.py   # Оркестрация: rate limit → AI → email → log
│   │   ├── ai_service.py        # Анализ тональности через OpenRouter
│   │   └── metrics_service.py   # Чтение/запись data/metrics.json
│   ├── handlers/
│   │   ├── email_handler.py     # SMTP_SSL отправка, 2 письма
│   │   ├── logging_handler.py   # Запись в logs/requests.log
│   │   └── rate_limit_handler.py # 5 req/h per IP, data/rate_limits.json
│   └── models/
│       └── contact.py           # Pydantic схемы запроса и ответа
├── logs/                        # Файлы логов (в .gitignore)
├── data/                        # JSON-хранилище метрик и rate limits (в .gitignore)
├── .env.example                 # Шаблон переменных окружения
├── postman_collection.json      # Postman коллекция с примерами запросов
├── Dockerfile
└── docker-compose.yml
```

---

## 4. Установка и запуск

### Локально

```bash
git clone <repo-url>
cd developer-landing-api

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Заполните .env своими данными

uvicorn app.main:app --reload
```

Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### Через Docker

```bash
cp .env.example .env
# Заполните .env

docker-compose up --build
```

### Переменные окружения (.env)

| Переменная          | Описание                                  | Обязательная |
|---------------------|-------------------------------------------|--------------|
| `SMTP_HOST`         | SMTP-сервер (smtp.gmail.com)              | Для email    |
| `SMTP_PORT`         | Порт (465 для SSL)                        | Для email    |
| `SMTP_USER`         | Email-адрес отправителя                   | Для email    |
| `SMTP_PASSWORD`     | Пароль / App Password                     | Для email    |
| `OWNER_EMAIL`       | Куда приходят уведомления о заявках       | Для email    |
| `OPENROUTER_API_KEY`| Ключ OpenRouter для AI-анализа           | Для AI       |

> Если `SMTP_*` не заданы — сервис принимает заявки и логирует, но письма не отправляет (200 OK).  
> Если `OPENROUTER_API_KEY` не задан — в письме пишется "AI analysis unavailable".

---

## 5. API — эндпоинты

### POST /api/contact

Приём заявки с лендинга.

**Тело запроса:**
```json
{
  "name": "Иван Иванов",
  "phone": "+79991234567",
  "email": "ivan@example.com",
  "comment": "Хочу обсудить разработку проекта"
}
```

**Валидация:**
- `name`: 2–50 символов
- `phone`: regex `^\+?[1-9]\d{6,14}$` (пробелы, тире, скобки допустимы)
- `email`: валидный email
- `comment`: 10–500 символов

**Ответы:**

| Код | Описание |
|-----|----------|
| 200 | Заявка принята |
| 422 | Ошибки валидации по полям |
| 429 | Rate limit превышен, `retry_after` — секунд до сброса |
| 500 | Internal server error |

### GET /api/health

```json
{ "status": "ok", "uptime_seconds": 3842.17 }
```

### GET /api/metrics

```json
{
  "total": 42,
  "successful": 38,
  "rate_limited": 4,
  "by_day": {
    "2026-06-20": { "total": 12, "successful": 10, "rate_limited": 2 }
  }
}
```

Полная интерактивная документация: `/docs` (Swagger UI), `/redoc` (ReDoc).

---

## 6. Деплой на Railway

**Live API:** https://developer-landing-api-production.up.railway.app  
**Swagger UI:** https://developer-landing-api-production.up.railway.app/docs

[Railway](https://railway.app) — PaaS-платформа с поддержкой Docker. Бесплатный tier включает 500 часов в месяц.

### Через GitHub (рекомендуется)

1. Пушите репозиторий на GitHub
2. Зайдите на [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Выберите репозиторий — Railway автоматически обнаружит `Dockerfile`
4. Перейдите в **Variables** и добавьте все переменные из `.env.example`
5. Railway сам деплоит при каждом пуше в `main`

### Через CLI

```bash
npm install -g @railway/cli
railway login
railway init        # привязать проект
railway up          # задеплоить
railway variables set SMTP_USER=your@gmail.com
railway variables set SMTP_PASSWORD=your_password
# ... остальные переменные
```

### Получить URL

После деплоя: **Settings → Networking → Generate Domain** — Railway выдаст публичный HTTPS URL.

### Персистентность данных

`logs/` и `data/` сбрасываются при каждом редеплое. Для продакшена замените JSON-хранилище на Railway PostgreSQL (добавить как отдельный сервис в проекте) или Redis.

---

## 7. Что сделано с помощью AI

Для генерации структуры проекта и boilerplate-кода использовался **Claude Code** (Anthropic).

AI помог с:
- Скаффолдингом слоистой архитектуры (routers → services → handlers)
- Шаблонами Pydantic-моделей и обработчиков ошибок
- Структурой Postman-коллекции и этого README

Весь сгенерированный код проверялся вручную: логика валидации, поведение rate limiter при сбросе окна, fallback в email_handler и ai_service, корректность async/await в цепочке contact_service → роутер. Финальный код соответствует тому, как я пишу сам — без избыточных абстракций и комментариев.
