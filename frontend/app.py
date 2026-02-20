"""
Credit Risk Assessment System — Streamlit Home Page.

Main entry point for the Streamlit dashboard application.
"""

import streamlit as st

# ─── Page Configuration ──────────────────────────────────────────
st.set_page_config(
    page_title="Credit Risk Assessment System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 0.8rem;
    }
    .tech-badge {
        display: inline-block;
        background: #e8eaf6;
        color: #3949ab;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────
st.markdown('<p class="main-header">🏦 Credit Risk Assessment System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">ML-Powered Loan Decisioning & Portfolio Management</p>', unsafe_allow_html=True)

st.divider()

# ─── Key Metrics ─────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="🎯 Model Accuracy", value="~94%", delta="Random Forest")
with col2:
    st.metric(label="📊 Features", value="28", delta="Engineered")
with col3:
    st.metric(label="🗄️ Database Tables", value="9", delta="PostgreSQL")
with col4:
    st.metric(label="🔌 API Endpoints", value="11", delta="RESTful")

st.divider()

# ─── Features Overview ──────────────────────────────────────────
st.header("✨ Key Features")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🧠 ML-Powered Credit Scoring")
    st.markdown("""
    - Random Forest classifier trained on **28 financial features**
    - Real-time risk probability calculation (0-100%)
    - **SHAP integration** for model explainability
    - Credit score generation on industry-standard **300-850 scale**
    """)

    st.subheader("📊 Financial Risk Metrics")
    st.markdown("""
    - **NPA tracking**: Flags loans overdue 90+ days
    - **DTI ratio**: Monthly debt burden vs. income
    - **LTI ratio**: Loan size relative to annual income
    - **EMI calculation** using compound interest formula
    """)

with col2:
    st.subheader("🔌 RESTful API Backend")
    st.markdown("""
    - **11 production-ready endpoints** following REST principles
    - Customer registration and KYC data management
    - Loan application with instant ML predictions
    - Portfolio analytics (NPA, repayment stats)
    """)

    st.subheader("📈 Interactive Dashboard")
    st.markdown("""
    - Loan application form with **real-time ML predictions**
    - Admin dashboard with **Plotly visualizations**
    - Real-time alerts for regulatory thresholds
    - Repayment performance tracking
    """)

st.divider()

# ─── Technology Stack ─────────────────────────────────────────────
st.header("🛠️ Technology Stack")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Backend")
    st.markdown("""
    - **Flask 3.1** — REST API framework
    - **SQLAlchemy 2.0** — ORM with connection pooling
    - **PostgreSQL** — Production RDBMS
    """)

with col2:
    st.subheader("Machine Learning")
    st.markdown("""
    - **scikit-learn** — Random Forest Classifier
    - **SHAP** — Model explainability
    - **pandas / numpy** — Data processing
    """)

with col3:
    st.subheader("Frontend")
    st.markdown("""
    - **Streamlit** — Interactive web app
    - **Plotly** — Data visualizations
    - **Matplotlib** — SHAP plots
    """)

st.divider()

# ─── Navigation ──────────────────────────────────────────────────
st.header("🚀 Get Started")
st.markdown("""
Use the **sidebar** to navigate between pages:

1. **📝 Loan Application** — Submit a loan application and get instant ML predictions
2. **📊 Admin Dashboard** — View portfolio health, NPA analysis, and risk metrics
""")

# ─── Footer ──────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 0.85rem;">
    Built with Python • Flask • PostgreSQL • scikit-learn • Streamlit
</div>
""", unsafe_allow_html=True)
