"""
Portfolio API Routes — Portfolio analytics, NPA analysis, and repayment statistics.
"""

from flask import Blueprint, jsonify
from sqlalchemy import func, case
from backend.database import get_db_session
from backend.models import (
    Loan, LoanApplication, Repayment, NPATracking, Disbursement
)

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')


@portfolio_bp.route('/summary', methods=['GET'])
def get_portfolio_summary():
    """
    Get comprehensive portfolio health metrics.
    Includes loan statistics, financial metrics, and risk indicators.
    """
    session = get_db_session()
    try:
        # ─── Loan statistics ────────────────────────────────────
        total_applications = session.query(func.count(LoanApplication.application_id)).scalar() or 0
        total_loans = session.query(func.count(Loan.loan_id)).scalar() or 0

        active_loans = session.query(func.count(Loan.loan_id))\
            .filter(Loan.loan_status == 'Active').scalar() or 0
        closed_loans = session.query(func.count(Loan.loan_id))\
            .filter(Loan.loan_status == 'Closed').scalar() or 0
        defaulted_loans = session.query(func.count(Loan.loan_id))\
            .filter(Loan.loan_status == 'Defaulted').scalar() or 0

        approved_apps = session.query(func.count(LoanApplication.application_id))\
            .filter(LoanApplication.status == 'Approved').scalar() or 0
        approval_rate = round((approved_apps / total_applications * 100), 2) \
            if total_applications > 0 else 0

        # ─── Financial metrics ──────────────────────────────────
        total_disbursed = session.query(func.sum(Loan.disbursed_amount)).scalar() or 0
        total_outstanding = session.query(func.sum(Loan.outstanding_amount))\
            .filter(Loan.loan_status.in_(['Active', 'Defaulted'])).scalar() or 0
        total_repaid = session.query(func.sum(Loan.total_paid)).scalar() or 0

        # NPA amount (outstanding on defaulted loans)
        total_npa_amount = session.query(func.sum(Loan.outstanding_amount))\
            .filter(Loan.loan_status == 'Defaulted').scalar() or 0

        # ─── Risk metrics ───────────────────────────────────────
        npa_ratio = round((float(total_npa_amount) / float(total_outstanding) * 100), 2) \
            if total_outstanding > 0 else 0
        default_rate = round((defaulted_loans / total_loans * 100), 2) \
            if total_loans > 0 else 0

        # Average EMI payment rate
        total_due = session.query(func.count(Repayment.repayment_id)).scalar() or 0
        paid_on_time = session.query(func.count(Repayment.repayment_id))\
            .filter(Repayment.payment_status == 'Paid').scalar() or 0
        avg_payment_rate = round((paid_on_time / total_due * 100), 2) if total_due > 0 else 0

        return jsonify({
            'loan_statistics': {
                'total_applications': total_applications,
                'total_loans': total_loans,
                'active_loans': active_loans,
                'closed_loans': closed_loans,
                'defaulted_loans': defaulted_loans,
                'approval_rate': approval_rate
            },
            'financial_metrics': {
                'total_disbursed': float(total_disbursed),
                'total_outstanding': float(total_outstanding),
                'total_repaid': float(total_repaid),
                'total_npa_amount': float(total_npa_amount)
            },
            'risk_metrics': {
                'npa_ratio': npa_ratio,
                'default_rate': default_rate,
                'average_emi_payment_rate': avg_payment_rate
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@portfolio_bp.route('/npa-analysis', methods=['GET'])
def get_npa_analysis():
    """
    Get detailed NPA classification breakdown.
    Categories: Standard, Sub-Standard, Doubtful, Loss
    """
    session = get_db_session()
    try:
        total_loans = session.query(func.count(Loan.loan_id)).scalar() or 1

        # Count loans by NPA category
        npa_counts = session.query(
            NPATracking.npa_category,
            func.count(NPATracking.npa_id)
        ).group_by(NPATracking.npa_category).all()

        npa_dict = {cat: count for cat, count in npa_counts}

        # Standard = total loans - all NPA loans
        total_npa = sum(npa_dict.values())
        standard_count = total_loans - total_npa

        classification = {
            'Standard': {
                'count': standard_count,
                'percentage': round(standard_count / total_loans * 100, 2)
            }
        }

        for category in ['Sub-Standard', 'Doubtful', 'Loss']:
            count = npa_dict.get(category, 0)
            classification[category] = {
                'count': count,
                'percentage': round(count / total_loans * 100, 2)
            }

        # Total NPA amount by category
        npa_amounts = session.query(
            NPATracking.npa_category,
            func.sum(NPATracking.outstanding_amount),
            func.sum(NPATracking.provision_amount)
        ).group_by(NPATracking.npa_category).all()

        amount_breakdown = {}
        for cat, outstanding, provision in npa_amounts:
            amount_breakdown[cat] = {
                'outstanding_amount': float(outstanding) if outstanding else 0,
                'provision_amount': float(provision) if provision else 0
            }

        return jsonify({
            'npa_classification': classification,
            'amount_breakdown': amount_breakdown,
            'total_npa_loans': total_npa,
            'total_loans': total_loans
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@portfolio_bp.route('/repayment-stats', methods=['GET'])
def get_repayment_stats():
    """Get repayment performance metrics."""
    session = get_db_session()
    try:
        # Payment status distribution
        status_counts = session.query(
            Repayment.payment_status,
            func.count(Repayment.repayment_id)
        ).group_by(Repayment.payment_status).all()

        status_distribution = {status: count for status, count in status_counts}
        total_payments = sum(status_distribution.values())

        # Total amounts
        total_emi_due = session.query(func.sum(Repayment.emi_amount)).scalar() or 0
        total_collected = session.query(func.sum(Repayment.amount_paid))\
            .filter(Repayment.payment_status.in_(['Paid', 'Partial'])).scalar() or 0
        total_penalties = session.query(func.sum(Repayment.penalty_amount)).scalar() or 0

        # Average days overdue for overdue payments
        avg_days_overdue = session.query(func.avg(Repayment.days_overdue))\
            .filter(Repayment.days_overdue > 0).scalar() or 0

        # On-time payment percentage
        on_time = status_distribution.get('Paid', 0)
        on_time_pct = round(on_time / total_payments * 100, 2) if total_payments > 0 else 0

        return jsonify({
            'repayment_summary': {
                'total_payments': total_payments,
                'on_time_payments': status_distribution.get('Paid', 0),
                'overdue_payments': status_distribution.get('Overdue', 0),
                'partial_payments': status_distribution.get('Partial', 0),
                'pending_payments': status_distribution.get('Pending', 0),
                'on_time_percentage': on_time_pct
            },
            'financial_summary': {
                'total_emi_due': float(total_emi_due),
                'total_collected': float(total_collected),
                'collection_efficiency': round(float(total_collected) / float(total_emi_due) * 100, 2) if float(total_emi_due) > 0 else 0,
                'total_penalties': float(total_penalties)
            },
            'risk_indicators': {
                'average_days_overdue': round(float(avg_days_overdue), 1),
                'payment_status_distribution': status_distribution
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
