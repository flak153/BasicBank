from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud import transfer as transfer_crud
from app.schemas.schemas import TransferCreate, Transfer
from app.database import get_db
from typing import List
from uuid import UUID

router = APIRouter()


@router.post("/", response_model=Transfer)
def create_transfer(transfer: TransferCreate, db: Session = Depends(get_db)) -> Transfer:
    return transfer_crud.create_transfer(db=db, transfer=transfer)


@router.get("/{transfer_id}", response_model=Transfer)
def read_transfer(transfer_id: int, db: Session = Depends(get_db)) -> Transfer:
    db_transfer = transfer_crud.get_transfer(db, transfer_id=transfer_id)
    if db_transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return db_transfer


@router.get("/account/{account_id}", response_model=List[Transfer])
def read_account_transfers(account_id: UUID, db: Session = Depends(get_db)) -> List[Transfer]:
    transfers = transfer_crud.get_account_transfers(db, account_id=account_id)
    return transfers

# Add other endpoint functions as needed
