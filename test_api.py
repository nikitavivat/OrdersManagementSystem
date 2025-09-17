import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db, Order, OrderItem, Nomenclature, Client, Category
from decimal import Decimal

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_test_data():
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    category = Category(name="Категория1")
    db.add(category)
    db.commit()
    db.refresh(category)
    
    nomenclature = Nomenclature(
        name="Товар1",
        quantity=100,
        price=Decimal("1000.00"),
        category_id=category.id
    )
    db.add(nomenclature)
    db.commit()
    db.refresh(nomenclature)
    
    client_obj = Client(name="Клиент1", address="Город1, Улица1, 1")
    db.add(client_obj)
    db.commit()
    db.refresh(client_obj)
    
    order = Order(
        client_id=client_obj.id,
        total_amount=Decimal("0.00")
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    yield {
        "category": category,
        "nomenclature": nomenclature,
        "client": client_obj,
        "order": order
    }
    
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "API работает"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_add_item_to_order_success(setup_test_data):
    test_data = setup_test_data
    
    response = client.post(
        f"/orders/{test_data['order'].id}/items",
        json={
            "order_id": test_data['order'].id,
            "nomenclature_id": test_data['nomenclature'].id,
            "quantity": 5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "добавлен" in data["message"]
    assert data["order_item_id"] is not None
    assert data["total_quantity"] == 5

def test_add_item_to_order_insufficient_stock(setup_test_data):
    test_data = setup_test_data
    
    response = client.post(
        f"/orders/{test_data['order'].id}/items",
        json={
            "order_id": test_data['order'].id,
            "nomenclature_id": test_data['nomenclature'].id,
            "quantity": 150
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Недостаточно товара" in data["detail"]

def test_add_item_to_order_nonexistent_order(setup_test_data):
    test_data = setup_test_data
    
    response = client.post(
        "/orders/999/items",
        json={
            "order_id": 999,
            "nomenclature_id": test_data['nomenclature'].id,
            "quantity": 5
        }
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "не найден" in data["detail"]

def test_add_item_to_order_nonexistent_nomenclature(setup_test_data):
    test_data = setup_test_data
    
    response = client.post(
        f"/orders/{test_data['order'].id}/items",
        json={
            "order_id": test_data['order'].id,
            "nomenclature_id": 999,
            "quantity": 5
        }
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "не найден" in data["detail"]

def test_add_existing_item_increases_quantity(setup_test_data):
    test_data = setup_test_data
    
    response1 = client.post(
        f"/orders/{test_data['order'].id}/items",
        json={
            "order_id": test_data['order'].id,
            "nomenclature_id": test_data['nomenclature'].id,
            "quantity": 3
        }
    )
    
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["success"] is True
    assert data1["total_quantity"] == 3
    
    response2 = client.post(
        f"/orders/{test_data['order'].id}/items",
        json={
            "order_id": test_data['order'].id,
            "nomenclature_id": test_data['nomenclature'].id,
            "quantity": 2
        }
    )
    
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["success"] is True
    assert "увеличено" in data2["message"]
    assert data2["total_quantity"] == 5

def test_get_order_info(setup_test_data):
    test_data = setup_test_data
    
    client.post(
        f"/orders/{test_data['order'].id}/items",
        json={
            "order_id": test_data['order'].id,
            "nomenclature_id": test_data['nomenclature'].id,
            "quantity": 2
        }
    )
    
    response = client.get(f"/orders/{test_data['order'].id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_data['order'].id
    assert data["client_id"] == test_data['client'].id
    assert data["client_name"] == test_data['client'].name
    assert len(data["items"]) == 1
    assert data["items"][0]["nomenclature_name"] == test_data['nomenclature'].name
    assert data["items"][0]["quantity"] == 2

def test_get_nomenclature_info(setup_test_data):
    test_data = setup_test_data
    
    response = client.get(f"/nomenclature/{test_data['nomenclature'].id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_data['nomenclature'].id
    assert data["name"] == test_data['nomenclature'].name
    assert data["quantity"] == test_data['nomenclature'].quantity
    assert data["category_name"] == test_data['category'].name

def test_validation_errors(setup_test_data):
    test_data = setup_test_data
    
    # Тест с отрицательным количеством
    response = client.post(
        f"/orders/{test_data['order'].id}/items",
        json={
            "order_id": test_data['order'].id,
            "nomenclature_id": test_data['nomenclature'].id,
            "quantity": -1
        }
    )
    
    assert response.status_code == 422  # Validation error
    
    # Тест с нулевым количеством
    response = client.post(
        f"/orders/{test_data['order'].id}/items",
        json={
            "order_id": test_data['order'].id,
            "nomenclature_id": test_data['nomenclature'].id,
            "quantity": 0
        }
    )
    
    assert response.status_code == 422  # Validation error
    
    # Тест с некорректным order_id
    response = client.post(
        f"/orders/{test_data['order'].id}/items",
        json={
            "order_id": -1,
            "nomenclature_id": test_data['nomenclature'].id,
            "quantity": 5
        }
    )
    
    assert response.status_code == 422  # Validation error

def test_health_detailed():
    """Тест детального health check"""
    response = client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data
    assert "cache" in data
    assert "version" in data

def test_metrics():
    """Тест метрик Prometheus"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    content = response.text
    assert "http_requests_total" in content

def test_cache_stats():
    """Тест статистики кэша"""
    response = client.get("/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_keys" in data
    assert "active_keys" in data
    assert "memory_usage_mb" in data

def test_clear_cache():
    """Тест очистки кэша"""
    response = client.post("/cache/clear")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Cache cleared successfully"
