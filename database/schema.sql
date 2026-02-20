-- ============================================================
-- Credit Risk Assessment System — Database Schema
-- PostgreSQL 12+
-- Creates 9 normalized tables with referential integrity
-- ============================================================

-- Drop tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS npa_tracking CASCADE;
DROP TABLE IF EXISTS repayments CASCADE;
DROP TABLE IF EXISTS disbursements CASCADE;
DROP TABLE IF EXISTS collateral CASCADE;
DROP TABLE IF EXISTS guarantors CASCADE;
DROP TABLE IF EXISTS loans CASCADE;
DROP TABLE IF EXISTS loan_applications CASCADE;
DROP TABLE IF EXISTS employment_details CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- ─── 1. CUSTOMERS ──────────────────────────────────────────────
CREATE TABLE customers (
    customer_id     SERIAL PRIMARY KEY,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    date_of_birth   DATE NOT NULL,
    gender          VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
    email           VARCHAR(200) UNIQUE NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    address         TEXT,
    city            VARCHAR(100),
    state           VARCHAR(100),
    pincode         VARCHAR(10),
    pan_number      VARCHAR(10) UNIQUE,
    aadhar_number   VARCHAR(12) UNIQUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_city ON customers(city);

-- ─── 2. EMPLOYMENT DETAILS ─────────────────────────────────────
CREATE TABLE employment_details (
    employment_id       SERIAL PRIMARY KEY,
    customer_id         INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    employer_name       VARCHAR(200),
    employment_type     VARCHAR(50) CHECK (employment_type IN ('Salaried', 'Self-Employed', 'Business', 'Freelancer', 'Retired')),
    designation         VARCHAR(100),
    monthly_income      NUMERIC(15, 2) NOT NULL,
    years_of_experience NUMERIC(5, 2) DEFAULT 0,
    office_address      TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_employment_customer ON employment_details(customer_id);

-- ─── 3. LOAN APPLICATIONS ──────────────────────────────────────
CREATE TABLE loan_applications (
    application_id      SERIAL PRIMARY KEY,
    customer_id         INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    loan_amount         NUMERIC(15, 2) NOT NULL,
    loan_tenure_months  INTEGER NOT NULL,
    interest_rate       NUMERIC(5, 2) NOT NULL,
    loan_purpose        VARCHAR(100),
    application_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status              VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    credit_score        NUMERIC(6, 2),
    risk_probability    NUMERIC(6, 4),
    risk_level          VARCHAR(20),
    recommendation      TEXT,
    ml_model_version    VARCHAR(50),
    processing_time_ms  INTEGER,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_applications_customer ON loan_applications(customer_id);
CREATE INDEX idx_applications_status ON loan_applications(status);
CREATE INDEX idx_applications_date ON loan_applications(application_date);

-- ─── 4. LOANS ───────────────────────────────────────────────────
CREATE TABLE loans (
    loan_id             SERIAL PRIMARY KEY,
    application_id      INTEGER REFERENCES loan_applications(application_id) ON DELETE CASCADE,
    customer_id         INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    loan_amount         NUMERIC(15, 2) NOT NULL,
    disbursed_amount    NUMERIC(15, 2),
    interest_rate       NUMERIC(5, 2) NOT NULL,
    tenure_months       INTEGER NOT NULL,
    emi_amount          NUMERIC(15, 2),
    loan_start_date     DATE,
    loan_end_date       DATE,
    loan_status         VARCHAR(20) DEFAULT 'Active' CHECK (loan_status IN ('Active', 'Closed', 'Defaulted', 'Written-Off')),
    outstanding_amount  NUMERIC(15, 2),
    total_paid          NUMERIC(15, 2) DEFAULT 0,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_loans_customer ON loans(customer_id);
CREATE INDEX idx_loans_status ON loans(loan_status);
CREATE INDEX idx_loans_application ON loans(application_id);

-- ─── 5. DISBURSEMENTS ───────────────────────────────────────────
CREATE TABLE disbursements (
    disbursement_id     SERIAL PRIMARY KEY,
    loan_id             INTEGER NOT NULL REFERENCES loans(loan_id) ON DELETE CASCADE,
    disbursement_date   DATE NOT NULL,
    amount              NUMERIC(15, 2) NOT NULL,
    payment_mode        VARCHAR(50) CHECK (payment_mode IN ('NEFT', 'RTGS', 'IMPS', 'Cheque', 'Direct')),
    reference_number    VARCHAR(100),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_disbursements_loan ON disbursements(loan_id);

-- ─── 6. REPAYMENTS ──────────────────────────────────────────────
CREATE TABLE repayments (
    repayment_id        SERIAL PRIMARY KEY,
    loan_id             INTEGER NOT NULL REFERENCES loans(loan_id) ON DELETE CASCADE,
    due_date            DATE NOT NULL,
    payment_date        DATE,
    emi_amount          NUMERIC(15, 2) NOT NULL,
    principal_component NUMERIC(15, 2),
    interest_component  NUMERIC(15, 2),
    amount_paid         NUMERIC(15, 2) DEFAULT 0,
    payment_status      VARCHAR(20) DEFAULT 'Pending' CHECK (payment_status IN ('Pending', 'Paid', 'Overdue', 'Partial')),
    days_overdue        INTEGER DEFAULT 0,
    penalty_amount      NUMERIC(15, 2) DEFAULT 0,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_repayments_loan ON repayments(loan_id);
CREATE INDEX idx_repayments_status ON repayments(payment_status);
CREATE INDEX idx_repayments_due_date ON repayments(due_date);

-- ─── 7. COLLATERAL ──────────────────────────────────────────────
CREATE TABLE collateral (
    collateral_id       SERIAL PRIMARY KEY,
    loan_id             INTEGER NOT NULL REFERENCES loans(loan_id) ON DELETE CASCADE,
    collateral_type     VARCHAR(100),
    description         TEXT,
    estimated_value     NUMERIC(15, 2),
    valuation_date      DATE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_collateral_loan ON collateral(loan_id);

-- ─── 8. GUARANTORS ──────────────────────────────────────────────
CREATE TABLE guarantors (
    guarantor_id        SERIAL PRIMARY KEY,
    loan_id             INTEGER NOT NULL REFERENCES loans(loan_id) ON DELETE CASCADE,
    full_name           VARCHAR(200) NOT NULL,
    relationship        VARCHAR(100),
    phone               VARCHAR(20),
    email               VARCHAR(200),
    monthly_income      NUMERIC(15, 2),
    address             TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_guarantors_loan ON guarantors(loan_id);

-- ─── 9. NPA TRACKING ────────────────────────────────────────────
CREATE TABLE npa_tracking (
    npa_id              SERIAL PRIMARY KEY,
    loan_id             INTEGER NOT NULL REFERENCES loans(loan_id) ON DELETE CASCADE,
    npa_date            DATE NOT NULL,
    days_overdue        INTEGER NOT NULL,
    outstanding_amount  NUMERIC(15, 2),
    npa_category        VARCHAR(20) CHECK (npa_category IN ('Standard', 'Sub-Standard', 'Doubtful', 'Loss')),
    provision_amount    NUMERIC(15, 2),
    resolution_status   VARCHAR(50) DEFAULT 'Open' CHECK (resolution_status IN ('Open', 'Resolved', 'Written-Off')),
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_npa_loan ON npa_tracking(loan_id);
CREATE INDEX idx_npa_category ON npa_tracking(npa_category);

-- ============================================================
-- Schema creation complete: 9 tables with referential integrity
-- ============================================================
