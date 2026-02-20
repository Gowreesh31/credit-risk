"""
SQLAlchemy ORM models for all 9 database tables.
"""

from sqlalchemy import (
    Column, Integer, String, Numeric, Date, DateTime, Text,
    ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Customer(Base):
    __tablename__ = 'customers'

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10))
    email = Column(String(200), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    pan_number = Column(String(10), unique=True)
    aadhar_number = Column(String(12), unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    # Relationships
    employment = relationship('EmploymentDetail', back_populates='customer', uselist=False)
    applications = relationship('LoanApplication', back_populates='customer')
    loans = relationship('Loan', back_populates='customer')

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'full_name': f"{self.first_name} {self.last_name}",
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': str(self.date_of_birth),
            'gender': self.gender,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'created_at': str(self.created_at)
        }


class EmploymentDetail(Base):
    __tablename__ = 'employment_details'

    employment_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)
    employer_name = Column(String(200))
    employment_type = Column(String(50))
    designation = Column(String(100))
    monthly_income = Column(Numeric(15, 2), nullable=False)
    years_of_experience = Column(Numeric(5, 2), default=0)
    office_address = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    customer = relationship('Customer', back_populates='employment')

    def to_dict(self):
        return {
            'employment_id': self.employment_id,
            'employer_name': self.employer_name,
            'employment_type': self.employment_type,
            'designation': self.designation,
            'monthly_income': float(self.monthly_income),
            'years_of_experience': float(self.years_of_experience) if self.years_of_experience else 0,
            'office_address': self.office_address
        }


class LoanApplication(Base):
    __tablename__ = 'loan_applications'

    application_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)
    loan_amount = Column(Numeric(15, 2), nullable=False)
    loan_tenure_months = Column(Integer, nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    loan_purpose = Column(String(100))
    application_date = Column(DateTime, default=func.now())
    status = Column(String(20), default='Pending')
    credit_score = Column(Numeric(6, 2))
    risk_probability = Column(Numeric(6, 4))
    risk_level = Column(String(20))
    recommendation = Column(Text)
    ml_model_version = Column(String(50))
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    # Relationships
    customer = relationship('Customer', back_populates='applications')
    loan = relationship('Loan', back_populates='application', uselist=False)

    def to_dict(self):
        return {
            'application_id': self.application_id,
            'customer_id': self.customer_id,
            'loan_amount': float(self.loan_amount),
            'loan_tenure_months': self.loan_tenure_months,
            'interest_rate': float(self.interest_rate),
            'loan_purpose': self.loan_purpose,
            'application_date': str(self.application_date),
            'status': self.status,
            'credit_score': float(self.credit_score) if self.credit_score else None,
            'risk_probability': float(self.risk_probability) if self.risk_probability else None,
            'risk_level': self.risk_level,
            'recommendation': self.recommendation
        }


class Loan(Base):
    __tablename__ = 'loans'

    loan_id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey('loan_applications.application_id', ondelete='CASCADE'), nullable=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)
    loan_amount = Column(Numeric(15, 2), nullable=False)
    disbursed_amount = Column(Numeric(15, 2))
    interest_rate = Column(Numeric(5, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    emi_amount = Column(Numeric(15, 2))
    loan_start_date = Column(Date)
    loan_end_date = Column(Date)
    loan_status = Column(String(20), default='Active')
    outstanding_amount = Column(Numeric(15, 2))
    total_paid = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    # Relationships
    application = relationship('LoanApplication', back_populates='loan')
    customer = relationship('Customer', back_populates='loans')
    disbursements = relationship('Disbursement', back_populates='loan')
    repayments = relationship('Repayment', back_populates='loan')
    collateral_items = relationship('Collateral', back_populates='loan')
    guarantors = relationship('Guarantor', back_populates='loan')
    npa_records = relationship('NPATracking', back_populates='loan')

    def to_dict(self):
        return {
            'loan_id': self.loan_id,
            'application_id': self.application_id,
            'customer_id': self.customer_id,
            'loan_amount': float(self.loan_amount),
            'disbursed_amount': float(self.disbursed_amount) if self.disbursed_amount else None,
            'interest_rate': float(self.interest_rate),
            'tenure_months': self.tenure_months,
            'emi_amount': float(self.emi_amount) if self.emi_amount else None,
            'loan_start_date': str(self.loan_start_date) if self.loan_start_date else None,
            'loan_end_date': str(self.loan_end_date) if self.loan_end_date else None,
            'loan_status': self.loan_status,
            'outstanding_amount': float(self.outstanding_amount) if self.outstanding_amount else None,
            'total_paid': float(self.total_paid) if self.total_paid else 0
        }


class Disbursement(Base):
    __tablename__ = 'disbursements'

    disbursement_id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey('loans.loan_id', ondelete='CASCADE'), nullable=False)
    disbursement_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_mode = Column(String(50))
    reference_number = Column(String(100))
    created_at = Column(DateTime, default=func.now())

    loan = relationship('Loan', back_populates='disbursements')

    def to_dict(self):
        return {
            'disbursement_id': self.disbursement_id,
            'loan_id': self.loan_id,
            'disbursement_date': str(self.disbursement_date),
            'amount': float(self.amount),
            'payment_mode': self.payment_mode,
            'reference_number': self.reference_number
        }


class Repayment(Base):
    __tablename__ = 'repayments'

    repayment_id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey('loans.loan_id', ondelete='CASCADE'), nullable=False)
    due_date = Column(Date, nullable=False)
    payment_date = Column(Date)
    emi_amount = Column(Numeric(15, 2), nullable=False)
    principal_component = Column(Numeric(15, 2))
    interest_component = Column(Numeric(15, 2))
    amount_paid = Column(Numeric(15, 2), default=0)
    payment_status = Column(String(20), default='Pending')
    days_overdue = Column(Integer, default=0)
    penalty_amount = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime, default=func.now())

    loan = relationship('Loan', back_populates='repayments')

    def to_dict(self):
        return {
            'repayment_id': self.repayment_id,
            'loan_id': self.loan_id,
            'due_date': str(self.due_date),
            'payment_date': str(self.payment_date) if self.payment_date else None,
            'emi_amount': float(self.emi_amount),
            'amount_paid': float(self.amount_paid) if self.amount_paid else 0,
            'payment_status': self.payment_status,
            'days_overdue': self.days_overdue
        }


class Collateral(Base):
    __tablename__ = 'collateral'

    collateral_id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey('loans.loan_id', ondelete='CASCADE'), nullable=False)
    collateral_type = Column(String(100))
    description = Column(Text)
    estimated_value = Column(Numeric(15, 2))
    valuation_date = Column(Date)
    created_at = Column(DateTime, default=func.now())

    loan = relationship('Loan', back_populates='collateral_items')

    def to_dict(self):
        return {
            'collateral_id': self.collateral_id,
            'loan_id': self.loan_id,
            'collateral_type': self.collateral_type,
            'description': self.description,
            'estimated_value': float(self.estimated_value) if self.estimated_value else None,
            'valuation_date': str(self.valuation_date) if self.valuation_date else None
        }


class Guarantor(Base):
    __tablename__ = 'guarantors'

    guarantor_id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey('loans.loan_id', ondelete='CASCADE'), nullable=False)
    full_name = Column(String(200), nullable=False)
    relationship = Column(String(100))
    phone = Column(String(20))
    email = Column(String(200))
    monthly_income = Column(Numeric(15, 2))
    address = Column(Text)
    created_at = Column(DateTime, default=func.now())

    loan = relationship('Loan', back_populates='guarantors')

    def to_dict(self):
        return {
            'guarantor_id': self.guarantor_id,
            'loan_id': self.loan_id,
            'full_name': self.full_name,
            'relationship': self.relationship,
            'phone': self.phone,
            'email': self.email,
            'monthly_income': float(self.monthly_income) if self.monthly_income else None
        }


class NPATracking(Base):
    __tablename__ = 'npa_tracking'

    npa_id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey('loans.loan_id', ondelete='CASCADE'), nullable=False)
    npa_date = Column(Date, nullable=False)
    days_overdue = Column(Integer, nullable=False)
    outstanding_amount = Column(Numeric(15, 2))
    npa_category = Column(String(20))
    provision_amount = Column(Numeric(15, 2))
    resolution_status = Column(String(50), default='Open')
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    loan = relationship('Loan', back_populates='npa_records')

    def to_dict(self):
        return {
            'npa_id': self.npa_id,
            'loan_id': self.loan_id,
            'npa_date': str(self.npa_date),
            'days_overdue': self.days_overdue,
            'outstanding_amount': float(self.outstanding_amount) if self.outstanding_amount else None,
            'npa_category': self.npa_category,
            'provision_amount': float(self.provision_amount) if self.provision_amount else None,
            'resolution_status': self.resolution_status,
            'notes': self.notes
        }
