"""
Real-time Credit Risk Prediction with SHAP Explainability.

Loads the trained Random Forest model, generates risk predictions,
and provides SHAP-based feature contribution explanations.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pandas as pd
import joblib
import config

# Global model cache (loaded once, reused for all predictions)
_model = None
_feature_columns = None
_shap_explainer = None


def _load_model():
    """Load model artifacts from disk (cached after first load)."""
    global _model, _feature_columns

    if _model is None:
        if not os.path.exists(config.MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {config.MODEL_PATH}. Run 'python ml/train_model.py' first."
            )

        _model = joblib.load(config.MODEL_PATH)
        _feature_columns = joblib.load(config.FEATURE_COLUMNS_PATH)
        print(f"📊 Model loaded: {len(_feature_columns)} features")

    return _model, _feature_columns


def _get_shap_explainer():
    """Create or return cached SHAP explainer."""
    global _shap_explainer

    if _shap_explainer is None:
        try:
            import shap
            model, _ = _load_model()
            _shap_explainer = shap.TreeExplainer(model)
        except ImportError:
            print("⚠️ SHAP not installed. Feature contributions unavailable.")
            return None

    return _shap_explainer


def _build_feature_vector(features, feature_columns):
    """
    Build a feature vector matching the training feature columns.
    Handles missing or new features gracefully.
    """
    # Calculate derived features if not present
    monthly_income = features.get('monthly_income', 50000)
    annual_income = features.get('annual_income', monthly_income * 12)
    loan_amount = features.get('loan_amount', 500000)
    tenure = features.get('loan_tenure_months', 36)
    interest_rate = features.get('interest_rate', 10)
    emi = features.get('estimated_emi', 0)
    experience = features.get('years_of_experience', 5)
    age = features.get('age', 35)

    # EMI calculation if not provided
    if emi == 0:
        r = interest_rate / (12 * 100)
        if r > 0:
            emi = loan_amount * r * (1 + r) ** tenure / ((1 + r) ** tenure - 1)
        else:
            emi = loan_amount / tenure

    # Build full feature dictionary
    full_features = {
        'loan_amount': loan_amount,
        'loan_tenure_months': tenure,
        'interest_rate': interest_rate,
        'monthly_income': monthly_income,
        'annual_income': annual_income,
        'years_of_experience': experience,
        'age': age,
        'estimated_emi': emi,
        'debt_to_income_ratio': emi / monthly_income if monthly_income > 0 else 1,
        'loan_to_income_ratio': loan_amount / annual_income if annual_income > 0 else 10,
        'emi_to_income_ratio': emi / monthly_income if monthly_income > 0 else 1,
        'loan_per_month': loan_amount / tenure,
        'total_interest': emi * tenure - loan_amount,
        'interest_to_principal': (emi * tenure - loan_amount) / loan_amount if loan_amount > 0 else 0,
        'income_per_year_exp': monthly_income / experience if experience > 0 else monthly_income,
        'log_income': np.log1p(monthly_income),
        'log_loan_amount': np.log1p(loan_amount),
        'high_dti_flag': 1 if (emi / monthly_income if monthly_income > 0 else 1) > 0.40 else 0,
        'high_lti_flag': 1 if (loan_amount / annual_income if annual_income > 0 else 10) > 5 else 0,
        'high_interest_flag': 1 if interest_rate > 12 else 0,
        'young_borrower_flag': 1 if age < 25 else 0,
        'low_experience_flag': 1 if experience < 2 else 0,
    }

    # Handle one-hot encoded features
    loan_purpose = features.get('loan_purpose', '')
    employment_type = features.get('employment_type', '')
    for col in feature_columns:
        if col.startswith('purpose_') and col == f'purpose_{loan_purpose}':
            full_features[col] = 1
        elif col.startswith('purpose_'):
            full_features[col] = full_features.get(col, 0)
        elif col.startswith('emp_type_') and col == f'emp_type_{employment_type}':
            full_features[col] = 1
        elif col.startswith('emp_type_'):
            full_features[col] = full_features.get(col, 0)

    # Build vector in correct column order
    vector = []
    for col in feature_columns:
        vector.append(full_features.get(col, 0))

    return np.array(vector).reshape(1, -1)


def predict_risk(features):
    """
    Generate credit risk prediction with SHAP explanations.

    Args:
        features (dict): Customer and loan features

    Returns:
        dict: {
            'risk_probability': float (0-1),
            'credit_score': float (300-850),
            'contributors': list of {feature, impact},
            'model_used': str
        }
    """
    model, feature_columns = _load_model()

    # Build feature vector
    X = _build_feature_vector(features, feature_columns)

    # Model prediction
    risk_probability = float(model.predict_proba(X)[0][1])

    # Credit score (inverse mapping)
    from backend.utils.calculations import risk_probability_to_credit_score
    credit_score = risk_probability_to_credit_score(risk_probability)

    # SHAP explanations
    contributors = []
    explainer = _get_shap_explainer()
    if explainer is not None:
        try:
            shap_values = explainer.shap_values(X)
            # For binary classification, use class 1 (high risk) SHAP values
            if isinstance(shap_values, list):
                contributions = shap_values[1][0]
            else:
                contributions = shap_values[0]

            # Sort by absolute impact
            feature_impacts = sorted(
                zip(feature_columns, contributions),
                key=lambda x: abs(x[1]),
                reverse=True
            )

            # Return top 5 contributors
            for feat, impact in feature_impacts[:5]:
                contributors.append({
                    'feature': feat,
                    'impact': round(float(impact), 4)
                })
        except Exception as e:
            print(f"⚠️ SHAP explanation failed: {e}")
            # Fallback: use feature importance
            importances = model.feature_importances_
            top_features = sorted(
                zip(feature_columns, importances),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for feat, imp in top_features:
                contributors.append({
                    'feature': feat,
                    'impact': round(float(imp) * (1 if risk_probability > 0.5 else -1), 4)
                })

    return {
        'risk_probability': risk_probability,
        'credit_score': credit_score,
        'contributors': contributors,
        'model_used': 'RF_v1.0'
    }


if __name__ == '__main__':
    # Test prediction with sample data
    sample = {
        'loan_amount': 3500000,
        'loan_tenure_months': 36,
        'interest_rate': 9.5,
        'monthly_income': 75000,
        'years_of_experience': 8,
        'age': 35,
        'loan_purpose': 'Home Renovation',
        'employment_type': 'Salaried',
        'city': 'Bangalore'
    }

    print("🔮 Testing prediction with sample data...")
    result = predict_risk(sample)
    print(f"\n   Risk Probability: {result['risk_probability']:.4f}")
    print(f"   Credit Score:     {result['credit_score']}")
    print(f"   Model:            {result['model_used']}")
    print(f"\n   Top Contributors:")
    for c in result['contributors']:
        direction = "↑ risk" if c['impact'] > 0 else "↓ risk"
        print(f"     {c['feature']:<30} {c['impact']:+.4f}  ({direction})")
