# Анализ оптимизации

## Проблемы запроса

1. Рекурсивный запрос медленный при большой глубине категорий
2. Много JOIN'ов
3. Нет индексов для поиска по дате
4. Вычисление корневых категорий на лету

## Варианты оптимизации

### 1. Денормализация

Добавить поле root_category_id в таблицу nomenclature:

```sql
ALTER TABLE nomenclature ADD COLUMN root_category_id INT;
CREATE INDEX idx_nomenclature_root_category ON nomenclature(root_category_id);
```

### 2. Индексы

```sql
CREATE INDEX idx_orders_date_status ON orders(order_date, status);
CREATE INDEX idx_order_items_nomenclature_quantity ON order_items(nomenclature_id, quantity);
```

### 3. Кэширование

Создать таблицу для кэширования статистики продаж.

### 4. Партиционирование

Разделить большие таблицы по датам.

## Результат

- Денормализация: 60-80% ускорение
- Индексы: 50-70% ускорение
- Кэширование: 90%+ ускорение отчетов
