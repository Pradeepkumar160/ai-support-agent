#!/usr/bin/env python3
"""
Run once to create DB tables and seed sample data.
Usage:  python scripts/init_db.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine, Base, SessionLocal
from app.models.all_models import Customer, Order, Ticket


def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    with SessionLocal() as session:
        if session.query(Customer).count() == 0:
            print("Seeding sample data...")

            customers = [
                Customer(name="Alice Smith", email="alice@example.com"),
                Customer(name="Bob Jones", email="bob@example.com"),
            ]
            session.add_all(customers)

            orders = [
                Order(id=101, status="SHIPPED", item_name="Wireless Headphones", customer_email="alice@example.com"),
                Order(id=102, status="PROCESSING", item_name="Mechanical Keyboard", customer_email="alice@example.com"),
                Order(id=103, status="DELIVERED", item_name="USB-C Hub", customer_email="bob@example.com"),
                Order(id=104, status="CANCELLED", item_name="Laptop Stand", customer_email="bob@example.com"),
            ]
            session.add_all(orders)
            session.commit()
            print("Seeding complete. Orders: 101, 102, 103, 104")
        else:
            print("Data already exists — skipping seed.")


if __name__ == "__main__":
    init_db()
