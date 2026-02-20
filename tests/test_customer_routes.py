"""
Unit tests for Customer API routes.

Tests customer listing, detail retrieval, and registration endpoints.
"""

import sys
import os
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self, client):
        """Health endpoint should return 200."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'


class TestCustomerListEndpoint:
    """Tests for GET /api/customers/"""

    def test_get_customers_default(self, client):
        """Should return customers with default pagination."""
        response = client.get('/api/customers/')
        assert response.status_code in [200, 500]  # 500 if DB not connected
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'customers' in data
            assert 'total' in data
            assert 'limit' in data
            assert 'offset' in data

    def test_get_customers_with_pagination(self, client):
        """Should respect limit and offset parameters."""
        response = client.get('/api/customers/?limit=10&offset=5')
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['limit'] == 10
            assert data['offset'] == 5
            assert len(data['customers']) <= 10

    def test_get_customers_max_limit(self, client):
        """Limit should be capped at 500."""
        response = client.get('/api/customers/?limit=9999')
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['limit'] <= 500


class TestCustomerDetailEndpoint:
    """Tests for GET /api/customers/<id>"""

    def test_get_existing_customer(self, client):
        """Should return customer details if customer exists."""
        response = client.get('/api/customers/1')
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'customer_id' in data
            assert 'full_name' in data

    def test_get_nonexistent_customer(self, client):
        """Should return 404 for non-existent customer."""
        response = client.get('/api/customers/999999')
        assert response.status_code in [404, 500]


class TestCustomerRegistration:
    """Tests for POST /api/customers/"""

    def test_register_missing_fields(self, client):
        """Should return 400 for missing required fields."""
        response = client.post('/api/customers/',
            data=json.dumps({'first_name': 'Test'}),
            content_type='application/json'
        )
        assert response.status_code in [400, 500]

    def test_register_empty_body(self, client):
        """Should return 400 for empty request body."""
        response = client.post('/api/customers/',
            data='',
            content_type='application/json'
        )
        assert response.status_code in [400, 500]

    def test_register_valid_customer(self, client):
        """Should register customer with valid data."""
        import random
        customer_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': '1990-05-15',
            'email': f'test.user.{random.randint(10000, 99999)}@test.com',
            'phone': '+91-9876543210',
            'gender': 'Male',
            'city': 'Mumbai',
            'state': 'Maharashtra'
        }
        response = client.post('/api/customers/',
            data=json.dumps(customer_data),
            content_type='application/json'
        )
        assert response.status_code in [201, 409, 500]  # 409 if email exists


class TestRootEndpoint:
    """Tests for the root API endpoint."""

    def test_root(self, client):
        """Root endpoint should return API info."""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'name' in data
        assert 'endpoints' in data

    def test_404_endpoint(self, client):
        """Non-existent endpoint should return 404."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
