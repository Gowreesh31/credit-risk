"""
Credit Risk Assessment API — Flask Application Entry Point.

Registers all route blueprints and starts the development server.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, jsonify
from flask_cors import CORS
import config
from backend.database import engine


def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)
    CORS(app)  # Enable Cross-Origin Resource Sharing

    # ─── Register Blueprints ────────────────────────────────────
    from backend.routes.customer_routes import customer_bp
    from backend.routes.loan_routes import loan_bp
    from backend.routes.portfolio_routes import portfolio_bp

    app.register_blueprint(customer_bp)
    app.register_blueprint(loan_bp)
    app.register_blueprint(portfolio_bp)

    # ─── Health Check Endpoint ──────────────────────────────────
    @app.route('/health', methods=['GET'])
    def health_check():
        """System health status with database connectivity check."""
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_status = 'connected'
        except Exception:
            db_status = 'disconnected'

        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'version': '1.0.0'
        }), 200

    # ─── Root Endpoint ──────────────────────────────────────────
    @app.route('/', methods=['GET'])
    def root():
        """API welcome page with available endpoints."""
        return jsonify({
            'name': 'Credit Risk Assessment API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'customers': '/api/customers/',
                'customer_detail': '/api/customers/<id>',
                'loan_apply': '/api/loans/apply',
                'loan_applications': '/api/loans/applications',
                'loans': '/api/loans/loans',
                'portfolio_summary': '/api/portfolio/summary',
                'npa_analysis': '/api/portfolio/npa-analysis',
                'repayment_stats': '/api/portfolio/repayment-stats'
            }
        }), 200

    # ─── Error Handlers ─────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("🚀 CREDIT RISK ASSESSMENT API STARTING")
    print("=" * 60)
    print(f"📍 API running at: http://127.0.0.1:{config.API_PORT}")
    print(f"📊 Database: {config.DB_NAME}")
    print(f"🔍 Debug mode: {config.DEBUG}")
    print("=" * 60)
    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.DEBUG
    )
