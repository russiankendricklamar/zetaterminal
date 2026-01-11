# Backend API для вычислительных задач

Бэкенд сервис для обработки вычислительных задач финансового дашборда.

## Структура проекта

```
backend/
├── src/
│   ├── api/          # API endpoints
│   ├── services/     # Бизнес-логика и вычисления
│   ├── models/       # Модели данных
│   └── utils/        # Вспомогательные утилиты
├── requirements.txt  # Зависимости Python
├── .env.example      # Пример конфигурации
└── README.md         # Документация
```

## Установка

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# На macOS/Linux:
source venv/bin/activate
# На Windows:
# venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

## Запуск

```bash
# Запуск сервера разработки
uvicorn src.main:app --reload --port 8000
```

## API Endpoints

API будет доступно по адресу: `http://localhost:8000`

Документация API (Swagger): `http://localhost:8000/docs`
