-- PostgreSQL схема для системы заказов

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_name ON categories(name);

CREATE TABLE nomenclature (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    price DECIMAL(10, 2) NOT NULL,
    category_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

CREATE INDEX idx_nomenclature_category_id ON nomenclature(category_id);
CREATE INDEX idx_nomenclature_name ON nomenclature(name);
CREATE INDEX idx_nomenclature_quantity ON nomenclature(quantity);

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_clients_name ON clients(name);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE RESTRICT
);

CREATE INDEX idx_orders_client_id ON orders(client_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    nomenclature_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (nomenclature_id) REFERENCES nomenclature(id) ON DELETE RESTRICT
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_nomenclature_id ON order_items(nomenclature_id);

-- Триггер для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_nomenclature_updated_at BEFORE UPDATE ON nomenclature
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Тестовые данные (сгенерированы для демонстрации функциональности)
INSERT INTO categories (name, parent_id) VALUES
('Категория1', NULL),
('Категория2', 1),
('Категория3', 2),
('Категория4', 1),
('Категория5', NULL),
('Категория6', 5),
('Категория7', 5);

INSERT INTO nomenclature (name, quantity, price, category_id) VALUES
('Товар1', 100, 1000.00, 3),
('Товар2', 50, 2000.00, 4),
('Товар3', 75, 1500.00, 3),
('Товар4', 25, 3000.00, 4),
('Товар5', 200, 500.00, 6),
('Товар6', 150, 800.00, 7);

INSERT INTO clients (name, address) VALUES
('Клиент1', 'Город1, Улица1, 1'),
('Клиент2', 'Город2, Улица2, 2'),
('Клиент3', 'Город3, Улица3, 3');

INSERT INTO orders (client_id, status, total_amount) VALUES
(1, 'completed', 1000.00),
(2, 'processing', 2000.00),
(3, 'pending', 0.00);

INSERT INTO order_items (order_id, nomenclature_id, quantity, price) VALUES
(1, 1, 1, 1000.00),
(2, 2, 1, 2000.00);