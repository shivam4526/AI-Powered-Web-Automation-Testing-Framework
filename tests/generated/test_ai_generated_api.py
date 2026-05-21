import pytest
import requests


CASES = [{'expected_key': 'message',
  'expected_status': 200,
  'expected_value': 'Login successful',
  'feature': 'login',
  'id': 'api_login_positive',
  'input': {'password': 'Password123', 'username': 'demouser'},
  'layer': 'api',
  'route': '/login',
  'title': 'AI generated API test: valid user can log in',
  'type': 'positive'},
 {'expected_key': 'error',
  'expected_status': 401,
  'expected_value': 'Authentication required',
  'feature': 'products',
  'id': 'api_products_requires_auth',
  'layer': 'api',
  'route': '/products',
  'title': 'AI generated API test: products endpoint rejects anonymous access',
  'type': 'negative'},
 {'expected_key': 'message',
  'expected_status': 200,
  'expected_value': 'Checkout complete',
  'feature': 'checkout',
  'id': 'api_checkout_positive',
  'layer': 'api',
  'route': '/checkout',
  'setup': {'add_to_cart': {'product_id': 1, 'quantity': 1}, 'login': True},
  'title': 'AI generated API test: logged in user can add product and checkout',
  'type': 'positive'}]


def _login(session, base_url, credentials):
    response = session.post(f"{base_url}/login", json=credentials, timeout=5)
    assert response.status_code == 200


@pytest.mark.api
@pytest.mark.generated
@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_ai_generated_api_cases(base_url, case):
    if case["id"] == "api_login_positive":
        response = requests.post(f"{base_url}/login", json=case["input"], timeout=5)
        body = response.json()
        assert response.status_code == case["expected_status"]
        assert body[case["expected_key"]] == case["expected_value"]
        return

    if case["id"] == "api_products_requires_auth":
        response = requests.get(f"{base_url}{case['route']}", timeout=5)
        body = response.json()
        assert response.status_code == case["expected_status"]
        assert body[case["expected_key"]] == case["expected_value"]
        return

    if case["id"] == "api_checkout_positive":
        session = requests.Session()
        _login(session, base_url, {"username": "demouser", "password": "Password123"})
        setup = case["setup"]["add_to_cart"]
        add_response = session.post(f"{base_url}/cart", json=setup, timeout=5)
        assert add_response.status_code == 200
        response = session.post(f"{base_url}{case['route']}", timeout=5)
        body = response.json()
        assert response.status_code == case["expected_status"]
        assert body[case["expected_key"]] == case["expected_value"]
        return

    raise AssertionError(f"Unhandled API case: {case['id']}")
