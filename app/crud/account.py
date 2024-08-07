from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.models import Account
from app.schemas.schemas import AccountCreate
from decimal import Decimal


def create_account(db: Session, account: AccountCreate) -> Account:
    db_account = Account(customer_id=account.customer_id, balance=Decimal(str(account.balance)))
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def get_account(db: Session, account_id: int) -> Account:
    return db.query(Account).filter(Account.id == account_id).first()


def get_account_balance(db: Session, account_id: int) -> Decimal:
    account = get_account(db, account_id)
    return account.balance if account else None


def update_account_balance(db: Session, account_id: int, amount: Decimal) -> Account:
    """
    Update the balance of an account by a specified amount.

    Args:
        db (Session): The database session.
        account_id (int): The ID of the account to update.
        amount (Decimal): The amount to update the balance by. Can be positive or negative.

    Returns:
        Account: The updated account.

    Raises:
        HTTPException: If the account is not found.
    """
    account = get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.balance += amount
    db.commit()
    db.refresh(account)
    return account

# Add other CRUD operations as needed
