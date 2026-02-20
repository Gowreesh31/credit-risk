"""
Causal Synthetic Data Generator for Credit Risk System.

Generates realistic financial data where risk factors (DTI, LTI)
causally determine default outcomes — ensuring the ML model learns
genuine financial patterns rather than spurious correlations.
"""

import sys
import os
import random
import math
from datetime import datetime, timedelta
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from psycopg2.extras import execute_batch
import config

# ─── Random seed for reproducibility ────────────────────────────────
random.seed(42)

# ─── Constants ───────────────────────────────────────────────────────
INDIAN_FIRST_NAMES_MALE = [
    'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh',
    'Ayaan', 'Krishna', 'Ishaan', 'Shaurya', 'Atharv', 'Advik', 'Pranav',
    'Advaith', 'Aryan', 'Dhruv', 'Kabir', 'Ritvik', 'Aarush', 'Karthik',
    'Rahul', 'Amit', 'Suresh', 'Rajesh', 'Vikram', 'Deepak', 'Manoj',
    'Ravi', 'Sanjay', 'Nikhil', 'Ashwin', 'Rohan', 'Gaurav', 'Prateek'
]

INDIAN_FIRST_NAMES_FEMALE = [
    'Saanvi', 'Aanya', 'Aadhya', 'Aaradhya', 'Ananya', 'Pari', 'Anika',
    'Navya', 'Diya', 'Myra', 'Ira', 'Priya', 'Kavya', 'Tara', 'Sara',
    'Meera', 'Shreya', 'Pooja', 'Neha', 'Divya', 'Swati', 'Anjali',
    'Sunita', 'Lakshmi', 'Gayathri', 'Nandini', 'Harini', 'Sowmya',
    'Bhavya', 'Charitha', 'Deepika', 'Fathima', 'Geetha', 'Hema', 'Indira'
]

INDIAN_LAST_NAMES = [
    'Sharma', 'Verma', 'Patel', 'Reddy', 'Kumar', 'Singh', 'Gupta',
    'Iyer', 'Nair', 'Menon', 'Joshi', 'Desai', 'Shah', 'Mehta', 'Rao',
    'Pillai', 'Chauhan', 'Mishra', 'Pandey', 'Agarwal', 'Banerjee',
    'Mukherjee', 'Chatterjee', 'Bose', 'Das', 'Ghosh', 'Sen', 'Roy',
    'Kulkarni', 'Patil', 'Deshpande', 'Kadam', 'Naik', 'Hegde', 'Shetty'
]

CITIES = [
    ('Mumbai', 'Maharashtra'), ('Delhi', 'Delhi'), ('Bangalore', 'Karnataka'),
    ('Hyderabad', 'Telangana'), ('Chennai', 'Tamil Nadu'), ('Kolkata', 'West Bengal'),
    ('Pune', 'Maharashtra'), ('Ahmedabad', 'Gujarat'), ('Jaipur', 'Rajasthan'),
    ('Lucknow', 'Uttar Pradesh'), ('Kochi', 'Kerala'), ('Chandigarh', 'Punjab'),
    ('Indore', 'Madhya Pradesh'), ('Bhopal', 'Madhya Pradesh'),
    ('Coimbatore', 'Tamil Nadu'), ('Nagpur', 'Maharashtra'),
    ('Visakhapatnam', 'Andhra Pradesh'), ('Thiruvananthapuram', 'Kerala')
]

EMPLOYERS = [
    'Tata Consultancy Services', 'Infosys', 'Wipro', 'HCL Technologies',
    'Tech Mahindra', 'Reliance Industries', 'HDFC Bank', 'ICICI Bank',
    'State Bank of India', 'Bajaj Finance', 'Larsen & Toubro',
    'Hindustan Unilever', 'ITC Limited', 'Bharti Airtel', 'Accenture India',
    'Cognizant', 'Capgemini', 'Deloitte India', 'Amazon India',
    'Flipkart', 'Google India', 'Microsoft India', 'IBM India',
    'Oracle India', 'SAP India'
]

EMPLOYMENT_TYPES = ['Salaried', 'Self-Employed', 'Business', 'Freelancer']
EMPLOYMENT_TYPE_WEIGHTS = [0.55, 0.20, 0.15, 0.10]

LOAN_PURPOSES = [
    'Home Purchase', 'Home Renovation', 'Vehicle Loan', 'Education',
    'Business Expansion', 'Personal', 'Medical Emergency', 'Debt Consolidation',
    'Wedding', 'Travel'
]

DESIGNATIONS = [
    'Software Engineer', 'Senior Developer', 'Manager', 'Analyst',
    'Consultant', 'Team Lead', 'Director', 'Associate', 'Executive',
    'Vice President', 'Architect', 'Data Scientist', 'Product Manager'
]

PAYMENT_MODES = ['NEFT', 'RTGS', 'IMPS', 'Cheque', 'Direct']

COLLATERAL_TYPES = [
    'Residential Property', 'Commercial Property', 'Vehicle', 'Fixed Deposit',
    'Gold', 'Mutual Fund Units', 'Insurance Policy'
]

RELATIONSHIPS = [
    'Spouse', 'Parent', 'Sibling', 'Friend', 'Colleague', 'Business Partner'
]


def get_connection():
    """Create PostgreSQL database connection."""
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )


def generate_pan():
    """Generate a realistic PAN number (XXXXX1234X format)."""
    letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))
    digits = ''.join(random.choices('0123456789', k=4))
    last = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    return f"{letters}{digits}{last}"


def generate_aadhar():
    """Generate a realistic Aadhar number (12-digit)."""
    return ''.join(random.choices('0123456789', k=12))


def generate_phone():
    """Generate an Indian phone number."""
    prefixes = ['9876', '9845', '9823', '9801', '9765', '9734', '9654', '9612', '9543', '9432']
    return f"+91-{random.choice(prefixes)}{random.randint(100000, 999999)}"


def calculate_emi(principal, annual_rate, tenure_months):
    """Calculate EMI using the compound interest formula."""
    if annual_rate == 0:
        return principal / tenure_months
    monthly_rate = annual_rate / (12 * 100)
    emi = principal * monthly_rate * (1 + monthly_rate) ** tenure_months
    emi /= ((1 + monthly_rate) ** tenure_months - 1)
    return round(emi, 2)


def calculate_risk_probability(dti_ratio, lti_ratio, age, experience, income):
    """
    Causal risk probability — higher DTI and LTI directly increase default risk.
    This ensures the ML model learns genuine financial risk patterns.
    """
    # Base risk from DTI (primary factor — should dominate feature importance)
    if dti_ratio > 0.50:
        dti_risk = 0.80 + random.uniform(0, 0.15)
    elif dti_ratio > 0.40:
        dti_risk = 0.55 + random.uniform(0, 0.20)
    elif dti_ratio > 0.30:
        dti_risk = 0.30 + random.uniform(0, 0.15)
    elif dti_ratio > 0.20:
        dti_risk = 0.15 + random.uniform(0, 0.10)
    else:
        dti_risk = 0.05 + random.uniform(0, 0.08)

    # LTI contribution (secondary factor)
    if lti_ratio > 8:
        lti_risk = 0.20
    elif lti_ratio > 5:
        lti_risk = 0.10
    elif lti_ratio > 3:
        lti_risk = 0.05
    else:
        lti_risk = 0.0

    # Experience provides stability (negative risk factor)
    exp_benefit = min(experience * 0.008, 0.10)

    # Income stability factor
    if income > 150000:
        income_benefit = 0.08
    elif income > 80000:
        income_benefit = 0.04
    else:
        income_benefit = 0.0

    # Age factor (middle-aged = lower risk)
    if 30 <= age <= 50:
        age_benefit = 0.03
    else:
        age_benefit = 0.0

    # Final risk (clamped between 0.02 and 0.98)
    risk = dti_risk + lti_risk - exp_benefit - income_benefit - age_benefit
    risk += random.uniform(-0.05, 0.05)  # Small noise
    return max(0.02, min(0.98, risk))


def risk_to_credit_score(risk_probability):
    """Convert risk probability to credit score (300-850 scale)."""
    # Inverse relationship: higher risk = lower score
    score = 850 - (risk_probability * 550)
    return round(max(300, min(850, score + random.uniform(-15, 15))), 2)


def seed_customers(cursor, count=1000):
    """Generate and insert customer records."""
    print(f"\n📋 Generating {count} customers...")
    customers = []
    pans_used = set()
    aadhars_used = set()
    emails_used = set()

    for i in range(count):
        gender = random.choice(['Male', 'Female'])
        if gender == 'Male':
            first_name = random.choice(INDIAN_FIRST_NAMES_MALE)
        else:
            first_name = random.choice(INDIAN_FIRST_NAMES_FEMALE)
        last_name = random.choice(INDIAN_LAST_NAMES)

        # Ensure unique identifiers
        pan = generate_pan()
        while pan in pans_used:
            pan = generate_pan()
        pans_used.add(pan)

        aadhar = generate_aadhar()
        while aadhar in aadhars_used:
            aadhar = generate_aadhar()
        aadhars_used.add(aadhar)

        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@email.com"
        while email in emails_used:
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 9999)}@email.com"
        emails_used.add(email)

        city, state = random.choice(CITIES)
        dob = datetime.now() - timedelta(days=random.randint(22 * 365, 60 * 365))
        pincode = str(random.randint(100000, 999999))

        customers.append((
            first_name, last_name, dob.date(), gender, email,
            generate_phone(), f"{random.randint(1, 500)}, {random.choice(['MG Road', 'Gandhi Nagar', 'Nehru Street', 'Park Avenue', 'Lake View Road', 'Temple Road', 'Station Road', 'Market Street'])}",
            city, state, pincode, pan, aadhar
        ))

    execute_batch(cursor,
        """INSERT INTO customers (first_name, last_name, date_of_birth, gender, email,
           phone, address, city, state, pincode, pan_number, aadhar_number)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        customers
    )
    print(f"   ✓ Created {count} customers")
    return count


def seed_employment(cursor, customer_count=1000):
    """Generate and insert employment details for each customer."""
    print(f"\n💼 Generating employment details...")
    employment = []

    for cid in range(1, customer_count + 1):
        emp_type = random.choices(EMPLOYMENT_TYPES, weights=EMPLOYMENT_TYPE_WEIGHTS, k=1)[0]
        experience = round(random.uniform(0.5, 30), 2)

        # Income correlated with experience and employment type
        base_income = 25000 + experience * 3000
        if emp_type == 'Business':
            base_income *= random.uniform(1.2, 3.0)
        elif emp_type == 'Self-Employed':
            base_income *= random.uniform(0.8, 2.5)
        elif emp_type == 'Freelancer':
            base_income *= random.uniform(0.6, 2.0)
        else:
            base_income *= random.uniform(0.9, 1.8)

        monthly_income = round(base_income + random.uniform(-5000, 15000), 2)
        monthly_income = max(15000, monthly_income)  # Minimum income floor

        employer = random.choice(EMPLOYERS) if emp_type == 'Salaried' else f"Self - {random.choice(['Consulting', 'Trading', 'Manufacturing', 'Services', 'Retail'])}"
        designation = random.choice(DESIGNATIONS)

        employment.append((
            cid, employer, emp_type, designation, monthly_income, experience,
            f"{random.choice(['Sector', 'Block', 'Wing'])} {random.randint(1, 50)}, {random.choice(CITIES)[0]}"
        ))

    execute_batch(cursor,
        """INSERT INTO employment_details (customer_id, employer_name, employment_type,
           designation, monthly_income, years_of_experience, office_address)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        employment
    )
    print(f"   ✓ Created {customer_count} employment records")


def seed_applications_and_loans(cursor, customer_count=1000, app_count=1500):
    """
    Generate loan applications with causal default logic.
    High DTI ratio → High risk probability → More likely to default.
    """
    print(f"\n📝 Generating {app_count} loan applications with causal risk logic...")

    # Fetch customer income data for DTI calculations
    cursor.execute("SELECT customer_id, monthly_income FROM employment_details")
    income_map = {row[0]: float(row[1]) for row in cursor.fetchall()}

    # Fetch customer DOB for age calculation
    cursor.execute("SELECT customer_id, date_of_birth FROM customers")
    dob_map = {row[0]: row[1] for row in cursor.fetchall()}

    # Fetch experience data
    cursor.execute("SELECT customer_id, years_of_experience FROM employment_details")
    exp_map = {row[0]: float(row[1]) for row in cursor.fetchall()}

    applications = []
    approved_apps = []
    rejected_count = 0
    pending_count = 0
    base_date = datetime(2024, 1, 1)

    for i in range(app_count):
        cid = random.randint(1, customer_count)
        monthly_income = income_map.get(cid, 50000)
        annual_income = monthly_income * 12

        # Loan amount varies — some deliberately high to create risky profiles
        if random.random() < 0.3:
            # High-risk applications (30%)
            loan_amount = round(annual_income * random.uniform(5, 12), -3)
        elif random.random() < 0.5:
            # Medium-risk applications (35%)
            loan_amount = round(annual_income * random.uniform(2, 5), -3)
        else:
            # Low-risk applications (35%)
            loan_amount = round(annual_income * random.uniform(0.5, 2), -3)

        loan_amount = max(100000, loan_amount)  # Minimum loan amount
        tenure = random.choice([12, 24, 36, 48, 60, 72, 84, 120, 180, 240])
        interest_rate = round(random.uniform(7.5, 14.5), 2)
        purpose = random.choice(LOAN_PURPOSES)

        # Calculate risk factors
        emi = calculate_emi(loan_amount, interest_rate, tenure)
        dti_ratio = emi / monthly_income if monthly_income > 0 else 1.0
        lti_ratio = loan_amount / annual_income if annual_income > 0 else 10.0

        # Age calculation
        dob = dob_map.get(cid, datetime(1990, 1, 1).date())
        age = (datetime.now().date() - dob).days / 365.25
        experience = exp_map.get(cid, 5)

        # Causal risk probability
        risk_prob = calculate_risk_probability(dti_ratio, lti_ratio, age, experience, monthly_income)
        credit_score = risk_to_credit_score(risk_prob)

        # Decision based on risk
        if risk_prob > 0.60:
            status = 'Rejected'
            recommendation = f"High risk — DTI ratio ({dti_ratio:.1%}) exceeds safe threshold"
            rejected_count += 1
        elif risk_prob > 0.45 and random.random() < 0.4:
            status = 'Pending'
            recommendation = "Moderate risk — requires manual review"
            pending_count += 1
        else:
            status = 'Approved'
            recommendation = "Low risk — strong financial profile"

        app_date = base_date + timedelta(days=random.randint(0, 365))

        applications.append((
            cid, loan_amount, tenure, interest_rate, purpose,
            app_date, status, credit_score, round(risk_prob, 4),
            'High' if risk_prob > 0.5 else 'Low',
            recommendation, 'RF_v1.0', random.randint(50, 300)
        ))

        if status == 'Approved':
            approved_apps.append({
                'index': i,
                'customer_id': cid,
                'loan_amount': loan_amount,
                'tenure': tenure,
                'interest_rate': interest_rate,
                'emi': emi,
                'risk_prob': risk_prob,
                'app_date': app_date
            })

    execute_batch(cursor,
        """INSERT INTO loan_applications (customer_id, loan_amount, loan_tenure_months,
           interest_rate, loan_purpose, application_date, status, credit_score,
           risk_probability, risk_level, recommendation, ml_model_version, processing_time_ms)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        applications
    )

    approved_count = len(approved_apps)
    print(f"   ✓ Created {app_count} applications (Approved: {approved_count}, Rejected: {rejected_count}, Pending: {pending_count})")

    return approved_apps


def seed_loans_and_related(cursor, approved_apps):
    """Create loans, disbursements, repayments, collateral, guarantors, and NPA tracking."""
    print(f"\n💰 Generating {len(approved_apps)} loans and related records...")

    loans = []
    disbursements = []
    repayments = []
    collateral_records = []
    guarantor_records = []
    npa_records = []
    defaulted_count = 0
    total_repayment_records = 0

    for idx, app in enumerate(approved_apps):
        app_id = idx + 1  # application_id is sequential
        # Find the actual application_id for approved ones
        cid = app['customer_id']
        loan_amount = app['loan_amount']
        tenure = app['tenure']
        interest_rate = app['interest_rate']
        emi = app['emi']
        risk_prob = app['risk_prob']
        start_date = app['app_date'] + timedelta(days=random.randint(3, 15))

        # Determine if loan defaults (causal: high risk → more defaults)
        will_default = random.random() < risk_prob * 0.25  # ~25% of high-risk approved loans default
        if will_default:
            defaulted_count += 1
            loan_status = 'Defaulted'
            months_paid = random.randint(3, min(tenure - 1, 18))
        else:
            if random.random() < 0.15:
                loan_status = 'Closed'
                months_paid = tenure
            else:
                loan_status = 'Active'
                months_active = (datetime.now().date() - start_date.date()).days // 30
                months_paid = min(months_active, tenure)

        disbursed_amount = loan_amount
        total_paid = round(emi * months_paid, 2)
        outstanding = round(max(0, loan_amount - total_paid * 0.6), 2)  # Simplified outstanding

        end_date = start_date + timedelta(days=tenure * 30)

        loans.append((
            cid, loan_amount, disbursed_amount, interest_rate, tenure,
            round(emi, 2), start_date.date(), end_date.date(),
            loan_status, outstanding, total_paid
        ))

        # Disbursement record
        disbursements.append((
            start_date.date(), disbursed_amount,
            random.choice(PAYMENT_MODES),
            f"TXN{random.randint(100000000, 999999999)}"
        ))

        # Generate repayment records
        for month in range(1, months_paid + 1):
            due_date = start_date + timedelta(days=30 * month)
            principal_part = round(emi * 0.6, 2)
            interest_part = round(emi * 0.4, 2)

            if will_default and month > months_paid - 3:
                # Last few months before default — overdue
                days_over = random.randint(30, 180)
                pay_status = 'Overdue'
                amount_paid = round(emi * random.uniform(0, 0.5), 2)
            elif random.random() < 0.05:
                # Occasional late payment
                days_over = random.randint(1, 29)
                pay_status = 'Partial'
                amount_paid = round(emi * random.uniform(0.5, 0.9), 2)
            else:
                days_over = 0
                pay_status = 'Paid'
                amount_paid = round(emi, 2)

            payment_date = due_date + timedelta(days=days_over) if pay_status != 'Pending' else None

            repayments.append((
                due_date.date(),
                payment_date.date() if payment_date else None,
                round(emi, 2), principal_part, interest_part,
                amount_paid, pay_status, days_over,
                round(days_over * emi * 0.001, 2)  # Penalty
            ))
            total_repayment_records += 1

        # Collateral (60% of loans have collateral)
        if random.random() < 0.60:
            coll_type = random.choice(COLLATERAL_TYPES)
            coll_value = round(loan_amount * random.uniform(1.1, 2.0), 2)
            collateral_records.append((
                coll_type, f"{coll_type} provided as security",
                coll_value, start_date.date()
            ))

        # Guarantor (30% of loans have guarantor)
        if random.random() < 0.30:
            g_gender = random.choice(['Male', 'Female'])
            if g_gender == 'Male':
                g_name = f"{random.choice(INDIAN_FIRST_NAMES_MALE)} {random.choice(INDIAN_LAST_NAMES)}"
            else:
                g_name = f"{random.choice(INDIAN_FIRST_NAMES_FEMALE)} {random.choice(INDIAN_LAST_NAMES)}"
            guarantor_records.append((
                g_name, random.choice(RELATIONSHIPS),
                generate_phone(),
                f"{g_name.split()[0].lower()}.guarantor@email.com",
                round(random.uniform(30000, 200000), 2),
                f"{random.choice(CITIES)[0]}, India"
            ))

        # NPA tracking for defaulted loans
        if will_default:
            days_over = random.randint(90, 365)
            if days_over <= 180:
                npa_cat = 'Sub-Standard'
                provision = round(outstanding * 0.15, 2)
            elif days_over <= 365:
                npa_cat = 'Doubtful'
                provision = round(outstanding * 0.40, 2)
            else:
                npa_cat = 'Loss'
                provision = round(outstanding * 1.0, 2)

            npa_records.append((
                (start_date + timedelta(days=months_paid * 30 + 90)).date(),
                days_over, outstanding, npa_cat, provision,
                random.choice(['Open', 'Resolved']),
                f"Loan defaulted after {months_paid} EMI payments"
            ))

    # Insert loans (we need loan_ids for related tables)
    cursor.execute("SELECT COALESCE(MAX(application_id), 0) FROM loan_applications WHERE status = 'Approved'")

    # Insert loans first
    loan_insert = """INSERT INTO loans (customer_id, loan_amount, disbursed_amount,
        interest_rate, tenure_months, emi_amount, loan_start_date, loan_end_date,
        loan_status, outstanding_amount, total_paid)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING loan_id"""

    loan_ids = []
    for loan_data in loans:
        cursor.execute(loan_insert, loan_data)
        lid = cursor.fetchone()[0]
        loan_ids.append(lid)

    # Also link loans to applications
    cursor.execute("""SELECT application_id FROM loan_applications WHERE status = 'Approved' ORDER BY application_id""")
    approved_app_ids = [row[0] for row in cursor.fetchall()]

    for i, lid in enumerate(loan_ids):
        if i < len(approved_app_ids):
            cursor.execute("UPDATE loans SET application_id = %s WHERE loan_id = %s",
                         (approved_app_ids[i], lid))

    # Insert disbursements
    for i, disb in enumerate(disbursements):
        if i < len(loan_ids):
            cursor.execute(
                """INSERT INTO disbursements (loan_id, disbursement_date, amount, payment_mode, reference_number)
                   VALUES (%s, %s, %s, %s, %s)""",
                (loan_ids[i], *disb)
            )

    # Insert repayments — map them to loan_ids
    rep_idx = 0
    for i, app in enumerate(approved_apps):
        if i >= len(loan_ids):
            break
        lid = loan_ids[i]
        risk_prob = app['risk_prob']
        will_default = random.Random(42 + i).random() < risk_prob * 0.25
        tenure = app['tenure']

        if will_default:
            months_paid = random.Random(42 + i).randint(3, min(tenure - 1, 18))
        elif random.Random(42 + i).random() < 0.15:
            months_paid = tenure
        else:
            start_date = app['app_date'] + timedelta(days=random.Random(42 + i).randint(3, 15))
            months_active = (datetime.now().date() - start_date.date()).days // 30
            months_paid = min(months_active, tenure)

        for _ in range(months_paid):
            if rep_idx < len(repayments):
                rep = repayments[rep_idx]
                cursor.execute(
                    """INSERT INTO repayments (loan_id, due_date, payment_date, emi_amount,
                       principal_component, interest_component, amount_paid, payment_status,
                       days_overdue, penalty_amount)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (lid, *rep)
                )
                rep_idx += 1

    # Insert collateral
    coll_idx = 0
    for i, lid in enumerate(loan_ids):
        if coll_idx < len(collateral_records):
            if random.Random(42 + i).random() < 0.60:
                cursor.execute(
                    """INSERT INTO collateral (loan_id, collateral_type, description, estimated_value, valuation_date)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (lid, *collateral_records[coll_idx])
                )
                coll_idx += 1

    # Insert guarantors
    guar_idx = 0
    for i, lid in enumerate(loan_ids):
        if guar_idx < len(guarantor_records):
            if random.Random(42 + i).random() < 0.30:
                cursor.execute(
                    """INSERT INTO guarantors (loan_id, full_name, relationship, phone, email, monthly_income, address)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (lid, *guarantor_records[guar_idx])
                )
                guar_idx += 1

    # Insert NPA records
    npa_loan_ids = [loan_ids[i] for i in range(len(loan_ids))
                    if i < len(loans) and loans[i][8] == 'Defaulted']
    for i, npa in enumerate(npa_records):
        if i < len(npa_loan_ids):
            cursor.execute(
                """INSERT INTO npa_tracking (loan_id, npa_date, days_overdue, outstanding_amount,
                   npa_category, provision_amount, resolution_status, notes)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (npa_loan_ids[i], *npa)
            )

    print(f"   ✓ Created {len(loans)} loans ({defaulted_count} defaulted based on risk probability)")
    print(f"   ✓ Created {len(disbursements)} disbursement records")
    print(f"   ✓ Created {total_repayment_records} repayment records")
    print(f"   ✓ Created {len(collateral_records)} collateral records")
    print(f"   ✓ Created {len(guarantor_records)} guarantor records")
    print(f"   ✓ Created {len(npa_records)} NPA tracking records")


def main():
    """Main entry point for database seeding."""
    print("=" * 60)
    print("🏦 CREDIT RISK SYSTEM — DATABASE SEEDER")
    print("=" * 60)
    print(f"\nDatabase: {config.DB_NAME}")
    print(f"Host: {config.DB_HOST}:{config.DB_PORT}")
    print("\n⚠️  This will populate the database with synthetic data.")

    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Seeding cancelled.")
        return

    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        # Phase 1: Customers
        customer_count = seed_customers(cursor, count=1000)

        # Phase 2: Employment details
        seed_employment(cursor, customer_count)

        # Phase 3: Loan applications (with causal risk logic)
        approved_apps = seed_applications_and_loans(cursor, customer_count, app_count=1500)

        # Phase 4: Loans, disbursements, repayments, collateral, guarantors, NPA
        seed_loans_and_related(cursor, approved_apps)

        conn.commit()
        print("\n" + "=" * 60)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    main()
