#!/usr/bin/env python3
"""
Development server runner
Usage: python run.py
"""

from app import app
from models import db

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    
    # Run the development server
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
