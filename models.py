from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import datetime
from typing import Optional, List

class AddItemToOrderRequest(BaseModel):
    order_id: int = Field(..., gt=0, description="ID заказа")
    nomenclature_id: int = Field(..., gt=0, description="ID товара")
    quantity: int = Field(..., gt=0, description="Количество товара")
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Количество должно быть больше 0')
        return v

class AddItemToOrderResponse(BaseModel):
    success: bool
    message: str
    order_item_id: Optional[int] = None
    total_quantity: Optional[int] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: str

class OrderItemInfo(BaseModel):
    id: int
    nomenclature_id: int
    nomenclature_name: str
    quantity: int
    price: Decimal
    total_price: Decimal

class OrderInfo(BaseModel):
    id: int
    client_id: int
    client_name: str
    order_date: datetime
    status: str
    total_amount: Decimal
    items: List[OrderItemInfo] = []

class NomenclatureInfo(BaseModel):
    id: int
    name: str
    quantity: int
    price: Decimal
    category_id: int
    category_name: str
