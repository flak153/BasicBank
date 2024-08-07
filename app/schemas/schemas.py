from pydantic import BaseModel, Field, field_validator, model_validator, UUID4
from decimal import Decimal
import re
from typing import ClassVar

class CustomerCreate(BaseModel):
    """
    Schema for creating a new customer.

    Attributes:
        name (str): The name of the customer. Must be between 1 and 100 characters.
    """
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator('name')
    @classmethod
    def validate_realistic_name(cls, v: str) -> str:
        """
        Validates that the name contains only letters, spaces, hyphens, and apostrophes.

        Args:
            v (str): The name to validate.

        Returns:
            str: The validated name in title case.

        Raises:
            ValueError: If the name contains invalid characters.
        """
        if not re.match(r'^[A-Za-z\s\-\']+$', v):
            raise ValueError('Name must contain only letters, spaces, hyphens, and apostrophes')
        return v.title()


class AccountCreate(BaseModel):
    """
    Schema for creating a new account.

    Attributes:
        customer_id (UUID4): The ID of the customer who owns the account.
        balance (Decimal): The initial balance of the account. Must be non-negative with up to 20 decimal places.
    """
    customer_id: UUID4
    balance: Decimal = Field(..., ge=Decimal('0.00'), decimal_places=20)

    @field_validator('balance')
    @classmethod
    def validate_positive_balance(cls, v: Decimal) -> Decimal:
        """
        Validates that the initial balance is positive.

        Args:
            v (Decimal): The balance to validate.

        Returns:
            Decimal: The validated balance.

        Raises:
            ValueError: If the balance is not positive.
        """
        if v <= Decimal('0'):
            raise ValueError('Initial balance must be positive')
        return v


class TransferCreate(BaseModel):
    """
    Schema for creating a new transfer.

    Attributes:
        from_account_id (UUID4): The ID of the account from which the transfer originates.
        to_account_id (UUID4): The ID of the account to which the transfer is destined.
        amount (Decimal): The amount of money to transfer. Must be positive with up to 20 decimal places.
    """
    from_account_id: UUID4
    to_account_id: UUID4
    amount: Decimal = Field(..., gt=Decimal('0'), decimal_places=20)

    @model_validator(mode='after')
    def validate_transfer(self) -> 'TransferCreate':
        """
        Validates that the transfer is not to the same account.

        Returns:
            TransferCreate: The validated transfer.

        Raises:
            ValueError: If the transfer is to the same account.
        """
        if self.from_account_id == self.to_account_id:
            raise ValueError('Cannot transfer to the same account')
        return self


class Customer(BaseModel):
    """
    Schema for a customer.

    Attributes:
        id (UUID4): The unique identifier of the customer.
        name (str): The name of the customer.
    """
    id: UUID4
    name: str


class Account(BaseModel):
    """
    Schema for an account.

    Attributes:
        id (UUID4): The unique identifier of the account.
        customer_id (UUID4): The ID of the customer who owns the account.
        balance (Decimal): The balance of the account.
    """
    id: UUID4
    customer_id: UUID4
    balance: Decimal


class Transfer(BaseModel):
    """
    Schema for a transfer.

    Attributes:
        id (UUID4): The unique identifier of the transfer.
        from_account_id (UUID4): The ID of the account from which the transfer originates.
        to_account_id (UUID4): The ID of the account to which the transfer is destined.
        amount (Decimal): The amount of money being transferred.
    """
    id: UUID4
    from_account_id: UUID4
    to_account_id: UUID4
    amount: Decimal