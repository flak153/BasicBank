import string
import pytest
from hypothesis import given, settings, strategies as st
from app.schemas.schemas import CustomerCreate, AccountCreate, TransferCreate
from app.crud import customer as customer_crud
from app.crud import account as account_crud
from app.crud import transfer as transfer_crud
from decimal import Decimal

def valid_name_strategy():
    return st.text(min_size=1, max_size=50, alphabet=string.ascii_letters + " -'").map(lambda s: s.strip()).filter(lambda x: len(x) > 0)

@given(name=valid_name_strategy())
def test_create_customer(db_session, name):
    with db_session() as session:
        customer = customer_crud.create_customer(session, CustomerCreate(name=name))
        assert customer.id is not None
        assert customer.name.lower() == name.strip().lower()

@given(st.data())
def test_create_account(db_session, data):
    with db_session() as session:
        name = data.draw(valid_name_strategy())
        customer = customer_crud.create_customer(session, CustomerCreate(name=name))
        balance = data.draw(st.decimals(min_value=0.01, max_value=1000000, places=2))
        account = account_crud.create_account(session, AccountCreate(customer_id=customer.id, balance=float(balance)))
        assert account.id is not None
        assert account.customer_id == customer.id
        assert account.balance == balance

@given(st.data())
def test_create_transfer(db_session, data):
    with db_session() as session:
        name1 = data.draw(valid_name_strategy())
        name2 = data.draw(valid_name_strategy().filter(lambda x: x != name1))
        customer1 = customer_crud.create_customer(session, CustomerCreate(name=name1))
        customer2 = customer_crud.create_customer(session, CustomerCreate(name=name2))
        account1 = account_crud.create_account(session, AccountCreate(customer_id=customer1.id, balance=Decimal('100.00')))
        account2 = account_crud.create_account(session, AccountCreate(customer_id=customer2.id, balance=Decimal('50.00')))
        amount = data.draw(st.decimals(min_value=0.01, max_value=50.00, places=2))

        # Ensure sufficient balance for transfer
        if amount >= account1.balance:
            account_crud.update_account_balance(session, account1.id, amount + Decimal('10.00') - account1.balance)
            session.refresh(account1)

        initial_balance1 = account1.balance
        initial_balance2 = account2.balance

        transfer = transfer_crud.create_transfer(session, TransferCreate(
            from_account_id=account1.id,
            to_account_id=account2.id,
            amount=float(amount)
        ))

        assert transfer.id is not None
        assert transfer.from_account_id == account1.id
        assert transfer.to_account_id == account2.id
        assert transfer.amount == amount

        updated_account1 = account_crud.get_account(session, account1.id)
        updated_account2 = account_crud.get_account(session, account2.id)

        assert updated_account1.balance == initial_balance1 - amount
        assert updated_account2.balance == initial_balance2 + amount
@given(st.data())
@settings(deadline=500)  # Disable the deadline for this test
def test_get_account_transfers(db_session, data):
    with db_session() as session:
        name = data.draw(valid_name_strategy())
        customer = customer_crud.create_customer(session, CustomerCreate(name=name))
        account1 = account_crud.create_account(session, AccountCreate(customer_id=customer.id, balance=Decimal('100.00')))
        account2 = account_crud.create_account(session, AccountCreate(customer_id=customer.id, balance=Decimal('50.00')))
        amounts = data.draw(st.lists(st.decimals(min_value=0.01, max_value=10.00, places=2), min_size=1, max_size=5))

        # Calculate total transfer amount
        total_transfer_amount = sum(amounts)

        # Ensure account1 has sufficient balance
        if total_transfer_amount > account1.balance:
            new_balance = total_transfer_amount + Decimal('10.00')
            account_crud.update_account_balance(session, account1.id, new_balance)
            session.refresh(account1)

        initial_balance1 = account1.balance
        initial_balance2 = account2.balance

        for amount in amounts:
            try:
                transfer_crud.create_transfer(session, TransferCreate(
                    from_account_id=account1.id,
                    to_account_id=account2.id,
                    amount=amount
                ))
            except Exception as e:
                pytest.fail(f"Failed to create transfer: {e}")

        transfers = transfer_crud.get_account_transfers(session, account1.id)
        assert len(transfers) == len(amounts), f"Expected {len(amounts)} transfers, got {len(transfers)}"

        for transfer, amount in zip(transfers, amounts):
            assert transfer.from_account_id == account1.id
            assert transfer.to_account_id == account2.id
            assert transfer.amount == amount

        # Verify final balances
        final_account1 = account_crud.get_account(session, account1.id)
        final_account2 = account_crud.get_account(session, account2.id)
        assert final_account1.balance == initial_balance1 - total_transfer_amount
        assert final_account2.balance == initial_balance2 + total_transfer_amount
