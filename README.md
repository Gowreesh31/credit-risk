# 🏦 Credit Risk Assessment & Loan Portfolio Management System

End-to-end enterprise credit risk system using **Random Forest** (~94% Accuracy), **Flask**, **PostgreSQL**, and **Streamlit**. Features real-time loan decisioning, NPA analytics, and a causal synthetic data pipeline.

---

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [ML Model Performance](#-ml-model-performance)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Design Decisions](#-design-decisions)
- [Future Enhancements](#-future-enhancements)

---

## 🎯 Project Overview

This system addresses the critical challenge of **manual loan underwriting** in financial institutions — a process that is slow, inconsistent, and vulnerable to human bias. Traditional credit assessment methods can take 3-5 business days and suffer from subjective decision-making.

### Business Impact
- **95% reduction in processing time**: From days to seconds for loan decisions
- **~94% prediction accuracy**: Validated with 5-fold cross-validation on stress-test scenarios
- **High recall rate**: Catches high-risk borrowers before default
- **Real-time portfolio monitoring**: Tracks ₹67+ Crores in disbursed loans with NPA ratio alerts
- **Regulatory compliance**: SHAP-based explanations for every rejection decision

### The Dataset Strategy
Rather than using randomly generated data, this system employs **causal synthetic data** where financial risk factors (Debt-to-Income ratio, Loan-to-Income ratio) directly determine default outcomes. This ensures the ML model learns genuine financial patterns rather than spurious correlations — validating that the #1 feature importance is `debt_to_income_ratio`, matching real-world banking theory.

---

## ✨ Key Features

### 1. ML-Powered Credit Scoring Engine
- Random Forest classifier trained on **28 financial features**
- ~94% test accuracy, high ROC-AUC score
- Real-time risk probability calculation (0-100%)
- **SHAP integration** for model explainability — satisfies regulatory requirements
- Credit score generation on industry-standard **300-850 scale**

### 2. Comprehensive Financial Risk Metrics
- **NPA (Non-Performing Asset) tracking**: Flags loans overdue 90+ days
- **Debt-to-Income (DTI) ratio**: Calculates monthly debt burden vs. income
- **Loan-to-Income (LTI) ratio**: Assesses total loan size relative to annual income
- **EMI calculation**: Computes Equated Monthly Installments using compound interest formula
- **Portfolio concentration risk**: Monitors exposure by loan purpose

### 3. RESTful API Backend
- **11 production-ready endpoints** following REST principles
- Customer registration and KYC data management
- Loan application submission with instant ML predictions
- Portfolio analytics API (NPA analysis, repayment statistics, risk distribution)
- Comprehensive error handling with HTTP status codes

### 4. Interactive Analytics Dashboard
- Loan application interface with real-time ML predictions and SHAP explanations
- Admin dashboard with **Plotly visualizations** (portfolio health, default trends)
- Real-time alerts for regulatory thresholds (NPA ratio > 5%, default rate > 10%)
- Repayment performance tracking

### 5. Production-Grade PostgreSQL Database
- **9 normalized tables** (3NF compliance): Customers, Employment, Applications, Loans, Disbursements, Repayments, Collateral, Guarantors, NPA Tracking
- Foreign key constraints ensuring referential integrity
- Indexes on search columns for query performance
- ACID transactions for financial data consistency

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                        │
│        (Loan Application Form + Admin Dashboard)            │
│   • Real-time ML Predictions    • SHAP Visualizations       │
│   • Portfolio Analytics         • Risk Alert Monitoring      │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST API
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                     FLASK API LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Customer    │  │     Loan     │  │   Portfolio     │   │
│  │   Routes      │  │    Routes    │  │    Routes       │   │
│  │  • Register   │  │  • Apply     │  │  • Summary      │   │
│  │  • Retrieve   │  │  • Approve   │  │  • NPA Analysis │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└────────────┬─────────────────────────┬──────────────────────┘
             │                         │
             ↓                         ↓
┌────────────────────────┐  ┌──────────────────────────────┐
│  ML PREDICTION MODULE  │  │     POSTGRESQL DATABASE      │
│                        │  │                              │
│  • Random Forest Model │  │  9 Normalized Tables:        │
│  • 28 Features         │  │  • customers                 │
│  • SHAP Explainer      │  │  • employment_details        │
│  • Feature Engineering │  │  • loan_applications         │
│                        │  │  • loans                     │
│  Financial Metrics:    │  │  • disbursements             │
│  • DTI Calculation     │  │  • repayments                │
│  • LTI Ratio           │  │  • collateral                │
│  • Risk Flags          │  │  • guarantors                │
│                        │  │  • npa_tracking              │
└────────────────────────┘  └──────────────────────────────┘
```

**Data Flow:**
1. User submits loan application via Streamlit UI
2. Flask API validates input and fetches customer data from PostgreSQL
3. ML module engineers 28 features and generates risk probability
4. SHAP explainer calculates feature contributions for decision transparency
5. System returns credit score, approval decision, and risk factors
6. Dashboard displays real-time portfolio health metrics

---

## 🛠️ Technology Stack

### Backend Framework
- **Flask 3.1.0** — Microframework for RESTful API development
- **SQLAlchemy 2.0.36** — ORM for database operations with connection pooling
- **psycopg2-binary 2.9.10** — PostgreSQL database adapter
- **Flask-CORS** — Cross-Origin Resource Sharing support

### Database
- **PostgreSQL 12+** — Production-grade RDBMS
  - 9 normalized tables with referential integrity
  - B-tree indexes on foreign keys and search columns
  - ACID compliance for transaction safety

### Machine Learning & Data Science
- **scikit-learn 1.6.0** — Random Forest Classifier, metrics, preprocessing
- **SHAP 0.44.0** — Model explainability (TreeExplainer for Random Forest)
- **pandas 2.2.3** — Data manipulation and feature engineering
- **numpy 2.2.1** — Numerical computations

### Frontend & Visualization
- **Streamlit 1.41.1** — Interactive web application framework
- **Plotly 5.24.1** — Professional data visualizations
- **Matplotlib** — SHAP waterfall plots

---

## 📊 ML Model Performance

### Training Configuration
```
Dataset Size:     1,500 loan applications (₹67+ Crores disbursed)
Training Set:     80%
Test Set:         20%
Features:         28 (after removing data leakage variables)
Algorithm:        Random Forest
                  • n_estimators: 100 trees
                  • max_depth: 10
                  • class_weight: 'balanced'
                  • random_state: 42
```

### Cross-Validation (5-Fold)
```
Mean Accuracy:    ~92-94% (varies with generated data)
Mean ROC-AUC:     ~95%
Overfitting:      Train-Test Gap < 3% (excellent generalization)
```

### Top Feature Importances
The model correctly prioritizes `debt_to_income_ratio` as the #1 feature, validating that it learned the causal relationship embedded in the synthetic data.

### Model Benchmarking
Random Forest vs Logistic Regression comparison shows:
1. **Precision Advantage**: Random Forest achieves higher precision → fewer false alarms
2. **Robustness**: Random Forest handles raw financial data without scaling
3. **Explainability**: SHAP integration for regulatory compliance

---

## 🚀 Installation

### Prerequisites
- Python 3.9+ ([Download](https://www.python.org/downloads/))
- PostgreSQL 12+ ([Download](https://www.postgresql.org/download/))
- Git ([Download](https://git-scm.com/downloads))

### Step 1: Clone Repository
```bash
git clone https://github.com/Gowreesh31/credit-risk.git
cd credit-risk
```

### Step 2: Create Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database
```sql
-- Start PostgreSQL and create database
psql -U postgres
CREATE DATABASE credit_risk_db;
\q

-- Run schema to create 9 tables
psql -U postgres -d credit_risk_db -f database/schema.sql
```

### Step 5: Update Configuration
Edit `config.py` and set your PostgreSQL credentials:
```python
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'credit_risk_db'
DB_USER = 'postgres'
DB_PASSWORD = 'your_password_here'  # Change this!
```

### Step 6: Seed Database with Causal Synthetic Data
```bash
python database/seed_data.py
```
When prompted, type `yes` to confirm. Expected output:
```
✓ Created 1000 customers
✓ Created 1500 applications (Approved: ~785, Rejected: ~500, Pending: ~215)
✓ Created ~785 loans (~80 defaulted based on risk probability)
✓ Created ~12,000+ repayment records
```

### Step 7: Train ML Model
```bash
python ml/train_model.py
```
Expected output:
```
✓ Training set: ~1,028 samples
✓ Test Accuracy: ~94%
✓ Test ROC-AUC: ~95%
✓ Model saved successfully
```

---

## 💻 Usage

### Start Backend API Server
```bash
python backend/app.py
```
The Flask API starts on `http://localhost:5000`:
```
============================================================
🚀 CREDIT RISK ASSESSMENT API STARTING
============================================================
📍 API running at: http://127.0.0.1:5000
📊 Database: credit_risk_db
🔍 Debug mode: True
============================================================
```

Health Check:
```bash
curl http://localhost:5000/health
# Response: {"status":"healthy","database":"connected"}
```

### Start Frontend Dashboard
Open a new terminal (keep Flask running):
```bash
streamlit run frontend/app.py
```
Streamlit opens automatically at `http://localhost:8501`

### Testing the System
```bash
# Submit a test loan application
curl -X POST http://localhost:5000/api/loans/apply \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 3500000,
    "loan_tenure_months": 36,
    "interest_rate": 9.5,
    "loan_purpose": "Home Renovation"
  }'
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `GET` | `/api/customers/` | List customers (paginated) |
| `GET` | `/api/customers/<id>` | Customer detail with employment |
| `POST` | `/api/customers/` | Register new customer |
| `POST` | `/api/loans/apply` | Submit loan application (ML prediction) |
| `GET` | `/api/loans/applications` | List applications (filterable) |
| `GET` | `/api/loans/loans` | List disbursed loans |
| `GET` | `/api/portfolio/summary` | Portfolio health metrics |
| `GET` | `/api/portfolio/npa-analysis` | NPA classification breakdown |
| `GET` | `/api/portfolio/repayment-stats` | Repayment performance |

---

## 📁 Project Structure

```
credit-risk-system/
│
├── backend/                    # Flask REST API
│   ├── app.py                  # Application entry point
│   ├── database.py             # SQLAlchemy connection management
│   ├── models.py               # ORM models for 9 tables
│   ├── routes/
│   │   ├── customer_routes.py  # Customer CRUD endpoints
│   │   ├── loan_routes.py      # Loan application & ML prediction
│   │   └── portfolio_routes.py # Portfolio analytics endpoints
│   └── utils/
│       └── calculations.py     # Financial formulas (EMI, NPA, DTI)
│
├── database/
│   ├── schema.sql              # PostgreSQL schema (9 tables)
│   └── seed_data.py            # Causal synthetic data generator
│
├── ml/                         # Machine Learning Pipeline
│   ├── data_prep.py            # Feature engineering (28 features)
│   ├── train_model.py          # Random Forest training pipeline
│   ├── predict.py              # Real-time prediction with SHAP
│   ├── compare_models.py       # Benchmarking (RF vs LR)
│   └── models/
│       └── credit_model.pkl    # Trained model (generated)
│
├── frontend/                   # Streamlit UI
│   ├── app.py                  # Home page & navigation
│   └── pages/
│       ├── 1_loan_application.py   # Loan form with ML predictions
│       └── 2_admin_dashboard.py    # Portfolio analytics dashboard
│
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── .gitignore                  # Git exclusions
```

---

## 🧠 Design Decisions

### Why Flask Over Django?
- **Microservices-friendly**: Flask's minimalist design is ideal for REST APIs
- **Flexibility**: Chose SQLAlchemy separately for connection pooling
- **Industry standard**: Flask is the framework of choice for ML model serving
- **ML integration**: Seamlessly integrates with scikit-learn

### Why PostgreSQL Over MySQL?
- **ACID compliance**: Stricter transactional guarantees for financial data
- **Advanced data types**: JSON columns and arrays for SHAP explanations
- **Concurrency**: Better handling of concurrent writes from multiple users
- **Fintech adoption**: Used by Stripe, Robinhood, Square

### Why Random Forest Over Neural Networks?
- **Precision advantage**: Higher precision means fewer wrongly rejected good borrowers
- **Robustness**: Handles raw financial data without preprocessing
- **Explainability**: Feature importance + SHAP for regulatory compliance
- **Training efficiency**: Fast training, no GPU required

### Why Causal Synthetic Data?
- Ensures ML model learns **genuine financial patterns**
- DTI ratio causally determines default → validates domain knowledge
- Avoids spurious correlations from random data
- Stress-tests the model on high-risk economic scenarios

---

## 🔮 Future Enhancements

### Phase 1: Advanced ML
- Gradient Boosted Trees (XGBoost/LightGBM) comparison
- Feature selection using recursive elimination
- Hyperparameter tuning with Optuna

### Phase 2: Production Hardening
- JWT token authentication
- Rate limiting and input sanitization
- Docker containerization
- CI/CD pipeline

### Phase 3: Advanced Analytics
- Time-series analysis for default trends
- Customer segmentation with clustering
- Real-time model monitoring and drift detection

---

## 👤 Author

**Gowreeswaran**
- GitHub: [@Gowreesh31](https://github.com/Gowreesh31)

---

## 📄 License

This project is for educational and portfolio purposes.

---

## 🙏 Acknowledgments
- scikit-learn documentation for ML best practices
- SHAP library for model explainability
- RBI guidelines for NPA classification norms
- Flask and Streamlit communities
