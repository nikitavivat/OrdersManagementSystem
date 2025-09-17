from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from config import settings

engine = create_engine(settings.database_url, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    parent = relationship("Category", remote_side=[id], backref="children")
    nomenclature = relationship("Nomenclature", back_populates="category")

class Nomenclature(Base):
    __tablename__ = "nomenclature"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("Category", back_populates="nomenclature")
    order_items = relationship("OrderItem", back_populates="nomenclature")

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = relationship("Order", back_populates="client")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('pending', 'processing', 'completed', 'cancelled', name='order_status'), default='pending')
    total_amount = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = relationship("Client", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    nomenclature_id = Column(Integer, ForeignKey("nomenclature.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    order = relationship("Order", back_populates="order_items")
    nomenclature = relationship("Nomenclature", back_populates="order_items")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
