# Orders Management System

Тестовое задание для позиции Middle Backend разработчика.

## Что это

Простая система для управления заказами с REST API. Позволяет добавлять товары в заказы, управлять категориями и клиентами.

## Что реализовано

- Схема БД с иерархией категорий (PostgreSQL)
- 3 SQL запроса по заданию
- REST API для добавления товаров в заказы
- Базовое кэширование и мониторинг
- Docker для запуска

## Как запустить

```bash
# Поднять все сервисы
docker-compose up -d

# Остановить
docker-compose down
```

## Что где смотреть

- http://localhost:8000/docs - документация API
- http://localhost:8080 - pgAdmin (admin@orders.com/admin)
- `sql_queries.sql` - SQL запросы из задания
- `database_schema.sql` - схема БД

## Тесты

```bash
python3 -m pytest test_api.py -v
```

14 тестов покрывают основную функциональность.
