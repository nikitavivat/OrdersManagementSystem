# Orders Management System

## Описание

Система управления заказами с REST API.

## Технологии

- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker

## Запуск

```bash
docker-compose up -d
```

## API

- http://localhost:8000/docs - документация
- http://localhost:8080 - pgAdmin (admin@orders.com/admin)

## Тестирование

```bash
python3 -m pytest test_api.py -v
```
