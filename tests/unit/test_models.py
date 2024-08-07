import pytest
from app.models.models import Customer, Account, Transfer
from decimal import Decimal
from uuid import UUID
from datetime import datetime, timedelta, timezone
from hypothesis import given, strategies as st
from ..conftest import valid_name_strategy
@given(name=valid_name_strategy())
def test_customer_model(db_session, name):
    with db_session() as db:
        customer = Customer(name=name)
        db.add(customer)
        db.commit()
        assert customer.id is not None
        assert isinstance(customer.id, UUID)
        assert customer.name == name

@given(name=valid_name_strategy())
def test_multiple_customers_same_name(db_session, name):
    with db_session() as db:
        customer1 = Customer(name=name)
        customer2 = Customer(name=name)
        db.add(customer1)
        db.add(customer2)
        db.commit()
        assert customer1.id != customer2.id
        assert customer1.name == customer2.name == name

@given(balance=st.decimals(min_value=0, max_value=1000000, places=2))
def test_account_model(db_session, balance):
    with db_session() as db:
        customer = Customer(name="Jane Doe")
        db.add(customer)
        db.commit()

        account = Account(customer_id=customer.id, balance=balance)
        db.add(account)
        db.commit()

        assert account.id is not None
        assert isinstance(account.id, UUID)
        assert account.customer_id == customer.id
        assert account.balance == balance

@given(amount=st.decimals(min_value=0.01, max_value=100, places=2))
def test_transfer_model(db_session, amount):
    with db_session() as db:
        customer1 = Customer(name="Alice")
        customer2 = Customer(name="Bob")
        db.add(customer1)
        db.add(customer2)
        db.commit()

        account1 = Account(customer_id=customer1.id, balance=Decimal('100.00'))
        account2 = Account(customer_id=customer2.id, balance=Decimal('50.00'))
        db.add(account1)
        db.add(account2)
        db.commit()

        transfer = Transfer(
            from_account_id=account1.id,
            to_account_id=account2.id,
            amount=amount,
            timestamp=datetime.now(timezone.utc)  # Ensure the timestamp has timezone info
        )
        db.add(transfer)
        db.commit()

        assert transfer.id is not None
        assert isinstance(transfer.id, UUID)
        assert transfer.from_account_id == account1.id
        assert transfer.to_account_id == account2.id
        assert transfer.amount == amount
        assert isinstance(transfer.timestamp, datetime)
        assert transfer.timestamp.tzinfo is not None
        assert transfer.timestamp <= datetime.now(timezone.utc)
        assert transfer.timestamp >= datetime.now(timezone.utc) - timedelta(seconds=10)
def test_relationships(db_session):
    with db_session() as db:
        customer = Customer(name="Charlie")
        db.add(customer)
        db.commit()

        account1 = Account(customer_id=customer.id, balance=Decimal('100.00'))
        account2 = Account(customer_id=customer.id, balance=Decimal('200.00'))
        db.add(account1)
        db.add(account2)
        db.commit()

        transfer = Transfer(from_account_id=account1.id, to_account_id=account2.id, amount=Decimal('50.00'))
        db.add(transfer)
        db.commit()

        db.refresh(customer)
        db.refresh(account1)
        db.refresh(account2)

        assert len(customer.accounts) == 2
        assert account1 in customer.accounts
        assert account2 in customer.accounts

        assert len(account1.transfers_from) == 1
        assert len(account2.transfers_to) == 1
        assert transfer in account1.transfers_from
        assert transfer in account2.transfers_to

        assert transfer.from_account == account1
        assert transfer.to_account == account2