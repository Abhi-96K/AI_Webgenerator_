#!/usr/bin/env python3
"""
Database initialization script
Run this to set up your database with sample data
"""

from app import app, db
from models import User, *
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the database with sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            print("✅ Admin user created (admin/admin123)")
        
        # Create sample user
        user = User.query.filter_by(username='demo').first()
        if not user:
            user = User(
                username='demo',
                email='demo@example.com',
                password_hash=generate_password_hash('demo123')
            )
            db.session.add(user)
            print("✅ Demo user created (demo/demo123)")
        
        db.session.commit()
        
        # Add sample data based on app type
        add_sample_data(admin, user)
        
        print("🎉 Database initialization complete!")
        print("\n📝 Login credentials:")
        print("   Admin: admin / admin123")
        print("   Demo:  demo / demo123")

def add_sample_data(admin_user, demo_user):
    """Add sample data specific to the application"""
    # This will be customized based on the app type during generation
    pass

if __name__ == '__main__':
    init_database()
