from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud import customer as customer_crud
from app.schemas.schemas import CustomerCreate, Customer
from app.database import get_db

router = APIRouter()


@router.post("/", response_model=Customer)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)) -> Customer:
    return customer_crud.create_customer(db=db, customer=customer)


@router.get("/{customer_id}", response_model=Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)) -> Customer:
    db_customer = customer_crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

# Add other endpoint functions as needed
