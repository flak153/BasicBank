import pytest
from app.main import app
from fastapi.testclient import TestClient
from hypothesis import given, strategies as st, settings, HealthCheck
from uuid import UUID
from decimal import Decimal
from ..conftest import db_session

def decimal_strategy():
    return st.decimals(min_value=Decimal('0.01'), max_value=Decimal('1000000.00'), places=2).map(lambda d: d.quantize(Decimal('0.01')))

def valid_name_strategy():
    # Only allow letters, spaces, hyphens, and apostrophes
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'"
    return st.text(alphabet=st.sampled_from(alphabet), min_size=1, max_size=50)

@given(name=valid_name_strategy())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_create_customer(db_session, name):
    with db_session() as session:
        with TestClient(app) as client:
            response = client.post("/customers/", json={"name": name})
            print(response.json())  # Debugging line
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert UUID(data["id"])  # Check if the ID is a valid UUID
            assert data["name"] == name.title()

@given(st.data())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_create_account(db_session, data):
    with db_session() as session:
        with TestClient(app) as client:
            name = data.draw(valid_name_strategy())
            customer_response = client.post("/customers/", json={"name": name})
            assert customer_response.status_code == 200
            customer_id = customer_response.json()["id"]
            balance = data.draw(st.decimals(min_value=0.01, max_value=1000000, places=2))
            response = client.post("/accounts/", json={"customer_id": customer_id, "balance": str(balance)})
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert UUID(data["id"])  # Check if the ID is a valid UUID
            assert data["customer_id"] == customer_id
            assert Decimal(data["balance"]) == balance

@given(st.data())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_create_transfer(db_session, data):
    with db_session() as session:
        with TestClient(app) as client:
            name1 = data.draw(valid_name_strategy())
            name2 = data.draw(valid_name_strategy().filter(lambda x: x != name1))
            customer1_response = client.post("/customers/", json={"name": name1})
            assert customer1_response.status_code == 200
            customer1_id = customer1_response.json()["id"]
            customer2_response = client.post("/customers/", json={"name": name2})
            assert customer2_response.status_code == 200
            customer2_id = customer2_response.json()["id"]

            account1_response = client.post("/accounts/", json={"customer_id": customer1_id, "balance": "100.00"})
            assert account1_response.status_code == 200
            account1_id = account1_response.json()["id"]

            account2_response = client.post("/accounts/", json={"customer_id": customer2_id, "balance": "50.00"})
            assert account2_response.status_code == 200
            account2_id = account2_response.json()["id"]

            amount = data.draw(st.decimals(min_value=0.01, max_value=50.00, places=2))

            response = client.post("/transfers/", json={
                "from_account_id": account1_id,
                "to_account_id": account2_id,
                "amount": str(amount)
            })
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert UUID(data["id"])  # Check if the ID is a valid UUID
            assert data["from_account_id"] == account1_id
            assert data["to_account_id"] == account2_id
            assert Decimal(data["amount"]) == amount


@given(st.data())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_get_account_transfers(db_session, data):
    with db_session() as session:
        with TestClient(app) as client:
            name = data.draw(valid_name_strategy())
            customer_response = client.post("/customers/", json={"name": name})
            print("Customer response:", customer_response.json())  # Debugging line
            assert customer_response.status_code == 200
            customer_id = customer_response.json()["id"]

            account1_response = client.post("/accounts/", json={"customer_id": customer_id, "balance": "100.00"})
            print("Account1 response:", account1_response.json())  # Debugging line
            assert account1_response.status_code == 200
            account1_id = account1_response.json()["id"]

            account2_response = client.post("/accounts/", json={"customer_id": customer_id, "balance": "50.00"})
            print("Account2 response:", account2_response.json())  # Debugging line
            assert account2_response.status_code == 200
            account2_id = account2_response.json()["id"]

            amounts = data.draw(st.lists(st.decimals(min_value=0.01, max_value=10.00, places=2), min_size=1, max_size=5))

            for amount in amounts:
                response = client.post("/transfers/", json={
                    "from_account_id": account1_id,
                    "to_account_id": account2_id,
                    "amount": str(amount)
                })
                print("Transfer response:", response.json())  # Debugging line
                assert response.status_code == 200

            response = client.get(f"/transfers/account/{account1_id}")
            print("Get transfers response:", response.json())  # Debugging line
            assert response.status_code == 200
            transfers = response.json()
            assert len(transfers) == len(amounts), f"Expected {len(amounts)} transfers, got {len(transfers)}"

            for transfer, amount in zip(transfers, amounts):
                assert transfer["from_account_id"] == account1_id
                assert transfer["to_account_id"] == account2_id
                assert Decimal(transfer["amount"]) == amount

