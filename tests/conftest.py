import string
from decimal import Decimal

import pytest, os, sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import Base, get_db, SQLALCHEMY_DATABASE_URL
from app.main import app
from hypothesis import given, strategies as st
from contextlib import contextmanager

# Use the same database URL as in database.py
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    """
    Create a SQLAlchemy engine for the test database.
    """
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def db_session():
    Base.metadata.create_all(bind=engine)

    @contextmanager
    def get_session():
        session = TestingSessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    yield get_session

    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session()
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client

def valid_name_strategy():
    # Only allow letters, spaces, hyphens, and apostrophes
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'"
    return st.text(alphabet=st.sampled_from(alphabet), min_size=1, max_size=50)

def decimal_strategy():
    return st.decimals(min_value=Decimal('0.01'), max_value=Decimal('1000000.00'), places=2).map(lambda d: d.quantize(Decimal('0.01')))
