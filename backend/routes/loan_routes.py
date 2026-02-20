"""
Loan API Routes — Loan application, ML predictions, and loan management.
"""

import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from backend.database import get_db_session
from backend.models import (
    Customer, EmploymentDetail, LoanApplication, Loan, Disbursement
)
from backend.utils.calculations import (
    calculate_emi, calculate_dti_ratio, calculate_lti_ratio,
    get_risk_level, generate_recommendation
)

loan_bp = Blueprint('loans', __name__, url_prefix='/api/loans')


def _get_ml_prediction(features):
    """
    Get ML prediction from the trained model.
    Falls back to rule-based assessment if model is unavailable.
    """
    try:
        from ml.predict import predict_risk
        return predict_risk(features)
    except Exception as e:
        # Fallback: rule-based risk assessment
        dti = features.get('debt_to_income_ratio', 0.5)
        lti = features.get('loan_to_income_ratio', 5)

        if dti > 0.50:
            risk_prob = 0.85
        elif dti > 0.40:
            risk_prob = 0.60
        elif dti > 0.30:
            risk_prob = 0.35
        elif dti > 0.20:
            risk_prob = 0.15
        else:
            risk_prob = 0.08

        from backend.utils.calculations import risk_probability_to_credit_score
        credit_score = risk_probability_to_credit_score(risk_prob)

        return {
            'risk_probability': risk_prob,
            'credit_score': credit_score,
            'contributors': [
                {'feature': 'debt_to_income_ratio', 'impact': round(dti * 0.8, 4)},
                {'feature': 'loan_to_income_ratio', 'impact': round(min(lti * 0.04, 0.3), 4)},
                {'feature': 'monthly_income', 'impact': round(-features.get('monthly_income', 50000) / 500000, 4)}
            ],
            'model_used': 'rule_based_fallback'
        }


@loan_bp.route('/apply', methods=['POST'])
def apply_for_loan():
    """
    Submit a new loan application with real-time ML prediction.
    Returns credit score, risk probability, and SHAP-based feature contributions.
    """
    session = get_db_session()
    start_time = time.time()

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        # Validate required fields
        required = ['customer_id', 'loan_amount', 'loan_tenure_months', 'interest_rate']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        customer_id = data['customer_id']
        loan_amount = float(data['loan_amount'])
        tenure_months = int(data['loan_tenure_months'])
        interest_rate = float(data['interest_rate'])
        loan_purpose = data.get('loan_purpose', 'Personal')

        # Fetch customer data
        customer = session.query(Customer).filter_by(customer_id=customer_id).first()
        if not customer:
            return jsonify({'error': f'Customer {customer_id} not found'}), 404

        employment = session.query(EmploymentDetail)\
            .filter_by(customer_id=customer_id).first()
        if not employment:
            return jsonify({'error': f'Employment data not found for customer {customer_id}'}), 404

        monthly_income = float(employment.monthly_income)
        annual_income = monthly_income * 12
        years_exp = float(employment.years_of_experience) if employment.years_of_experience else 0

        # Calculate financial metrics
        emi = calculate_emi(loan_amount, interest_rate, tenure_months)
        dti_ratio = calculate_dti_ratio(emi, monthly_income)
        lti_ratio = calculate_lti_ratio(loan_amount, annual_income)

        # Calculate age
        from datetime import date
        today = date.today()
        age = (today - customer.date_of_birth).days / 365.25

        # Prepare features for ML model
        features = {
            'loan_amount': loan_amount,
            'loan_tenure_months': tenure_months,
            'interest_rate': interest_rate,
            'monthly_income': monthly_income,
            'annual_income': annual_income,
            'years_of_experience': years_exp,
            'age': age,
            'estimated_emi': emi,
            'debt_to_income_ratio': dti_ratio,
            'loan_to_income_ratio': lti_ratio,
            'emi_to_income_ratio': emi / monthly_income if monthly_income > 0 else 1,
            'loan_purpose': loan_purpose,
            'employment_type': employment.employment_type,
            'city': customer.city
        }

        # Get ML prediction
        prediction = _get_ml_prediction(features)
        risk_probability = prediction['risk_probability']
        credit_score = prediction['credit_score']
        contributors = prediction.get('contributors', [])

        # Determine approval status
        risk_level = get_risk_level(risk_probability)
        recommendation = generate_recommendation(risk_probability, dti_ratio, lti_ratio, credit_score)

        if risk_probability > 0.60:
            status = 'Rejected'
        elif risk_probability > 0.45:
            status = 'Pending'
        else:
            status = 'Approved'

        processing_time = int((time.time() - start_time) * 1000)

        # Save application to database
        application = LoanApplication(
            customer_id=customer_id,
            loan_amount=loan_amount,
            loan_tenure_months=tenure_months,
            interest_rate=interest_rate,
            loan_purpose=loan_purpose,
            status=status,
            credit_score=credit_score,
            risk_probability=round(risk_probability, 4),
            risk_level=risk_level,
            recommendation=recommendation,
            ml_model_version=prediction.get('model_used', 'RF_v1.0'),
            processing_time_ms=processing_time
        )
        session.add(application)
        session.commit()

        return jsonify({
            'application_id': application.application_id,
            'customer_id': customer_id,
            'credit_score': credit_score,
            'risk_probability': round(risk_probability, 4),
            'risk_level': risk_level,
            'status': status,
            'recommendation': recommendation,
            'model_confidence': round(risk_probability, 4),
            'contributors': contributors,
            'factors': {
                'debt_to_income_ratio': round(dti_ratio * 100, 2),
                'loan_to_income_ratio': round(lti_ratio, 2),
                'estimated_emi': emi,
                'monthly_income': monthly_income
            },
            'processing_time_ms': processing_time
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@loan_bp.route('/applications', methods=['GET'])
def get_applications():
    """Retrieve loan applications with optional filtering."""
    session = get_db_session()
    try:
        query = session.query(LoanApplication)

        # Apply filters
        status = request.args.get('status')
        if status:
            query = query.filter(LoanApplication.status == status)

        customer_id = request.args.get('customer_id', type=int)
        if customer_id:
            query = query.filter(LoanApplication.customer_id == customer_id)

        # Pagination
        limit = min(request.args.get('limit', 100, type=int), 500)
        offset = max(request.args.get('offset', 0, type=int), 0)

        applications = query.order_by(LoanApplication.application_date.desc())\
            .offset(offset).limit(limit).all()

        total = query.count()

        return jsonify({
            'applications': [a.to_dict() for a in applications],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@loan_bp.route('/loans', methods=['GET'])
def get_loans():
    """Retrieve all disbursed loans."""
    session = get_db_session()
    try:
        limit = min(request.args.get('limit', 100, type=int), 500)
        offset = max(request.args.get('offset', 0, type=int), 0)

        status = request.args.get('status')
        query = session.query(Loan)
        if status:
            query = query.filter(Loan.loan_status == status)

        loans = query.order_by(Loan.loan_id.desc())\
            .offset(offset).limit(limit).all()
        total = query.count()

        return jsonify({
            'loans': [l.to_dict() for l in loans],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
