# Система заказов

Простая система для управления заказами и товарами.

## Описание

Система включает:
- Управление товарами и категориями
- Создание заказов
- REST API для работы с данными

## Технологии

- FastAPI
- PostgreSQL
- SQLAlchemy
- Redis
- Docker

## Запуск

```bash
# Запуск системы
./scripts/start.sh

# Остановка
./scripts/stop.sh
```

## API

- http://localhost:8000 - API
- http://localhost:8000/docs - документация
- http://localhost:8080 - pgAdmin (admin@orders.com/admin)

## Тестирование

```bash
./scripts/test.sh
```
