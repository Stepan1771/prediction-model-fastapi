# 🩺 Prediction Model FastAPI

REST API сервис для предсказания диабета на основе ONNX ML-модели, построенный на **FastAPI**, **SQLAlchemy (async)** и **SQLite**.

---

## 📋 Содержание

- [Стек технологий](#-стек-технологий)
- [Архитектура проекта](#-архитектура-проекта)
- [Быстрый старт (Docker)](#-быстрый-старт-docker)
- [Локальный запуск](#-локальный-запуск)
- [Переменные окружения](#-переменные-окружения)
- [API эндпоинты](#-api-эндпоинты)
- [Аутентификация](#-аутентификация)
- [Тесты](#-тесты)
- [Makefile — все команды](#-makefile--все-команды)
- [Миграции Alembic](#-миграции-alembic)
- [Логи](#-логи)
- [Структура проекта](#-структура-проекта)

---

## 🛠 Стек технологий

| Категория | Технология |
|---|---|
| Фреймворк | [FastAPI](https://fastapi.tiangolo.com/) |
| ML инференс | [ONNX Runtime](https://onnxruntime.ai/) |
| База данных | SQLite + [SQLAlchemy](https://www.sqlalchemy.org/) (async) + [aiosqlite](https://github.com/omnilib/aiosqlite) |
| Миграции | [Alembic](https://alembic.sqlalchemy.org/) |
| Пароли | [Argon2](https://github.com/hynek/argon2-cffi) |
| Аутентификация | HTTP Basic Auth |
| Логирование | [Loguru](https://github.com/Delgan/loguru) |
| Сервер | [Uvicorn](https://www.uvicorn.org/) + uvloop |
| Пакетный менеджер | [uv](https://docs.astral.sh/uv/) |
| Тесты | pytest + pytest-asyncio + pytest-cov |
| Контейнеризация | Docker + Docker Compose |

---

## 🏗 Архитектура проекта

```
prediction-model-fastapi/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── uv.lock
├── .env
└── src/
    ├── main.py                  # точка входа, создание FastAPI приложения
    ├── alembic.ini              # конфиг Alembic
    ├── api/
    │   ├── api_v1/
    │   │   ├── auth.py          # эндпоинты /auth/register, /auth/me
    │   │   └── predict.py       # эндпоинт /predict/
    │   └── depends/             # FastAPI Depends-зависимости
    ├── core/
    │   ├── config.py            # настройки приложения (pydantic-settings)
    │   ├── database/            # движок SQLAlchemy, фабрика сессий
    │   ├── security/            # хэширование паролей, HTTPBasic
    │   ├── handlers.py          # обработчик AppException
    │   ├── lifespan.py          # startup/shutdown события
    │   └── logging.py           # настройка Loguru
    ├── exceptions/              # кастомные исключения
    ├── migrations/              # Alembic миграции
    ├── ml/
    │   └── diabetes_model.onnx  # обученная ONNX модель
    ├── models/                  # SQLAlchemy ORM модели
    ├── repositories/            # слой доступа к данным
    ├── schemas/                 # Pydantic схемы запросов/ответов
    ├── services/                # бизнес-логика (Auth, ML)
    ├── logs/                    # файлы логов (создаётся автоматически)
    └── tests/
        ├── conftest.py          # фикстуры pytest
        ├── test_auth.py         # тесты аутентификации
        ├── test_predict.py      # тесты предсказания
        ├── test_security.py     # тесты хэширования паролей
        └── test_services.py     # юнит-тесты сервисов
```

Приложение организовано по слоям:

```
HTTP Request → Router → Depends → Service → Repository → Database
                                ↓
                           ML Service → ONNX Model
```

---

## 🚀 Быстрый старт (Docker)

### Требования

- [Docker](https://www.docker.com/) 24+
- [Docker Compose](https://docs.docker.com/compose/) v2+

### Шаги

**1. Клонируйте репозиторий**

```bash
git clone https://github.com/Stepan1771/prediction-model-fastapi.git
cd prediction-model-fastapi
```

**2. Создайте файл `.env`** (или используйте готовый):

```bash
cp .env.example .env   # если есть, иначе создайте вручную — см. раздел ниже
```

**3. Запустите**

```bash
docker compose up -d
```

Docker Compose автоматически:
1. Соберёт образ приложения
2. Запустит контейнер `prediction-migrate` — применит Alembic миграции
3. Запустит контейнер `prediction-api` после успешных миграций

**4. Откройте Swagger UI**

```
http://localhost:8000/docs
```

**5. Остановка**

```bash
docker compose down --volumes
```

> **Примечание:** флаг `--volumes` удаляет БД. Без него — `docker compose down`.

---

## 💻 Локальный запуск

### Требования

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (`pip install uv` или через brew/scoop)

### Шаги

**1. Установите зависимости**

```bash
uv sync --group dev
```

**2. Создайте файл `.env`** в корне проекта:

```dotenv
APP_CONFIG__APP__SERVICE_NAME=predict-service
APP_CONFIG__APP__HOST=0.0.0.0
APP_CONFIG__APP__PORT=8000

APP_CONFIG__DB__URL=sqlite+aiosqlite:///./src/users.db
```

**3. Примените миграции**

```bash
cd src && uv run alembic upgrade head
```

или через Makefile:

```bash
make migrate
```

**4. Запустите сервер**

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

или через Makefile:

```bash
make run
```

**5. Откройте Swagger UI**

```
http://localhost:8000/docs
```

---

## ⚙️ Переменные окружения

Все переменные задаются в файле `.env` в корне проекта.  
Префикс `APP_CONFIG__` — разделитель вложенности `__`.

| Переменная | Описание | Пример |
|---|---|---|
| `APP_CONFIG__APP__SERVICE_NAME` | Название сервиса (отображается в Swagger) | `predict-service` |
| `APP_CONFIG__APP__HOST` | Хост для uvicorn | `0.0.0.0` |
| `APP_CONFIG__APP__PORT` | Порт для uvicorn | `8000` |
| `APP_CONFIG__DB__URL` | URL подключения к БД | `sqlite+aiosqlite:///./src/users.db` |

**URL для разных сред:**

```dotenv
# Локально
APP_CONFIG__DB__URL=sqlite+aiosqlite:///./src/users.db

# В Docker (задаётся через docker-compose.yml автоматически)
APP_CONFIG__DB__URL=sqlite+aiosqlite:////app/src/data/users.db
```

---

## 📡 API эндпоинты

Базовый URL: `http://localhost:8000/api/v1`

Интерактивная документация: [`/docs`](http://localhost:8000/docs) (Swagger UI)

### Auth

#### `POST /auth/register` — Регистрация пользователя

**Тело запроса:**
```json
{
  "username": "john",
  "password": "MySecret123!"
}
```

**Ответ `201 Created`:**
```json
{
  "message": "Пользователь успешно зарегистрирован",
  "user": "john"
}
```

**Возможные ошибки:**

| Статус | Код | Описание |
|---|---|---|
| `409` | `USERNAME_ALREADY_EXISTS` | Имя уже занято |
| `422` | — | Ошибка валидации |

---

#### `GET /auth/me` — Текущий пользователь

> 🔒 Требует аутентификации (HTTP Basic Auth)

**Ответ `200 OK`:**
```json
{
  "username": "john"
}
```

---

### Predict

#### `POST /predict/` — Предсказание диабета

> 🔒 Требует аутентификации (HTTP Basic Auth)

Модель принимает 4 признака и возвращает бинарное предсказание.

**Тело запроса:**
```json
{
  "Pregnancies": 6,
  "Glucose": 148,
  "BMI": 33.6,
  "Age": 50
}
```

| Поле | Тип | Описание |
|---|---|---|
| `Pregnancies` | `int` | Количество беременностей |
| `Glucose` | `float` | Уровень глюкозы в плазме |
| `BMI` | `float` | Индекс массы тела |
| `Age` | `int` | Возраст |

**Ответ `201 Created`:**
```json
{
  "prediction": 1
}
```

| Значение | Интерпретация |
|---|---|
| `0` | Диабет не выявлен |
| `1` | Диабет выявлен |

**Возможные ошибки:**

| Статус | Код | Описание |
|---|---|---|
| `401` | `AUTH_REQUIRED` | Не переданы учётные данные |
| `403` | `INVALID_CREDENTIALS` | Неверный логин или пароль |
| `422` | — | Ошибка валидации тела запроса |
| `500` | `MODEL_INFERENCE_ERROR` | Ошибка ML инференса |

---

## 🔐 Аутентификация

Сервис использует **HTTP Basic Authentication**.

### В Swagger UI

1. Откройте [`http://localhost:8000/docs`](http://localhost:8000/docs)
2. Зарегистрируйтесь через `POST /auth/register`
3. Нажмите кнопку **Authorize** (🔒) в правом верхнем углу
4. Введите `username` и `password`
5. Нажмите **Authorize** — теперь все защищённые запросы будут автоматически подписаны

### В curl / httpie

```bash
# curl
curl -u "john:MySecret123!" http://localhost:8000/api/v1/auth/me

# httpie
http -a john:MySecret123! GET http://localhost:8000/api/v1/auth/me
```

### В Python (httpx)

```python
import httpx

with httpx.Client(base_url="http://localhost:8000") as client:
    # Регистрация
    client.post("/api/v1/auth/register", json={
        "username": "john", "password": "MySecret123!"
    })

    # Запрос с авторизацией
    resp = client.post(
        "/api/v1/predict/",
        json={"Pregnancies": 6, "Glucose": 148, "BMI": 33.6, "Age": 50},
        auth=("john", "MySecret123!"),
    )
    print(resp.json())  # {"prediction": 1}
```

---

## 🧪 Тесты

### Запуск тестов

```bash
# Просто запустить
make test

# С отчётом покрытия в терминале + HTML
make test-cov

# XML отчёт (для CI/CD)
make test-cov-xml
```

Или напрямую через uv:

```bash
uv run pytest -v
uv run pytest -v --cov=src --cov-report=term-missing
```

### Структура тестов

```
src/tests/
├── conftest.py        # фикстуры: in-memory SQLite, async HTTP client, mock ML
├── test_auth.py       # тесты /register и /me (8 тестов)
├── test_predict.py    # тесты /predict/ (6 тестов)
├── test_security.py   # юнит-тесты hash_password / verify_password (7 тестов)
└── test_services.py   # юнит-тесты AuthService с mock-репозиторием (3 теста)
```

**Итого: 24 теста, покрытие ~89%**

### Особенности тестовой среды

- **База данных** — in-memory SQLite (`sqlite+aiosqlite:///:memory:`) с `StaticPool`, изолированная для каждого теста
- **ML-сервис** — заменяется `MockMLService` (всегда возвращает `1`), ONNX модель не загружается
- **HTTP клиент** — `httpx.AsyncClient` с `ASGITransport` (без реального TCP)

### HTML отчёт покрытия

После `make test-cov` отчёт доступен в браузере:

```
src/coverage_html/index.html
```

---

## 🐳 Docker

### Контейнеры

| Контейнер | Роль | Поведение |
|---|---|---|
| `prediction-migrate` | Применяет Alembic миграции | Запускается один раз, завершается |
| `prediction-api` | Основной API сервер | Запускается после успешных миграций |

### Volumes

| Volume / Mount | Назначение |
|---|---|
| `db_data` → `/app/src/data` | Именованный volume для SQLite БД |
| `./src/logs` → `/app/src/logs` | Bind-mount для лог-файлов |

### Полезные команды

```bash
# Сборка образов (с нуля)
make docker-build

# Запуск в фоне
make docker-up

# Остановка и удаление контейнеров + volumes
make docker-down

# Полный перезапуск (down → build → up)
make docker-restart

# Просмотр логов всех контейнеров
make docker-logs

# Логи только API контейнера
make docker-logs-app

# Статус контейнеров
make docker-ps
```

---

## 📦 Makefile — все команды

```bash
make help              # Показать список всех команд
```

| Команда | Описание |
|---|---|
| `make install` | Установить все зависимости включая dev (`uv sync --group dev`) |
| `make run` | Запустить приложение локально с hot-reload |
| `make migrate` | Применить Alembic миграции локально |
| `make migrate-create name=<имя>` | Создать новую миграцию автогенерацией |
| `make test` | Запустить тесты |
| `make test-cov` | Тесты + покрытие (терминал + HTML) |
| `make test-cov-xml` | Тесты + покрытие (XML для CI) |
| `make docker-build` | Собрать Docker образы без кэша |
| `make docker-up` | Запустить контейнеры в фоне |
| `make docker-down` | Остановить контейнеры и удалить volumes |
| `make docker-restart` | Пересобрать и перезапустить всё |
| `make docker-logs` | Следить за логами всех контейнеров |
| `make docker-logs-app` | Следить за логами API контейнера |
| `make docker-ps` | Показать статус контейнеров |

---

## 🗄 Миграции Alembic

Конфигурация Alembic находится в `src/alembic.ini`, миграции — в `src/migrations/versions/`.

### Применить миграции

```bash
# Локально
make migrate

# Вручную
cd src && uv run alembic upgrade head
```

### Создать новую миграцию

```bash
make migrate-create name=add_email_to_users
```

Или вручную:

```bash
cd src && uv run alembic revision --autogenerate -m "add_email_to_users"
```

### Откат миграции

```bash
cd src && uv run alembic downgrade -1       # откат на 1 версию назад
cd src && uv run alembic downgrade base     # откат к начальному состоянию
```

### История миграций

```bash
cd src && uv run alembic history --verbose
cd src && uv run alembic current
```

---

## 📝 Логи

Логи пишутся одновременно в **stdout** и в файл.

| Место | Путь |
|---|---|
| Консоль | stdout (цветной вывод) |
| Файл | `src/logs/app.log` |

Настройки ротации: 500 MB на файл, хранение 10 дней, сжатие в zip.

**В Docker** лог-файл доступен локально через bind-mount:

```
./src/logs/app.log
```

---

## 🔧 Разработка

### Добавление зависимости

```bash
uv add <package>            # production
uv add --dev <package>      # development only
```

### Структура зависимостей

```toml
# pyproject.toml

[project]
dependencies = [...]         # production

[dependency-groups]
dev = [...]                  # только для разработки и тестов
```

---

## 📌 Требования к системе

| Инструмент | Минимальная версия |
|---|---|
| Python | 3.13 |
| uv | последняя |
| Docker | 24.0 |
| Docker Compose | v2.0 |
| GNU Make | 3.81 (опционально) |

