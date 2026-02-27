"""
VALLY'S DIVINE HAIR
COMPLETE DATABASE RESET + ADMIN FIX

- Deletes ALL tables
- Recreates tables with is_admin column
- Creates ONE admin account
- Fixes ADMIN badge showing for all users
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Minimal Flask app for DB operations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/hair_salon_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =========================
# MODELS (MUST MATCH app.py)
# =========================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)   # ✅ FIX
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    service_type = db.Column(db.String(200), nullable=False)
    braid_size = db.Column(db.String(50))
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(50), nullable=False)
    special_requests = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CompletedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    service_type = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500))
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# =========================
# RESET FUNCTION
# =========================

def reset_database():
    print("=" * 70)
    print("VALLY'S DIVINE HAIR - COMPLETE DATABASE RESET")
    print("=" * 70)

    print("\n⚠️ WARNING:")
    print("• ALL users will be deleted")
    print("• ALL appointments will be deleted")
    print("• ALL messages will be deleted")
    print("• ALL portfolio items will be deleted")

    confirm = input("\nType 'YES' to continue: ")
    if confirm != "YES":
        print("\n❌ Cancelled.")
        return

    with app.app_context():
        try:
            print("\nSTEP 1: Dropping all tables...")
            db.drop_all()
            print("✅ Tables dropped")

            print("\nSTEP 2: Creating fresh tables...")
            db.create_all()
            print("✅ Tables created")

            print("\nSTEP 3: Creating ADMIN account...")
            admin = User(
                username="admin",
                email="admin@vallys.com",
                is_admin=True
            )
            # FIXED: Password is Admin123 (capital A) to match app.py
            admin.set_password("Admin123")
            db.session.add(admin)
            db.session.commit()

            print("✅ Admin account created")

            print("\n" + "=" * 70)
            print("🎉 DATABASE RESET SUCCESSFUL!")
            print("=" * 70)

            print("\n🔐 ADMIN LOGIN DETAILS")
            print("Email: admin@vallys.com")
            print("Password: Admin123")
            print("          ^^^^^^^^^ (Capital A)")

            print("\n👤 USER LOGIC FIXED:")
            print("• is_admin = TRUE → ADMIN badge visible")
            print("• is_admin = FALSE → Regular customer")
            print("• New registrations are NOT admins")

            print("\n📌 NEXT STEPS:")
            print("1. Stop Flask if running (Ctrl + C)")
            print("2. Run: python app.py")
            print("3. Login as admin@vallys.com with password Admin123")
            print("4. Register customers normally")

            print("=" * 70)

        except Exception as e:
            print("\n❌ ERROR:", e)
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    reset_database()