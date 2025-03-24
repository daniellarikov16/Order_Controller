from sqlalchemy.orm import Session
from models import Order

class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def get_pending_orders_by_email(self, email: str):
        return self.db.query(Order).filter(Order.email == email).filter(Order.status == "Pending").all()

    def get_processed_orders_by_email(self, email: str):
        return self.db.query(Order).filter(Order.email == email).filter(Order.status == "Processed").all()

    def get_order_by_id(self, order_id: int):
        return self.db.query(Order).filter(Order.id == order_id).first()

    def append_new_order(self, email: str, description: str, status: str = "Pending"):
        new_order = Order(
            email = email,
            status = status,
            description = description
        )
        self.db.add(new_order)
        self.db.commit()
        self.db.refresh(new_order)

        return new_order

    def update_order_status(self, order_id: int, status: str):
        order = self.get_order_by_id(order_id)
        if order:
            order.status = status
            self.db.commit()
            return order
        return None

    def delete_processed_orders_by_email(self, email: str):
        orders = self.get_processed_orders_by_email(email)
        for order in orders:
            self.db.delete(order)
        self.db.commit()