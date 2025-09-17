-- 2.1. Сумма заказов по клиентам
SELECT 
    c.name AS "Клиент",
    COALESCE(SUM(o.total_amount), 0) AS "Сумма"
FROM clients c
LEFT JOIN orders o ON c.id = o.client_id
GROUP BY c.id, c.name
ORDER BY "Сумма" DESC;

-- 2.2. Количество дочерних категорий
SELECT 
    parent.name AS "Категория",
    COUNT(child.id) AS "Дочерних"
FROM categories parent
LEFT JOIN categories child ON parent.id = child.parent_id
GROUP BY parent.id, parent.name
ORDER BY parent.name;

-- 2.3.1. Топ-5 товаров за месяц (с категорией 1-го уровня)
CREATE OR REPLACE VIEW top_5_products_last_month AS
WITH RECURSIVE category_hierarchy AS (
    SELECT id, name, parent_id, 0 as level
    FROM categories 
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT c.id, c.name, c.parent_id, ch.level + 1
    FROM categories c
    JOIN category_hierarchy ch ON c.parent_id = ch.id
),
root_categories AS (
    SELECT 
        child.id as category_id,
        parent.name as root_name
    FROM category_hierarchy child
    JOIN category_hierarchy parent ON (
        child.id = parent.id OR 
        (child.parent_id = parent.id AND parent.level = 0)
    )
    WHERE parent.level = 0
)
SELECT 
    n.name AS "Наименование товара",
    rc.root_name AS "Категория 1-го уровня",
    SUM(oi.quantity) AS "Общее количество проданных штук"
FROM order_items oi
JOIN nomenclature n ON oi.nomenclature_id = n.id
JOIN orders o ON oi.order_id = o.id
JOIN root_categories rc ON n.category_id = rc.category_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 month'
    AND o.status IN ('completed', 'processing')
GROUP BY n.id, n.name, rc.root_name
ORDER BY "Общее количество проданных штук" DESC
LIMIT 5;

SELECT * FROM top_5_products_last_month;

