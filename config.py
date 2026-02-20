"""
Configuration settings for the Credit Risk Assessment System.
"""

# ─── Database Configuration ─────────────────────────────────────────
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'credit_risk_db'
DB_USER = 'postgres'
DB_PASSWORD = 'your_password_here'  # Change this!

# SQLAlchemy connection string
DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Connection pool settings
POOL_SIZE = 5
MAX_OVERFLOW = 10
POOL_TIMEOUT = 30

# ─── API Configuration ──────────────────────────────────────────────
API_HOST = '0.0.0.0'
API_PORT = 5000
DEBUG = True

# ─── ML Model Configuration ─────────────────────────────────────────
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'ml', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'credit_model.pkl')
FEATURE_COLUMNS_PATH = os.path.join(MODEL_DIR, 'feature_columns.pkl')

# ─── Credit Score Configuration ──────────────────────────────────────
CREDIT_SCORE_MIN = 300
CREDIT_SCORE_MAX = 850

# ─── Risk Thresholds ────────────────────────────────────────────────
DTI_THRESHOLD = 0.40        # Debt-to-Income ratio threshold (40%)
NPA_DAYS_THRESHOLD = 90     # Days overdue before NPA classification
DEFAULT_RISK_THRESHOLD = 0.5  # Probability threshold for high risk
