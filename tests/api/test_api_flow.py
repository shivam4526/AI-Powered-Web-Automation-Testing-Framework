import pytest
import requests


@pytest.mark.api
def test_login_api(base_url):
    response = requests.post(
        f"{base_url}/login",
        json={"username": "demouser", "password": "Password123"},
        timeout=5,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"


@pytest.mark.api
def test_products_api_requires_auth(base_url):
    response = requests.get(f"{base_url}/products", timeout=5)
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication required"


@pytest.mark.api
def test_checkout_api(base_url):
    session = requests.Session()
    login_response = session.post(
        f"{base_url}/login",
        json={"username": "demouser", "password": "Password123"},
        timeout=5,
    )
    assert login_response.status_code == 200

    add_response = session.post(
        f"{base_url}/cart",
        json={"product_id": 1, "quantity": 1},
        timeout=5,
    )
    assert add_response.status_code == 200
    assert add_response.json()["message"] == "Product added to cart"

    checkout_response = session.post(f"{base_url}/checkout", timeout=5)
    body = checkout_response.json()
    assert checkout_response.status_code == 200
    assert body["message"] == "Checkout complete"
    assert body["order_summary"]["status"] == "confirmed"
