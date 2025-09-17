from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_
from decimal import Decimal
from typing import Union
import logging
import traceback
import time

from database import get_db, Order, OrderItem, Nomenclature, Client, Category
from models import (
    AddItemToOrderRequest, 
    AddItemToOrderResponse, 
    ErrorResponse,
    OrderInfo,
    OrderItemInfo,
    NomenclatureInfo
)
from cache_service import cache_service
from metrics_service import metrics_service
from config import settings

# Запускам логгер
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Test Task API",
    version="1.0.0",
    description="API для управления заказами"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для логирования запросов и метрик
@app.middleware("http")
async def log_requests_and_metrics(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # Логирование
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    # Метрики
    metrics_service.record_request(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        duration=process_time
    )
    
    return response

@app.get("/")
async def root():
    return {"message": "API работает"}

@app.get("/health")
async def health():
    """Базовый health check"""
    return {"status": "ok"}

@app.get("/health/detailed")
async def health_detailed():
    """Детальный health check с метриками"""
    health_status = metrics_service.get_health_status()
    cache_stats = cache_service.get_cache_stats()
    
    return {
        **health_status,
        "cache": cache_stats,
        "version": "1.0.0"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus метрики"""
    return Response(
        content=metrics_service.get_metrics(),
        media_type="text/plain"
    )

@app.get("/cache/stats")
async def cache_stats():
    """Статистика кэша"""
    return cache_service.get_cache_stats()

@app.post("/cache/clear")
async def clear_cache():
    """Очистка кэша"""
    cache_service._cache.clear()
    logger.info("Cache cleared manually")
    return {"message": "Cache cleared successfully"}

@app.post("/orders/{order_id}/items", response_model=AddItemToOrderResponse)
async def add_item_to_order(
    order_id: int,
    request: AddItemToOrderRequest,
    db: Session = Depends(get_db)
):
    """
    Добавляет товар в заказ.
    Если товар уже есть в заказе, увеличивает его количество.
    """
    try:
        logger.info(f"Добавление товара {request.nomenclature_id} в заказ {order_id}, количество: {request.quantity}")
        
        # Проверяем существование заказа
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.warning(f"Заказ {order_id} не найден")
            raise HTTPException(status_code=404, detail=f"Заказ {order_id} не найден")
        
        # Проверяем существование товара
        nomenclature = db.query(Nomenclature).filter(
            Nomenclature.id == request.nomenclature_id
        ).first()
        if not nomenclature:
            logger.warning(f"Товар {request.nomenclature_id} не найден")
            raise HTTPException(status_code=404, detail=f"Товар {request.nomenclature_id} не найден")
        
        # Проверяем наличие товара на складе
        if nomenclature.quantity < request.quantity:
            logger.warning(f"Недостаточно товара {request.nomenclature_id}. Доступно: {nomenclature.quantity}, запрошено: {request.quantity}")
            raise HTTPException(
                status_code=400, 
                detail=f"Недостаточно товара на складе. Доступно: {nomenclature.quantity}, запрошено: {request.quantity}"
            )
        
        # Проверяем, есть ли уже такой товар в заказе
        existing_item = db.query(OrderItem).filter(
            and_(
                OrderItem.order_id == order_id,
                OrderItem.nomenclature_id == request.nomenclature_id
            )
        ).first()
        
        if existing_item:
            # Увеличиваем количество существующего товара
            existing_item.quantity += request.quantity
            existing_item.price = nomenclature.price
            order.total_amount += nomenclature.price * request.quantity
            
            logger.info(f"Увеличено количество товара {request.nomenclature_id} в заказе {order_id}")
        else:
            # Создаем новую позицию в заказе
            new_item = OrderItem(
                order_id=order_id,
                nomenclature_id=request.nomenclature_id,
                quantity=request.quantity,
                price=nomenclature.price
            )
            
            db.add(new_item)
            order.total_amount += nomenclature.price * request.quantity
            
            logger.info(f"Добавлен новый товар {request.nomenclature_id} в заказ {order_id}")
        
        db.commit()
        
        # Инвалидируем кэш после изменений
        await cache_service.delete_pattern(f"order_full:order_id:{order_id}")
        
        # Записываем метрики
        metrics_service.record_database_query("update", "orders")
        metrics_service.record_database_query("insert", "order_items")
        
        if existing_item:
            db.refresh(existing_item)
            return AddItemToOrderResponse(
                success=True,
                message=f"Количество товара '{nomenclature.name}' увеличено",
                order_item_id=existing_item.id,
                total_quantity=existing_item.quantity
            )
        else:
            db.refresh(new_item)
            return AddItemToOrderResponse(
                success=True,
                message=f"Товар '{nomenclature.name}' добавлен в заказ",
                order_item_id=new_item.id,
                total_quantity=new_item.quantity
            )
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Неожиданная ошибка при добавлении товара в заказ: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/orders/{order_id}", response_model=OrderInfo)
async def get_order_info(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Получает информацию о заказе с его позициями"""
    try:
        # Кэшируем полную информацию о заказе
        cache_key = cache_service._generate_key("order_full", order_id=order_id)
        
        async def fetch_order_info():
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return None
            
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            
            items_info = []
            for item in order_items:
                nomenclature = db.query(Nomenclature).filter(
                    Nomenclature.id == item.nomenclature_id
                ).first()
                
                items_info.append(OrderItemInfo(
                    id=item.id,
                    nomenclature_id=item.nomenclature_id,
                    nomenclature_name=nomenclature.name if nomenclature else "Неизвестный товар",
                    quantity=item.quantity,
                    price=item.price,
                    total_price=item.price * item.quantity
                ))
            
            return OrderInfo(
                id=order.id,
                client_id=order.client_id,
                client_name=order.client.name if order.client else "Неизвестный клиент",
                order_date=order.order_date,
                status=order.status,
                total_amount=order.total_amount,
                items=items_info
            )
        
        order_info = await cache_service.get_or_set(
            cache_key,
            fetch_order_info,
            ttl=settings.CACHE_TTL_ORDERS
        )
        
        if not order_info:
            raise HTTPException(status_code=404, detail=f"Заказ {order_id} не найден")
        
        return order_info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении информации о заказе {order_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/nomenclature/{nomenclature_id}", response_model=NomenclatureInfo)
async def get_nomenclature_info(
    nomenclature_id: int,
    db: Session = Depends(get_db)
):
    """Получает информацию о товаре"""
    try:
        # Кэшируем информацию о товаре
        cache_key = cache_service._generate_key("nomenclature_full", nomenclature_id=nomenclature_id)
        
        async def fetch_nomenclature_info():
            nomenclature = db.query(Nomenclature).filter(
                Nomenclature.id == nomenclature_id
            ).first()
            
            if not nomenclature:
                return None
            
            category = db.query(Category).filter(
                Category.id == nomenclature.category_id
            ).first()
            
            return NomenclatureInfo(
                id=nomenclature.id,
                name=nomenclature.name,
                quantity=nomenclature.quantity,
                price=nomenclature.price,
                category_id=nomenclature.category_id,
                category_name=category.name if category else "Без категории"
            )
        
        nomenclature_info = await cache_service.get_or_set(
            cache_key,
            fetch_nomenclature_info,
            ttl=settings.CACHE_TTL_NOMENCLATURE
        )
        
        if not nomenclature_info:
            raise HTTPException(status_code=404, detail=f"Товар {nomenclature_id} не найден")
        
        return nomenclature_info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении информации о товаре {nomenclature_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
