import pytest
from uuid import UUID, uuid4
from decimal import Decimal
from pydantic import ValidationError
from app.schemas.schemas import (
    CustomerCreate, AccountCreate, TransferCreate,
    Customer, Account, Transfer
)


def test_customer_create_schema():
    # Valid customer
    customer = CustomerCreate(name="John Doe")
    assert customer.name == "John Doe"

    # Invalid names
    with pytest.raises(ValidationError):
        CustomerCreate(name="")  # Empty name

    with pytest.raises(ValidationError):
        CustomerCreate(name="John123")  # Contains numbers

    with pytest.raises(ValidationError):
        CustomerCreate(name="John@Doe")  # Contains special characters

    # Name normalization
    customer = CustomerCreate(name="john doe")
    assert customer.name == "John Doe"


def test_account_create_schema():
    customer_id = uuid4()

    # Valid account
    account = AccountCreate(customer_id=customer_id, balance=Decimal("100.00"))
    assert account.customer_id == customer_id
    assert account.balance == Decimal("100.00")

    # Invalid customer_id
    with pytest.raises(ValidationError):
        AccountCreate(customer_id="not-a-uuid", balance=Decimal("100.00"))

    # Invalid balance
    with pytest.raises(ValidationError):
        AccountCreate(customer_id=customer_id, balance=Decimal("-100.00"))

    with pytest.raises(ValidationError):
        AccountCreate(customer_id=customer_id, balance="not-a-decimal")


def test_transfer_create_schema():
    from_account_id = uuid4()
    to_account_id = uuid4()

    # Valid transfer
    transfer = TransferCreate(from_account_id=from_account_id, to_account_id=to_account_id, amount=Decimal("500.00"))
    assert transfer.from_account_id == from_account_id
    assert transfer.to_account_id == to_account_id
    assert transfer.amount == Decimal("500.00")

    # Invalid UUID
    with pytest.raises(ValidationError):
        TransferCreate(from_account_id="not-a-uuid", to_account_id=to_account_id, amount=Decimal("50.00"))

    # Negative amount
    with pytest.raises(ValidationError):
        TransferCreate(from_account_id=from_account_id, to_account_id=to_account_id, amount=Decimal("-50.00"))

    # Same account transfer (this validation can be omitted if handled elsewhere)
    with pytest.raises(ValidationError):
        TransferCreate(from_account_id=from_account_id, to_account_id=from_account_id, amount=Decimal("50.00"))


def test_customer_schema():
    customer_id = uuid4()
    customer = Customer(id=customer_id, name="Jane Doe")
    assert customer.id == customer_id
    assert customer.name == "Jane Doe"

    with pytest.raises(ValidationError):
        Customer(id="not-a-uuid", name="Jane Doe")


def test_account_schema():
    account_id = uuid4()
    customer_id = uuid4()
    account = Account(id=account_id, customer_id=customer_id, balance=Decimal("1000.00"))
    assert account.id == account_id
    assert account.customer_id == customer_id
    assert account.balance == Decimal("1000.00")

    with pytest.raises(ValidationError):
        Account(id="not-a-uuid", customer_id=customer_id, balance=Decimal("1000.00"))

    with pytest.raises(ValidationError):
        Account(id=account_id, customer_id="not-a-uuid", balance=Decimal("1000.00"))

    with pytest.raises(ValidationError):
        Account(id=account_id, customer_id=customer_id, balance="not-a-decimal")


def test_transfer_schema():
    transfer_id = uuid4()
    from_account_id = uuid4()
    to_account_id = uuid4()
    transfer = Transfer(
        id=transfer_id,
        from_account_id=from_account_id,
        to_account_id=to_account_id,
        amount=Decimal("500.00")
    )
    assert transfer.id == transfer_id
    assert transfer.from_account_id == from_account_id
    assert transfer.to_account_id == to_account_id
    assert transfer.amount == Decimal("500.00")

    with pytest.raises(ValidationError):
        Transfer(
            id="not-a-uuid",
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=Decimal("500.00")
        )

    with pytest.raises(ValidationError):
        Transfer(
            id=transfer_id,
            from_account_id="not-a-uuid",
            to_account_id=to_account_id,
            amount=Decimal("500.00")
        )

    with pytest.raises(ValidationError):
        Transfer(
            id=transfer_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount="not-a-decimal"
        )
