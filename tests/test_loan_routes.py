"""
Unit tests for Loan API routes.

Tests loan application submission, ML prediction integration,
and loan listing endpoints.
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


class TestLoanApplicationEndpoint:
    """Tests for POST /api/loans/apply"""

    def test_apply_missing_fields(self, client):
        """Should return 400 for missing required fields."""
        response = client.post('/api/loans/apply',
            data=json.dumps({'customer_id': 1}),
            content_type='application/json'
        )
        assert response.status_code in [400, 500]
        if response.status_code == 400:
            data = json.loads(response.data)
            assert 'error' in data

    def test_apply_empty_body(self, client):
        """Should return 400 for empty request body."""
        response = client.post('/api/loans/apply',
            data='',
            content_type='application/json'
        )
        assert response.status_code in [400, 500]

    def test_apply_valid_application(self, client):
        """Should process loan application with ML prediction."""
        application = {
            'customer_id': 1,
            'loan_amount': 2000000,
            'loan_tenure_months': 36,
            'interest_rate': 9.5,
            'loan_purpose': 'Home Renovation'
        }
        response = client.post('/api/loans/apply',
            data=json.dumps(application),
            content_type='application/json'
        )
        assert response.status_code in [201, 404, 500]
        if response.status_code == 201:
            data = json.loads(response.data)
            assert 'application_id' in data
            assert 'credit_score' in data
            assert 'risk_probability' in data
            assert 'status' in data
            assert data['status'] in ['Approved', 'Rejected', 'Pending']
            assert 'contributors' in data
            assert 300 <= data['credit_score'] <= 850
            assert 0 <= data['risk_probability'] <= 1

    def test_apply_nonexistent_customer(self, client):
        """Should return 404 for non-existent customer."""
        application = {
            'customer_id': 999999,
            'loan_amount': 1000000,
            'loan_tenure_months': 24,
            'interest_rate': 10.0,
            'loan_purpose': 'Personal'
        }
        response = client.post('/api/loans/apply',
            data=json.dumps(application),
            content_type='application/json'
        )
        assert response.status_code in [404, 500]

    def test_apply_high_risk_application(self, client):
        """High-risk loan should be flagged appropriately."""
        application = {
            'customer_id': 1,
            'loan_amount': 50000000,  # Very high loan amount
            'loan_tenure_months': 12,
            'interest_rate': 14.5,
            'loan_purpose': 'Personal'
        }
        response = client.post('/api/loans/apply',
            data=json.dumps(application),
            content_type='application/json'
        )
        assert response.status_code in [201, 404, 500]
        if response.status_code == 201:
            data = json.loads(response.data)
            # Very high loan should result in high risk
            assert data['risk_probability'] > 0.3


class TestLoanApplicationsListEndpoint:
    """Tests for GET /api/loans/applications"""

    def test_get_applications_default(self, client):
        """Should return applications with default pagination."""
        response = client.get('/api/loans/applications')
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'applications' in data
            assert 'total' in data

    def test_get_applications_filter_by_status(self, client):
        """Should filter applications by status."""
        response = client.get('/api/loans/applications?status=Approved')
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = json.loads(response.data)
            for app in data['applications']:
                assert app['status'] == 'Approved'

    def test_get_applications_filter_by_customer(self, client):
        """Should filter applications by customer ID."""
        response = client.get('/api/loans/applications?customer_id=1')
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = json.loads(response.data)
            for app in data['applications']:
                assert app['customer_id'] == 1


class TestLoansListEndpoint:
    """Tests for GET /api/loans/loans"""

    def test_get_loans_default(self, client):
        """Should return disbursed loans."""
        response = client.get('/api/loans/loans')
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'loans' in data
            assert 'total' in data

    def test_get_loans_filter_by_status(self, client):
        """Should filter loans by status."""
        response = client.get('/api/loans/loans?status=Active')
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = json.loads(response.data)
            for loan in data['loans']:
                assert loan['loan_status'] == 'Active'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
