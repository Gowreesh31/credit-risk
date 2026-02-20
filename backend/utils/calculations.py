"""
Financial calculation utilities for the Credit Risk System.

Provides core financial formulas:
- EMI (Equated Monthly Installment) calculation
- Debt-to-Income (DTI) ratio
- Loan-to-Income (LTI) ratio
- NPA classification logic
- Credit score mapping
"""

import math


def calculate_emi(principal, annual_rate, tenure_months):
    """
    Calculate Equated Monthly Installment using compound interest formula.

    EMI = P × r × (1+r)^n / ((1+r)^n - 1)

    Args:
        principal (float): Loan amount in ₹
        annual_rate (float): Annual interest rate (e.g., 9.5 for 9.5%)
        tenure_months (int): Loan tenure in months

    Returns:
        float: Monthly EMI amount
    """
    if annual_rate == 0:
        return round(principal / tenure_months, 2)

    monthly_rate = annual_rate / (12 * 100)
    numerator = principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)
    denominator = math.pow(1 + monthly_rate, tenure_months) - 1
    emi = numerator / denominator
    return round(emi, 2)


def calculate_dti_ratio(monthly_emi, monthly_income):
    """
    Calculate Debt-to-Income ratio.

    DTI = Monthly EMI / Monthly Income

    Args:
        monthly_emi (float): Total monthly debt obligations
        monthly_income (float): Gross monthly income

    Returns:
        float: DTI ratio (0 to 1+)
    """
    if monthly_income <= 0:
        return 1.0
    return round(monthly_emi / monthly_income, 4)


def calculate_lti_ratio(loan_amount, annual_income):
    """
    Calculate Loan-to-Income ratio.

    LTI = Total Loan Amount / Annual Income

    Args:
        loan_amount (float): Total loan amount
        annual_income (float): Annual gross income

    Returns:
        float: LTI ratio
    """
    if annual_income <= 0:
        return 10.0
    return round(loan_amount / annual_income, 4)


def calculate_ltv_ratio(loan_amount, collateral_value):
    """
    Calculate Loan-to-Value ratio.

    LTV = Loan Amount / Collateral Value

    Args:
        loan_amount (float): Loan amount
        collateral_value (float): Estimated collateral value

    Returns:
        float: LTV ratio
    """
    if collateral_value <= 0:
        return 1.0
    return round(loan_amount / collateral_value, 4)


def classify_npa(days_overdue):
    """
    Classify NPA category based on RBI guidelines.

    - Standard: 0-89 days overdue
    - Sub-Standard: 90-180 days overdue
    - Doubtful: 181-365 days overdue
    - Loss: >365 days overdue

    Args:
        days_overdue (int): Number of days the payment is overdue

    Returns:
        str: NPA classification category
    """
    if days_overdue < 90:
        return 'Standard'
    elif days_overdue <= 180:
        return 'Sub-Standard'
    elif days_overdue <= 365:
        return 'Doubtful'
    else:
        return 'Loss'


def calculate_provision(outstanding_amount, npa_category):
    """
    Calculate required provision amount based on NPA category.

    Provisioning rates (RBI norms):
    - Standard: 0.40%
    - Sub-Standard: 15%
    - Doubtful: 40%
    - Loss: 100%

    Args:
        outstanding_amount (float): Outstanding loan amount
        npa_category (str): NPA classification

    Returns:
        float: Required provision amount
    """
    rates = {
        'Standard': 0.004,
        'Sub-Standard': 0.15,
        'Doubtful': 0.40,
        'Loss': 1.0
    }
    rate = rates.get(npa_category, 0.004)
    return round(outstanding_amount * rate, 2)


def risk_probability_to_credit_score(risk_probability):
    """
    Map risk probability to credit score on 300-850 scale.

    Lower risk probability → Higher credit score (inverse relationship).

    Args:
        risk_probability (float): Model output between 0 and 1

    Returns:
        float: Credit score between 300 and 850
    """
    # Linear inverse mapping: 0.0 risk → 850 score, 1.0 risk → 300 score
    score = 850 - (risk_probability * 550)
    return round(max(300, min(850, score)), 2)


def get_risk_level(risk_probability):
    """
    Categorize risk level from probability.

    Args:
        risk_probability (float): Model output between 0 and 1

    Returns:
        str: 'Low', 'Medium', or 'High'
    """
    if risk_probability < 0.30:
        return 'Low'
    elif risk_probability < 0.60:
        return 'Medium'
    else:
        return 'High'


def generate_recommendation(risk_probability, dti_ratio, lti_ratio, credit_score):
    """
    Generate a human-readable recommendation based on risk assessment.

    Args:
        risk_probability (float): Model prediction
        dti_ratio (float): Debt-to-Income ratio
        lti_ratio (float): Loan-to-Income ratio
        credit_score (float): Calculated credit score

    Returns:
        str: Recommendation text
    """
    if risk_probability < 0.30:
        return "Low risk — Strong financial profile with healthy debt ratios"
    elif risk_probability < 0.45:
        return "Low-moderate risk — Acceptable financial metrics within safe thresholds"
    elif risk_probability < 0.60:
        if dti_ratio > 0.35:
            return f"Moderate risk — DTI ratio ({dti_ratio:.1%}) approaching threshold, manual review recommended"
        else:
            return "Moderate risk — Some risk factors present, requires additional assessment"
    else:
        reasons = []
        if dti_ratio > 0.40:
            reasons.append(f"DTI ratio ({dti_ratio:.1%}) exceeds safe threshold (40%)")
        if lti_ratio > 5:
            reasons.append(f"LTI ratio ({lti_ratio:.2f}x) indicates high loan burden")
        if credit_score < 500:
            reasons.append(f"Credit score ({credit_score}) below acceptable range")

        if reasons:
            return f"High risk — {'; '.join(reasons)}"
        else:
            return "High risk — Multiple risk factors indicate elevated default probability"
