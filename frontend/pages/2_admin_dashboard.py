"""
Admin Dashboard — Portfolio Analytics & Risk Monitoring.

Displays comprehensive portfolio health metrics including:
- Key performance indicators
- NPA analysis with classification breakdown
- Repayment performance tracking
- Visual analytics with Plotly charts
"""

import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px

# ─── Page Configuration ──────────────────────────────────────────
st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")

API_BASE_URL = "http://localhost:5000/api"

st.title("📊 Admin Dashboard")
st.markdown("Real-time portfolio health monitoring and risk analytics.")
st.divider()


def fetch_data(endpoint):
    """Fetch data from the Flask API."""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.ConnectionError:
        return None


# ─── Check API connectivity ──────────────────────────────────────
try:
    health = requests.get("http://localhost:5000/health", timeout=5)
    api_connected = health.status_code == 200
except Exception:
    api_connected = False

if not api_connected:
    st.error("""
    ❌ **Cannot connect to the API server.**

    Please start the Flask backend first:
    ```
    python backend/app.py
    ```
    """)
    st.stop()

# ─── Fetch All Data ──────────────────────────────────────────────
with st.spinner("Loading dashboard data..."):
    summary = fetch_data("portfolio/summary")
    npa_data = fetch_data("portfolio/npa-analysis")
    repayment_data = fetch_data("portfolio/repayment-stats")

if not summary:
    st.error("Failed to fetch portfolio data. Please check the API.")
    st.stop()

# ───────────────────────────────────────────────────────────────────
# SECTION 1: KEY PERFORMANCE INDICATORS
# ───────────────────────────────────────────────────────────────────
st.header("🎯 Key Performance Indicators")

loan_stats = summary.get('loan_statistics', {})
fin_metrics = summary.get('financial_metrics', {})
risk_metrics = summary.get('risk_metrics', {})

# Row 1: Loan KPIs
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Total Applications", f"{loan_stats.get('total_applications', 0):,}")
with k2:
    st.metric("Active Loans", f"{loan_stats.get('active_loans', 0):,}")
with k3:
    st.metric("Approval Rate", f"{loan_stats.get('approval_rate', 0):.1f}%")
with k4:
    default_rate = risk_metrics.get('default_rate', 0)
    st.metric("Default Rate", f"{default_rate:.1f}%",
             delta="⚠️ Above threshold" if default_rate > 10 else "✅ Normal",
             delta_color="inverse" if default_rate > 10 else "normal")

# Row 2: Financial KPIs
k5, k6, k7, k8 = st.columns(4)
with k5:
    disbursed = fin_metrics.get('total_disbursed', 0)
    st.metric("Total Disbursed", f"₹{disbursed / 10000000:.1f} Cr")
with k6:
    outstanding = fin_metrics.get('total_outstanding', 0)
    st.metric("Outstanding", f"₹{outstanding / 10000000:.1f} Cr")
with k7:
    npa_ratio = risk_metrics.get('npa_ratio', 0)
    st.metric("NPA Ratio", f"{npa_ratio:.1f}%",
             delta="🚨 Critical" if npa_ratio > 5 else "✅ Healthy",
             delta_color="inverse" if npa_ratio > 5 else "normal")
with k8:
    payment_rate = risk_metrics.get('average_emi_payment_rate', 0)
    st.metric("EMI Payment Rate", f"{payment_rate:.1f}%")

# ─── Alert Banner ───────────────────────────────────────────────
alerts = []
if npa_ratio > 5:
    alerts.append(f"⚠️ NPA Ratio ({npa_ratio:.1f}%) exceeds regulatory threshold of 5%")
if default_rate > 10:
    alerts.append(f"⚠️ Default Rate ({default_rate:.1f}%) exceeds threshold of 10%")
if payment_rate < 80:
    alerts.append(f"⚠️ EMI Payment Rate ({payment_rate:.1f}%) is below 80%")

if alerts:
    st.divider()
    for alert in alerts:
        st.warning(alert)

st.divider()

# ───────────────────────────────────────────────────────────────────
# SECTION 2: PORTFOLIO VISUALIZATIONS
# ───────────────────────────────────────────────────────────────────
st.header("📈 Portfolio Analytics")

vis_col1, vis_col2 = st.columns(2)

# ─── Loan Status Distribution (Pie Chart) ───────────────────────
with vis_col1:
    st.subheader("Loan Status Distribution")

    labels = ['Active', 'Closed', 'Defaulted']
    values = [
        loan_stats.get('active_loans', 0),
        loan_stats.get('closed_loans', 0),
        loan_stats.get('defaulted_loans', 0)
    ]
    colors = ['#66bb6a', '#42a5f5', '#ef5350']

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        hole=0.45,
        marker_colors=colors,
        textfont_size=14,
        textinfo='label+percent'
    )])
    fig.update_layout(
        height=350, margin=dict(t=30, b=10, l=10, r=10),
        template='plotly_white',
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

# ─── Financial Breakdown (Bar Chart) ────────────────────────────
with vis_col2:
    st.subheader("Financial Breakdown")

    categories = ['Disbursed', 'Outstanding', 'Repaid', 'NPA Amount']
    amounts = [
        fin_metrics.get('total_disbursed', 0) / 10000000,
        fin_metrics.get('total_outstanding', 0) / 10000000,
        fin_metrics.get('total_repaid', 0) / 10000000,
        fin_metrics.get('total_npa_amount', 0) / 10000000
    ]
    colors = ['#5c6bc0', '#ffa726', '#66bb6a', '#ef5350']

    fig = go.Figure(data=[go.Bar(
        x=categories, y=amounts,
        marker_color=colors,
        text=[f"₹{a:.1f} Cr" for a in amounts],
        textposition='outside'
    )])
    fig.update_layout(
        yaxis_title="Amount (₹ Crores)",
        height=350, margin=dict(t=30, b=10, l=10, r=10),
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ───────────────────────────────────────────────────────────────────
# SECTION 3: NPA ANALYSIS
# ───────────────────────────────────────────────────────────────────
st.header("🔍 NPA Analysis")

if npa_data:
    npa_classification = npa_data.get('npa_classification', {})

    npa_col1, npa_col2 = st.columns(2)

    with npa_col1:
        st.subheader("NPA Classification")

        categories = list(npa_classification.keys())
        counts = [npa_classification[c]['count'] for c in categories]
        percentages = [npa_classification[c]['percentage'] for c in categories]

        npa_colors = {
            'Standard': '#66bb6a',
            'Sub-Standard': '#ffa726',
            'Doubtful': '#ef5350',
            'Loss': '#b71c1c'
        }

        fig = go.Figure(data=[go.Bar(
            x=categories, y=counts,
            marker_color=[npa_colors.get(c, '#999') for c in categories],
            text=[f"{p:.1f}%" for p in percentages],
            textposition='outside'
        )])
        fig.update_layout(
            yaxis_title="Number of Loans",
            height=350, margin=dict(t=30, b=10, l=10, r=10),
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

    with npa_col2:
        st.subheader("NPA Summary")

        for cat in categories:
            data = npa_classification[cat]
            if cat == 'Standard':
                st.success(f"**{cat}**: {data['count']} loans ({data['percentage']:.1f}%)")
            elif cat == 'Sub-Standard':
                st.warning(f"**{cat}**: {data['count']} loans ({data['percentage']:.1f}%)")
            else:
                st.error(f"**{cat}**: {data['count']} loans ({data['percentage']:.1f}%)")

        st.divider()
        st.metric("Total NPA Loans", npa_data.get('total_npa_loans', 0))

st.divider()

# ───────────────────────────────────────────────────────────────────
# SECTION 4: REPAYMENT PERFORMANCE
# ───────────────────────────────────────────────────────────────────
st.header("💳 Repayment Performance")

if repayment_data:
    rep_summary = repayment_data.get('repayment_summary', {})
    fin_summary = repayment_data.get('financial_summary', {})

    rep_col1, rep_col2 = st.columns(2)

    with rep_col1:
        st.subheader("Payment Status Distribution")

        statuses = ['On-Time', 'Overdue', 'Partial', 'Pending']
        status_counts = [
            rep_summary.get('on_time_payments', 0),
            rep_summary.get('overdue_payments', 0),
            rep_summary.get('partial_payments', 0),
            rep_summary.get('pending_payments', 0)
        ]
        status_colors = ['#66bb6a', '#ef5350', '#ffa726', '#bdbdbd']

        fig = go.Figure(data=[go.Pie(
            labels=statuses, values=status_counts,
            hole=0.4,
            marker_colors=status_colors,
            textinfo='label+percent'
        )])
        fig.update_layout(
            height=350, margin=dict(t=30, b=10, l=10, r=10),
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

    with rep_col2:
        st.subheader("Collection Metrics")

        r1, r2 = st.columns(2)
        with r1:
            st.metric("Total Payments", f"{rep_summary.get('total_payments', 0):,}")
            st.metric("On-Time %", f"{rep_summary.get('on_time_percentage', 0):.1f}%")
        with r2:
            efficiency = fin_summary.get('collection_efficiency', 0)
            st.metric("Collection Efficiency", f"{efficiency:.1f}%")
            penalties = fin_summary.get('total_penalties', 0)
            st.metric("Total Penalties", f"₹{penalties / 100000:.1f} Lakhs")

st.divider()

# ─── Footer ──────────────────────────────────────────────────────
st.caption("Dashboard auto-refreshes when data changes. Click 'Rerun' to refresh manually.")
