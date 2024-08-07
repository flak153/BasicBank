from sqlalchemy.orm import Session
from app.models.models import Customer
from app.schemas.schemas import CustomerCreate


def create_customer(db: Session, customer: CustomerCreate) -> Customer:
    db_customer = Customer(name=customer.name)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def get_customer(db: Session, customer_id: int) -> Customer:
    return db.query(Customer).filter(Customer.id == customer_id).first()

# Add other CRUD operations as needed
