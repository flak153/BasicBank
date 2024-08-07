from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from datetime import datetime, timezone
import uuid


class Customer(Base):
    """
    Represents a customer in the database.

    Attributes:
        id (UUID): Primary key, unique identifier for the customer.
        name (str): Name of the customer.
        accounts (list[Account]): List of accounts associated with the customer.
    """
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), index=True)
    accounts = relationship("Account", back_populates="customer")


class Account(Base):
    """
    Represents an account in the database.

    Attributes:
        id (UUID): Primary key, unique identifier for the account.
        customer_id (UUID): Foreign key, references the customer who owns the account.
        balance (Decimal): Balance of the account with high precision.
        customer (Customer): The customer who owns the account.
        transfers_from (list[Transfer]): List of transfers originating from this account.
        transfers_to (list[Transfer]): List of transfers destined to this account.
    """
    __tablename__ = "accounts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    balance = Column(Numeric(precision=36, scale=20))  # High precision for financial calculations
    customer = relationship("Customer", back_populates="accounts")
    transfers_from = relationship("Transfer", foreign_keys="[Transfer.from_account_id]", back_populates="from_account")
    transfers_to = relationship("Transfer", foreign_keys="[Transfer.to_account_id]", back_populates="to_account")


class Transfer(Base):
    """
    Represents a transfer in the database.

    Attributes:
        id (UUID): Primary key, unique identifier for the transfer.
        from_account_id (UUID): Foreign key, references the account from which the transfer originates.
        to_account_id (UUID): Foreign key, references the account to which the transfer is destined.
        amount (Decimal): Amount of money being transferred with high precision.
        timestamp (datetime): Timestamp of when the transfer was made, timezone-aware.
        from_account (Account): The account from which the transfer originates.
        to_account (Account): The account to which the transfer is destined.
    """
    __tablename__ = "transfers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    from_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    to_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    amount = Column(Numeric(precision=36, scale=20))  # High precision for financial calculations
    timestamp = Column(DateTime(timezone=True),
                       default=lambda: datetime.now(timezone.utc))  # Ensure timezone-aware datetime
    from_account = relationship("Account", foreign_keys=[from_account_id], back_populates="transfers_from")
    to_account = relationship("Account", foreign_keys=[to_account_id], back_populates="transfers_to")
