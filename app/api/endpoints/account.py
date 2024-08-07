from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud import account as account_crud
from app.schemas.schemas import AccountCreate, Account
from app.database import get_db
from typing import Dict

router = APIRouter()


@router.post("/", response_model=Account)
def create_account(account: AccountCreate, db: Session = Depends(get_db)) -> Account:
    return account_crud.create_account(db=db, account=account)


@router.get("/{account_id}", response_model=Account)
def read_account(account_id: int, db: Session = Depends(get_db)) -> Account:
    db_account = account_crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account


@router.get("/{account_id}/balance", response_model=Dict[str, float])
def get_account_balance(account_id: int, db: Session = Depends(get_db)) -> Dict[str, float]:
    balance = account_crud.get_account_balance(db, account_id=account_id)
    if balance is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"balance": float(balance)}

# Add other endpoint functions as needed
