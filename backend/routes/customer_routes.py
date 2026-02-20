"""
Customer API Routes — CRUD operations for customer management.
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from backend.database import get_db_session
from backend.models import Customer, EmploymentDetail

customer_bp = Blueprint('customers', __name__, url_prefix='/api/customers')


@customer_bp.route('/', methods=['GET'])
def get_all_customers():
    """Retrieve all customers with pagination."""
    session = get_db_session()
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Clamp values
        limit = min(limit, 500)
        offset = max(offset, 0)

        customers = session.query(Customer)\
            .order_by(Customer.customer_id)\
            .offset(offset)\
            .limit(limit)\
            .all()

        total = session.query(func.count(Customer.customer_id)).scalar()

        return jsonify({
            'customers': [c.to_dict() for c in customers],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@customer_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get detailed customer information including employment data."""
    session = get_db_session()
    try:
        customer = session.query(Customer).filter_by(customer_id=customer_id).first()
        if not customer:
            return jsonify({'error': f'Customer {customer_id} not found'}), 404

        result = customer.to_dict()

        # Include employment details
        employment = session.query(EmploymentDetail)\
            .filter_by(customer_id=customer_id).first()
        if employment:
            result['employment'] = employment.to_dict()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@customer_bp.route('/', methods=['POST'])
def register_customer():
    """Register a new customer with KYC data."""
    session = get_db_session()
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        # Validate required fields
        required = ['first_name', 'last_name', 'date_of_birth', 'email', 'phone']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        # Check for duplicate email
        existing = session.query(Customer).filter_by(email=data['email']).first()
        if existing:
            return jsonify({'error': f'Email {data["email"]} already registered'}), 409

        # Create customer
        customer = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=data['date_of_birth'],
            gender=data.get('gender'),
            email=data['email'],
            phone=data['phone'],
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            pincode=data.get('pincode'),
            pan_number=data.get('pan_number'),
            aadhar_number=data.get('aadhar_number')
        )
        session.add(customer)
        session.flush()  # Get the generated customer_id

        # Create employment details if provided
        if 'employment' in data:
            emp_data = data['employment']
            employment = EmploymentDetail(
                customer_id=customer.customer_id,
                employer_name=emp_data.get('employer_name'),
                employment_type=emp_data.get('employment_type'),
                designation=emp_data.get('designation'),
                monthly_income=emp_data.get('monthly_income', 0),
                years_of_experience=emp_data.get('years_of_experience', 0),
                office_address=emp_data.get('office_address')
            )
            session.add(employment)

        session.commit()

        return jsonify({
            'message': 'Customer registered successfully',
            'customer_id': customer.customer_id,
            'customer': customer.to_dict()
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
