from sqlalchemy.orm import Session
from app.models.models import Transfer, Account
from app.schemas.schemas import TransferCreate
from decimal import Decimal
from fastapi import HTTPException
from app.crud.account import update_account_balance, get_account

def create_transfer(db: Session, transfer: TransferCreate) -> Transfer:
    # Get accounts
    from_account = get_account(db, transfer.from_account_id)
    to_account = get_account(db, transfer.to_account_id)

    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail="One or both accounts not found")

    amount = Decimal(str(transfer.amount))

    # Check balance
    if from_account.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Create transfer record
    db_transfer = Transfer(
        from_account_id=transfer.from_account_id,
        to_account_id=transfer.to_account_id,
        amount=amount
    )
    db.add(db_transfer)

    # Update account balances
    update_account_balance(db, from_account.id, -amount)
    update_account_balance(db, to_account.id, amount)

    db.commit()
    db.refresh(db_transfer)
    return db_transfer

def get_transfer(db: Session, transfer_id: int) -> Transfer:
    return db.query(Transfer).filter(Transfer.id == transfer_id).first()

def get_account_transfers(db: Session, account_id: int) -> list[Transfer]:
    return db.query(Transfer).filter(
        (Transfer.from_account_id == account_id) | (Transfer.to_account_id == account_id)
    ).all()
