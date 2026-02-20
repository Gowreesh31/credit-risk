"""
Feature Engineering Module for Credit Risk ML Pipeline.

Engineers 28 features from raw loan and customer data for
the Random Forest classifier. Features include financial ratios,
risk indicators, and encoded categorical variables.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from datetime import datetime
import config


def fetch_training_data():
    """
    Fetch raw data from PostgreSQL for model training.
    Joins customers, employment, applications, and loans tables.
    """
    import psycopg2

    conn = psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )

    query = """
        SELECT
            la.application_id,
            la.customer_id,
            la.loan_amount,
            la.loan_tenure_months,
            la.interest_rate,
            la.loan_purpose,
            la.status,
            la.risk_probability,
            c.date_of_birth,
            c.gender,
            c.city,
            c.state,
            e.employment_type,
            e.monthly_income,
            e.years_of_experience,
            e.employer_name
        FROM loan_applications la
        JOIN customers c ON la.customer_id = c.customer_id
        LEFT JOIN employment_details e ON la.customer_id = e.customer_id
        WHERE la.status IN ('Approved', 'Rejected')
        AND e.monthly_income IS NOT NULL
        AND e.monthly_income > 0
    """

    df = pd.read_sql(query, conn)
    conn.close()

    print(f"📊 Fetched {len(df)} records from database")
    return df


def engineer_features(df):
    """
    Transform raw data into 28 ML-ready features.

    Feature categories:
    1. Financial ratios (DTI, LTI, EMI-to-income)
    2. Customer demographics (age, income, experience)
    3. Loan characteristics (amount, tenure, rate)
    4. Risk flags (binary indicators for high-risk conditions)
    5. One-hot encoded categoricals (purpose, employment type, city)
    """
    print("🔧 Engineering 28 features...")

    # ─── 1. Basic Loan Features ─────────────────────────────────
    df['loan_amount'] = df['loan_amount'].astype(float)
    df['loan_tenure_months'] = df['loan_tenure_months'].astype(int)
    df['interest_rate'] = df['interest_rate'].astype(float)
    df['monthly_income'] = df['monthly_income'].astype(float)
    df['years_of_experience'] = df['years_of_experience'].astype(float).fillna(0)

    # ─── 2. Age Calculation ─────────────────────────────────────
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
    df['age'] = (pd.Timestamp.now() - df['date_of_birth']).dt.days / 365.25
    df['age'] = df['age'].round(1)

    # ─── 3. Annual Income ──────────────────────────────────────
    df['annual_income'] = df['monthly_income'] * 12

    # ─── 4. EMI Calculation ─────────────────────────────────────
    def calc_emi(row):
        p = row['loan_amount']
        r = row['interest_rate'] / (12 * 100)
        n = row['loan_tenure_months']
        if r == 0:
            return p / n
        emi = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
        return round(emi, 2)

    df['estimated_emi'] = df.apply(calc_emi, axis=1)

    # ─── 5. Financial Ratios (core risk features) ───────────────
    df['debt_to_income_ratio'] = df['estimated_emi'] / df['monthly_income']
    df['loan_to_income_ratio'] = df['loan_amount'] / df['annual_income']
    df['emi_to_income_ratio'] = df['estimated_emi'] / df['monthly_income']
    df['loan_per_month'] = df['loan_amount'] / df['loan_tenure_months']

    # ─── 6. Interest Burden ─────────────────────────────────────
    df['total_interest'] = df['estimated_emi'] * df['loan_tenure_months'] - df['loan_amount']
    df['interest_to_principal'] = df['total_interest'] / df['loan_amount']

    # ─── 7. Income-Based Features ───────────────────────────────
    df['income_per_year_exp'] = np.where(
        df['years_of_experience'] > 0,
        df['monthly_income'] / df['years_of_experience'],
        df['monthly_income']
    )
    df['log_income'] = np.log1p(df['monthly_income'])
    df['log_loan_amount'] = np.log1p(df['loan_amount'])

    # ─── 8. Risk Flags (binary indicators) ──────────────────────
    df['high_dti_flag'] = (df['debt_to_income_ratio'] > 0.40).astype(int)
    df['high_lti_flag'] = (df['loan_to_income_ratio'] > 5).astype(int)
    df['high_interest_flag'] = (df['interest_rate'] > 12).astype(int)
    df['young_borrower_flag'] = (df['age'] < 25).astype(int)
    df['low_experience_flag'] = (df['years_of_experience'] < 2).astype(int)

    # ─── 9. Target Variable ────────────────────────────────────
    # High risk = 1 (rejected or high risk probability)
    # Low risk = 0 (approved with low risk)
    df['is_high_risk'] = np.where(
        df['risk_probability'].astype(float) > 0.5, 1, 0
    )

    # ─── 10. One-Hot Encoding ──────────────────────────────────
    # Loan purpose
    purpose_dummies = pd.get_dummies(df['loan_purpose'], prefix='purpose', dtype=int)
    # Keep top 5 purposes, combine rest into 'other'
    top_purposes = purpose_dummies.sum().nlargest(5).index
    for col in purpose_dummies.columns:
        if col not in top_purposes:
            purpose_dummies.drop(col, axis=1, inplace=True)

    # Employment type
    emp_dummies = pd.get_dummies(df['employment_type'], prefix='emp_type', dtype=int)

    # Combine
    df = pd.concat([df, purpose_dummies, emp_dummies], axis=1)

    print(f"   ✓ Created {len(get_feature_columns(df))} features")
    return df


def get_feature_columns(df):
    """Return the list of feature columns used for training."""
    # Core numeric features
    numeric_features = [
        'loan_amount', 'loan_tenure_months', 'interest_rate',
        'monthly_income', 'annual_income', 'years_of_experience', 'age',
        'estimated_emi', 'debt_to_income_ratio', 'loan_to_income_ratio',
        'emi_to_income_ratio', 'loan_per_month',
        'total_interest', 'interest_to_principal',
        'income_per_year_exp', 'log_income', 'log_loan_amount',
        'high_dti_flag', 'high_lti_flag', 'high_interest_flag',
        'young_borrower_flag', 'low_experience_flag'
    ]

    # One-hot encoded columns
    encoded_cols = [c for c in df.columns if c.startswith('purpose_') or c.startswith('emp_type_')]

    return numeric_features + encoded_cols


def prepare_training_data():
    """
    Full pipeline: fetch data → engineer features → return X, y, feature_columns.
    """
    df = fetch_training_data()
    df = engineer_features(df)

    feature_cols = get_feature_columns(df)
    X = df[feature_cols].fillna(0)
    y = df['is_high_risk']

    print(f"\n📋 Training Data Summary:")
    print(f"   Samples: {len(X)}")
    print(f"   Features: {len(feature_cols)}")
    print(f"   Target distribution:")
    print(f"     Low Risk (0): {(y == 0).sum()} ({(y == 0).mean():.1%})")
    print(f"     High Risk (1): {(y == 1).sum()} ({(y == 1).mean():.1%})")

    return X, y, feature_cols


if __name__ == '__main__':
    X, y, cols = prepare_training_data()
    print(f"\n✅ Feature engineering complete: {X.shape[0]} samples × {X.shape[1]} features")
    print(f"\nFeature columns:")
    for i, col in enumerate(cols, 1):
        print(f"   {i:2}. {col}")
