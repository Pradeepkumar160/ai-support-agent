from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(100), nullable=False, default="PROCESSING")
    item_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="OPEN")
    customer_email = Column(String(255), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
