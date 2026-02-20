"""
Unit tests for financial calculation utilities.

Tests EMI, DTI, LTI, NPA classification, credit score mapping,
and risk recommendation generation.
"""

import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.utils.calculations import (
    calculate_emi,
    calculate_dti_ratio,
    calculate_lti_ratio,
    calculate_ltv_ratio,
    classify_npa,
    calculate_provision,
    risk_probability_to_credit_score,
    get_risk_level,
    generate_recommendation
)


class TestEMICalculation:
    """Tests for EMI (Equated Monthly Installment) calculation."""

    def test_standard_loan(self):
        """Test EMI for a typical home loan."""
        emi = calculate_emi(principal=3000000, annual_rate=9.5, tenure_months=240)
        assert emi > 0
        assert 25000 < emi < 35000  # Expected range for this loan

    def test_short_tenure(self):
        """Test EMI for a short-tenure personal loan."""
        emi = calculate_emi(principal=500000, annual_rate=12.0, tenure_months=12)
        assert emi > 0
        assert emi > 500000 / 12  # EMI should be more than simple division

    def test_zero_interest(self):
        """Test EMI with 0% interest rate."""
        emi = calculate_emi(principal=120000, annual_rate=0, tenure_months=12)
        assert emi == 10000.0  # Simple division when no interest

    def test_high_interest(self):
        """Test EMI with high interest rate."""
        emi = calculate_emi(principal=1000000, annual_rate=15.0, tenure_months=60)
        assert emi > 0
        assert emi * 60 > 1000000  # Total payment should exceed principal

    def test_emi_precision(self):
        """Test that EMI is rounded to 2 decimal places."""
        emi = calculate_emi(principal=1000000, annual_rate=10.0, tenure_months=36)
        assert emi == round(emi, 2)


class TestDTIRatio:
    """Tests for Debt-to-Income ratio calculation."""

    def test_healthy_dti(self):
        """Test DTI for a healthy financial profile."""
        dti = calculate_dti_ratio(monthly_emi=20000, monthly_income=100000)
        assert dti == 0.2

    def test_high_dti(self):
        """Test DTI exceeding safe threshold."""
        dti = calculate_dti_ratio(monthly_emi=50000, monthly_income=80000)
        assert dti > 0.40
        assert dti == 0.625

    def test_zero_income(self):
        """Test DTI with zero income returns 1.0."""
        dti = calculate_dti_ratio(monthly_emi=10000, monthly_income=0)
        assert dti == 1.0

    def test_negative_income(self):
        """Test DTI with negative income returns 1.0."""
        dti = calculate_dti_ratio(monthly_emi=10000, monthly_income=-5000)
        assert dti == 1.0


class TestLTIRatio:
    """Tests for Loan-to-Income ratio calculation."""

    def test_reasonable_lti(self):
        """Test LTI for a reasonable loan."""
        lti = calculate_lti_ratio(loan_amount=2000000, annual_income=1200000)
        assert round(lti, 2) == 1.67

    def test_high_lti(self):
        """Test high LTI indicating overborrowing."""
        lti = calculate_lti_ratio(loan_amount=10000000, annual_income=600000)
        assert lti > 5  # Very high LTI

    def test_zero_income(self):
        """Test LTI with zero annual income returns 10.0."""
        lti = calculate_lti_ratio(loan_amount=1000000, annual_income=0)
        assert lti == 10.0


class TestLTVRatio:
    """Tests for Loan-to-Value ratio calculation."""

    def test_standard_ltv(self):
        """Test LTV with adequate collateral."""
        ltv = calculate_ltv_ratio(loan_amount=5000000, collateral_value=8000000)
        assert ltv == 0.625

    def test_zero_collateral(self):
        """Test LTV with zero collateral returns 1.0."""
        ltv = calculate_ltv_ratio(loan_amount=1000000, collateral_value=0)
        assert ltv == 1.0


class TestNPAClassification:
    """Tests for NPA (Non-Performing Asset) classification."""

    def test_standard_loan(self):
        """Loans less than 90 days overdue are Standard."""
        assert classify_npa(0) == 'Standard'
        assert classify_npa(45) == 'Standard'
        assert classify_npa(89) == 'Standard'

    def test_sub_standard(self):
        """Loans 90-180 days overdue are Sub-Standard."""
        assert classify_npa(90) == 'Sub-Standard'
        assert classify_npa(120) == 'Sub-Standard'
        assert classify_npa(180) == 'Sub-Standard'

    def test_doubtful(self):
        """Loans 181-365 days overdue are Doubtful."""
        assert classify_npa(181) == 'Doubtful'
        assert classify_npa(300) == 'Doubtful'
        assert classify_npa(365) == 'Doubtful'

    def test_loss(self):
        """Loans over 365 days overdue are Loss assets."""
        assert classify_npa(366) == 'Loss'
        assert classify_npa(500) == 'Loss'
        assert classify_npa(1000) == 'Loss'


class TestProvisionCalculation:
    """Tests for NPA provision amount calculation."""

    def test_standard_provision(self):
        """Standard assets require 0.40% provision."""
        provision = calculate_provision(1000000, 'Standard')
        assert provision == 4000.0

    def test_sub_standard_provision(self):
        """Sub-Standard assets require 15% provision."""
        provision = calculate_provision(1000000, 'Sub-Standard')
        assert provision == 150000.0

    def test_doubtful_provision(self):
        """Doubtful assets require 40% provision."""
        provision = calculate_provision(1000000, 'Doubtful')
        assert provision == 400000.0

    def test_loss_provision(self):
        """Loss assets require 100% provision."""
        provision = calculate_provision(1000000, 'Loss')
        assert provision == 1000000.0


class TestCreditScoreMapping:
    """Tests for risk probability to credit score conversion."""

    def test_low_risk(self):
        """Low risk probability → High credit score."""
        score = risk_probability_to_credit_score(0.1)
        assert score >= 750

    def test_high_risk(self):
        """High risk probability → Low credit score."""
        score = risk_probability_to_credit_score(0.9)
        assert score <= 400

    def test_score_bounds(self):
        """Credit score should always be between 300 and 850."""
        assert risk_probability_to_credit_score(0.0) <= 850
        assert risk_probability_to_credit_score(1.0) >= 300

    def test_zero_risk(self):
        """Zero risk should give maximum score."""
        score = risk_probability_to_credit_score(0.0)
        assert score == 850.0

    def test_full_risk(self):
        """100% risk should give minimum score."""
        score = risk_probability_to_credit_score(1.0)
        assert score == 300.0


class TestRiskLevel:
    """Tests for risk level categorization."""

    def test_low_risk(self):
        assert get_risk_level(0.10) == 'Low'
        assert get_risk_level(0.29) == 'Low'

    def test_medium_risk(self):
        assert get_risk_level(0.30) == 'Medium'
        assert get_risk_level(0.50) == 'Medium'

    def test_high_risk(self):
        assert get_risk_level(0.60) == 'High'
        assert get_risk_level(0.90) == 'High'


class TestRecommendation:
    """Tests for recommendation text generation."""

    def test_low_risk_recommendation(self):
        rec = generate_recommendation(0.15, 0.20, 2.0, 780)
        assert 'Low risk' in rec

    def test_high_risk_dti(self):
        rec = generate_recommendation(0.75, 0.55, 8.0, 350)
        assert 'High risk' in rec
        assert 'DTI' in rec

    def test_moderate_risk(self):
        rec = generate_recommendation(0.50, 0.38, 4.0, 550)
        assert 'Moderate risk' in rec


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
