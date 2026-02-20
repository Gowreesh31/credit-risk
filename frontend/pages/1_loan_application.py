"""
Loan Application Page — Submit loan applications with real-time ML predictions.

Provides an interactive form where users can submit loan applications
and receive instant credit risk assessments with SHAP explanations.
"""

import streamlit as st
import requests
import plotly.graph_objects as go

# ─── Page Configuration ──────────────────────────────────────────
st.set_page_config(page_title="Loan Application", page_icon="📝", layout="wide")

API_BASE_URL = "http://localhost:5001/api"

st.title("📝 Loan Application")
st.markdown("Submit a new loan application and receive instant ML-powered risk assessment.")
st.divider()

# ─── Application Form ───────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Application Details")

    customer_id = st.number_input(
        "Customer ID",
        min_value=1, max_value=10000, value=1,
        help="Enter the registered customer ID"
    )

    loan_amount = st.number_input(
        "Loan Amount (₹)",
        min_value=100000, max_value=50000000, value=2000000, step=100000,
        help="Loan amount in Indian Rupees"
    )

    loan_tenure = st.selectbox(
        "Loan Tenure (months)",
        options=[12, 24, 36, 48, 60, 72, 84, 120, 180, 240],
        index=2,
        help="Loan repayment period"
    )

    interest_rate = st.slider(
        "Interest Rate (%)",
        min_value=7.0, max_value=15.0, value=9.5, step=0.25,
        help="Annual interest rate"
    )

    loan_purpose = st.selectbox(
        "Loan Purpose",
        options=[
            'Home Purchase', 'Home Renovation', 'Vehicle Loan', 'Education',
            'Business Expansion', 'Personal', 'Medical Emergency',
            'Debt Consolidation', 'Wedding', 'Travel'
        ],
        index=0
    )

    st.divider()
    submit_button = st.button("🚀 Submit Application", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 ML Prediction Results")

    if submit_button:
        # Prepare request payload
        payload = {
            "customer_id": customer_id,
            "loan_amount": loan_amount,
            "loan_tenure_months": loan_tenure,
            "interest_rate": interest_rate,
            "loan_purpose": loan_purpose
        }

        try:
            with st.spinner("🔮 Analyzing credit risk..."):
                response = requests.post(f"{API_BASE_URL}/loans/apply", json=payload, timeout=30)

            if response.status_code == 201:
                result = response.json()

                # ─── Status Banner ──────────────────────────────
                status = result['status']
                if status == 'Approved':
                    st.success(f"✅ Application **APPROVED** — {result['recommendation']}")
                elif status == 'Rejected':
                    st.error(f"❌ Application **REJECTED** — {result['recommendation']}")
                else:
                    st.warning(f"⏳ Application **PENDING** — {result['recommendation']}")

                # ─── Key Metrics ────────────────────────────────
                m1, m2, m3 = st.columns(3)
                with m1:
                    score = result.get('credit_score', 0)
                    score_color = "normal" if score >= 650 else "off" if score >= 500 else "inverse"
                    st.metric("Credit Score", f"{score:.0f}", delta=f"{'Good' if score >= 650 else 'Fair' if score >= 500 else 'Poor'}")
                with m2:
                    risk = result.get('risk_probability', 0)
                    st.metric("Risk Probability", f"{risk:.1%}")
                with m3:
                    st.metric("Risk Level", result.get('risk_level', 'N/A'))

                # ─── Financial Factors ──────────────────────────
                st.divider()
                st.subheader("💰 Financial Factors")
                factors = result.get('factors', {})
                f1, f2, f3 = st.columns(3)
                with f1:
                    dti = factors.get('debt_to_income_ratio', 0)
                    st.metric("DTI Ratio", f"{dti:.1f}%",
                             delta="⚠️ High" if dti > 40 else "✅ Safe")
                with f2:
                    lti = factors.get('loan_to_income_ratio', 0)
                    st.metric("LTI Ratio", f"{lti:.2f}x")
                with f3:
                    emi = factors.get('estimated_emi', 0)
                    st.metric("Monthly EMI", f"₹{emi:,.0f}")

                # ─── SHAP Feature Contributions ─────────────────
                contributors = result.get('contributors', [])
                if contributors:
                    st.divider()
                    st.subheader("🔍 SHAP Feature Contributions")
                    st.caption("How each feature influenced the risk decision")

                    # Create waterfall-style chart
                    features = [c['feature'] for c in contributors]
                    impacts = [c['impact'] for c in contributors]
                    colors = ['#ef5350' if i > 0 else '#66bb6a' for i in impacts]

                    fig = go.Figure(go.Bar(
                        x=impacts,
                        y=features,
                        orientation='h',
                        marker_color=colors,
                        text=[f"{i:+.4f}" for i in impacts],
                        textposition='outside'
                    ))
                    fig.update_layout(
                        title="Feature Impact on Risk Decision",
                        xaxis_title="SHAP Impact (+ = higher risk, - = lower risk)",
                        yaxis_title="Feature",
                        height=350,
                        margin=dict(l=10, r=10, t=40, b=10),
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # ─── Application Details ────────────────────────
                st.divider()
                st.subheader("📄 Application Record")
                st.json({
                    'application_id': result.get('application_id'),
                    'customer_id': result.get('customer_id'),
                    'credit_score': result.get('credit_score'),
                    'risk_probability': result.get('risk_probability'),
                    'status': result.get('status'),
                    'processing_time_ms': result.get('processing_time_ms')
                })

            elif response.status_code == 404:
                st.error(f"❌ {response.json().get('error', 'Customer not found')}")
            else:
                st.error(f"❌ API Error: {response.json().get('error', 'Unknown error')}")

        except requests.exceptions.ConnectionError:
            st.error("""
            ❌ **Cannot connect to the API server.**

            Please ensure the Flask backend is running:
            ```
            python backend/app.py
            ```
            """)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    else:
        st.info("👈 Fill in the application form and click **Submit Application** to get ML predictions.")

        # Show sample info
        st.divider()
        st.subheader("ℹ️ How It Works")
        st.markdown("""
        1. Enter the customer ID and loan details
        2. Click **Submit Application**
        3. The system instantly:
           - Calculates financial ratios (DTI, LTI, EMI)
           - Runs the Random Forest ML model
           - Generates SHAP explanations
           - Returns credit score, risk level, and recommendation
        """)
