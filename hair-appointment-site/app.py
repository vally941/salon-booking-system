from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import inspect
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/hair_salon_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '🔐 Please login first to continue.'
login_manager.login_message_category = 'info'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Database Models - UPDATED WITH is_admin FIELD
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
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

# NEW MODEL: CompletedJob (Portfolio)
class CompletedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    service_type = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500))
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database check function - UPDATED TO CHECK is_admin COLUMN
def check_and_fix_database():
    """Check if all required columns exist and fix if needed"""
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            
            # Get existing columns for each table
            tables = {}
            for table_name in ['user', 'appointment', 'contact_message', 'completed_job']:
                if inspector.has_table(table_name):
                    columns = inspector.get_columns(table_name)
                    tables[table_name] = [col['name'] for col in columns]
                else:
                    tables[table_name] = []
            
            # Check for missing tables
            missing_tables = []
            for table in ['user', 'appointment', 'contact_message', 'completed_job']:
                if not inspector.has_table(table):
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"⚠️ Missing tables: {', '.join(missing_tables)}")
                print("Creating missing tables...")
                db.create_all()
                return True
            
            # Check for critical columns - INCLUDING is_admin
            critical_columns = {
                'user': ['username', 'email', 'password_hash', 'is_admin', 'created_at'],
                'appointment': ['customer_name', 'customer_email', 'customer_phone', 
                               'service_type', 'braid_size', 'user_id', 'status'],
                'contact_message': ['name', 'email', 'message', 'read', 'user_id'],
                'completed_job': ['title', 'description', 'service_type', 'image_url', 'featured']
            }
            
            all_good = True
            for table, required_cols in critical_columns.items():
                existing_cols = tables.get(table, [])
                for col in required_cols:
                    if col not in existing_cols:
                        print(f"⚠️ Missing column: {table}.{col}")
                        all_good = False
            
            if not all_good:
                print("Some columns are missing. Dropping and recreating tables...")
                db.drop_all()
                db.create_all()
                
                # Create admin user with is_admin=True and strong password
                admin = User(username='admin', email='admin@vallys.com', is_admin=True)
                admin.set_password('Admin123')
                db.session.add(admin)
                db.session.commit()
                print("✅ Database recreated with all columns")
                print("✅ Admin user created: admin@vallys.com / Admin123")
            else:
                # Check if admin user exists
                admin = User.query.filter_by(email='admin@vallys.com').first()
                if not admin:
                    admin = User(username='admin', email='admin@vallys.com', is_admin=True)
                    admin.set_password('Admin123')
                    db.session.add(admin)
                    db.session.commit()
                    print("✅ Admin user created: admin@vallys.com / Admin123")
            
            return True
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

# ========= PUBLIC ROUTES (No login required) =========
@app.route('/')
def home():
    # Get featured completed jobs for homepage
    featured_jobs = CompletedJob.query.filter_by(featured=True).order_by(CompletedJob.created_at.desc()).limit(3).all()
    return render_template('home.html', featured_jobs=featured_jobs)

@app.route('/services')
def services():
    services_data = [
        {
            'name': 'Long Knotless Braids',
            'description': 'Elegant and comfortable long knotless braids that last for weeks.',
            'icon': '💇‍♀️',
            'duration': '4-5 hours',
            'prices': [
                {'size': 'Large Boxes', 'price': 'R180'},
                {'size': 'Medium Boxes', 'price': 'R200'},
                {'size': 'Small Boxes', 'price': 'R250'}
            ]
        },
        {
            'name': 'Short Knotless Braids',
            'description': 'Stylish and practical short braids perfect for everyday wear.',
            'icon': '💇‍♀️',
            'duration': '2-4 hours',
            'prices': [
                {'size': 'Large Boxes', 'price': 'R150'},
                {'size': 'Medium Boxes', 'price': 'R180'},
                {'size': 'Small Boxes', 'price': 'R200'}
            ]
        },
        {
            'name': 'Cluster Lashes',
            'description': 'Enhance your natural beauty with our premium cluster lashes.',
            'icon': '👁️',
            'duration': '15-30 mins',
            'prices': [
                {'option': 'Lashes Only', 'price': 'R70'},
                {'option': 'With Braids', 'price': 'R50'}
            ]
        }
    ]
    return render_template('services.html', services=services_data)

@app.route('/about')
def about():
    return render_template('about.html')

# NEW ROUTE: Portfolio/Gallery
@app.route('/portfolio')
def portfolio():
    """Showcase completed jobs/portfolio"""
    jobs = CompletedJob.query.order_by(CompletedJob.created_at.desc()).all()
    return render_template('portfolio.html', jobs=jobs)

# ========= PROTECTED ROUTES (Login required) =========
@app.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        service = request.form.get('service')
        braid_size = request.form.get('braid_size')
        date_str = request.form.get('date')
        time = request.form.get('time')
        special_requests = request.form.get('special_requests')
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            flash('❌ Invalid date format', 'error')
            return redirect(url_for('book'))
        
        appointment = Appointment(
            customer_name=name,
            customer_email=email,
            customer_phone=phone,
            service_type=service,
            braid_size=braid_size,
            appointment_date=date_obj,
            appointment_time=time,
            special_requests=special_requests,
            user_id=current_user.id
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        flash('🎉 Appointment booked successfully! We will confirm soon.', 'success')
        return redirect(url_for('my_appointments'))
    
    # Generate time slots
    time_slots = []
    for hour in range(9, 19):
        for minute in ['00', '30']:
            time_str = f"{hour:02d}:{minute}"
            if hour < 12:
                time_slots.append(f"{time_str} AM")
            elif hour == 12:
                time_slots.append(f"12:{minute} PM")
            else:
                time_slots.append(f"{hour-12:02d}:{minute} PM")
    
    tomorrow = datetime.now() + timedelta(days=1)
    return render_template('book.html', time_slots=time_slots, tomorrow=tomorrow)

@app.route('/my-appointments')
@login_required
def my_appointments():
    """Show all appointments for the logged-in user"""
    appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.created_at.desc()).all()
    return render_template('my_appointments.html', appointments=appointments)

@app.route('/check-status', methods=['GET', 'POST'])
@login_required
def check_status():
    appointment = None
    if request.method == 'POST':
        phone = request.form.get('phone')
        # Users can only check their own appointments
        appointment = Appointment.query.filter_by(
            customer_phone=phone,
            user_id=current_user.id
        ).order_by(Appointment.created_at.desc()).first()
        
        if not appointment:
            flash('❌ No appointment found for this phone number under your account', 'error')
    
    return render_template('check_status.html', appointment=appointment)

@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message_text = request.form.get('message')
        
        message = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_text,
            user_id=current_user.id
        )
        
        db.session.add(message)
        db.session.commit()
        
        flash('📩 Message sent successfully! We will respond soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# ========= AUTHENTICATION ROUTES =========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Find user by email only
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'✅ Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('home'))
        else:
            flash('❌ Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate password strength
        if len(password) < 8:
            flash("❌ Password must be at least 8 characters long!", "error")
            return redirect(url_for('register'))
        
        # Check for special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(char in special_chars for char in password):
            flash("❌ Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)", "error")
            return redirect(url_for('register'))
        
        # Check for at least one number
        if not any(char.isdigit() for char in password):
            flash("❌ Password must contain at least one number!", "error")
            return redirect(url_for('register'))
        
        # Check for at least one uppercase letter
        if not any(char.isupper() for char in password):
            flash("❌ Password must contain at least one uppercase letter!", "error")
            return redirect(url_for('register'))
        
        # Check for at least one lowercase letter
        if not any(char.islower() for char in password):
            flash("❌ Password must contain at least one lowercase letter!", "error")
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('❌ Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('❌ Email already registered', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('❌ Username already taken', 'error')
            return redirect(url_for('register'))
        
        # Regular users are NOT admins by default
        user = User(username=username, email=email, is_admin=False)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('✅ Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('✅ Logged out successfully', 'success')
    return redirect(url_for('home'))

# ========= ADMIN ROUTES (Protected by is_admin check) =========
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Check if user is admin
    if not current_user.is_admin:
        flash('❌ Admin access required', 'error')
        return redirect(url_for('home'))
    
    # Get statistics
    total_appointments = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='pending').count()
    confirmed_appointments = Appointment.query.filter_by(status='confirmed').count()
    cancelled_appointments = Appointment.query.filter_by(status='cancelled').count()
    
    total_messages = ContactMessage.query.count()
    unread_messages = ContactMessage.query.filter_by(read=False).count()
    read_messages = ContactMessage.query.filter_by(read=True).count()
    
    total_users = User.query.count()
    total_jobs = CompletedJob.query.count()
    featured_jobs = CompletedJob.query.filter_by(featured=True).count()
    
    # Get recent appointments (last 5)
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()
    
    # Get recent messages (last 5)
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    
    # Get recent jobs (last 5)
    recent_jobs = CompletedJob.query.order_by(CompletedJob.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         confirmed_appointments=confirmed_appointments,
                         cancelled_appointments=cancelled_appointments,
                         total_messages=total_messages,
                         unread_messages=unread_messages,
                         read_messages=read_messages,
                         total_users=total_users,
                         total_jobs=total_jobs,
                         featured_jobs=featured_jobs,
                         recent_appointments=recent_appointments,
                         recent_messages=recent_messages,
                         recent_jobs=recent_jobs)

@app.route('/admin/appointments')
@login_required
def admin_appointments():
    # Check if user is admin
    if not current_user.is_admin:
        flash('❌ Admin access required', 'error')
        return redirect(url_for('home'))
    
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    return render_template('admin_appointments.html', appointments=appointments)

@app.route('/admin/messages')
@login_required
def admin_messages():
    # Check if user is admin
    if not current_user.is_admin:
        flash('❌ Admin access required', 'error')
        return redirect(url_for('home'))
    
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin_messages.html', messages=messages)

# NEW ADMIN ROUTES: Portfolio Management
@app.route('/admin/portfolio')
@login_required
def admin_portfolio():
    # Check if user is admin
    if not current_user.is_admin:
        flash('❌ Admin access required', 'error')
        return redirect(url_for('home'))
    
    jobs = CompletedJob.query.order_by(CompletedJob.created_at.desc()).all()
    return render_template('admin_portfolio.html', jobs=jobs)

@app.route('/admin/portfolio/add', methods=['GET', 'POST'])
@login_required
def add_portfolio_item():
    # Check if user is admin
    if not current_user.is_admin:
        flash('❌ Admin access required', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        service_type = request.form.get('service_type')
        featured = True if request.form.get('featured') else False
        
        # Handle file upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to make filename unique
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = f"uploads/{filename}"
        
        job = CompletedJob(
            title=title,
            description=description,
            service_type=service_type,
            image_url=image_url,
            featured=featured
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash('✅ Portfolio item added successfully!', 'success')
        return redirect(url_for('admin_portfolio'))
    
    service_types = ['Long Knotless Braids', 'Short Knotless Braids', 'Cluster Lashes', 'Other']
    return render_template('add_portfolio_item.html', service_types=service_types)

@app.route('/admin/portfolio/edit/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_portfolio_item(job_id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('❌ Admin access required', 'error')
        return redirect(url_for('home'))
    
    job = CompletedJob.query.get_or_404(job_id)
    
    if request.method == 'POST':
        job.title = request.form.get('title')
        job.description = request.form.get('description')
        job.service_type = request.form.get('service_type')
        job.featured = True if request.form.get('featured') else False
        
        # Handle file upload (optional - only if new file is provided)
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Delete old image if exists
                if job.image_url:
                    old_path = os.path.join('static', job.image_url)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Save new image
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                job.image_url = f"uploads/{filename}"
        
        db.session.commit()
        flash('✅ Portfolio item updated successfully!', 'success')
        return redirect(url_for('admin_portfolio'))
    
    service_types = ['Long Knotless Braids', 'Short Knotless Braids', 'Cluster Lashes', 'Other']
    return render_template('edit_portfolio_item.html', job=job, service_types=service_types)

@app.route('/admin/portfolio/delete/<int:job_id>', methods=['POST'])
@login_required
def delete_portfolio_item(job_id):
    # Check if user is admin
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    job = CompletedJob.query.get_or_404(job_id)
    
    # Delete image file if exists
    if job.image_url:
        image_path = os.path.join('static', job.image_url)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(job)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/admin/portfolio/toggle-featured/<int:job_id>', methods=['POST'])
@login_required
def toggle_featured(job_id):
    # Check if user is admin
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    job = CompletedJob.query.get_or_404(job_id)
    job.featured = not job.featured
    db.session.commit()
    
    return jsonify({'success': True, 'featured': job.featured})

@app.route('/admin/appointments/confirm/<int:appointment_id>')
@login_required
def confirm_appointment(appointment_id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('❌ Admin access required', 'error')
        return redirect(url_for('home'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'confirmed'
    db.session.commit()
    flash('✅ Appointment confirmed!', 'success')
    return redirect(url_for('admin_appointments'))

@app.route('/admin/appointments/cancel/<int:appointment_id>')
@login_required
def cancel_appointment(appointment_id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('❌ Admin access required', 'error')
        return redirect(url_for('home'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'cancelled'
    db.session.commit()
    flash('❌ Appointment cancelled!', 'info')
    return redirect(url_for('admin_appointments'))

# Admin message actions
@app.route('/admin/messages/read/<int:message_id>', methods=['POST'])
@login_required
def mark_message_read(message_id):
    # Check if user is admin
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    message = ContactMessage.query.get_or_404(message_id)
    message.read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/messages/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    # Check if user is admin
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    return jsonify({'success': True})

# ========= API ENDPOINTS =========
@app.route('/available-slots')
def available_slots():
    date_str = request.args.get('date')
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return jsonify([])
    
    appointments = Appointment.query.filter_by(appointment_date=date_obj).all()
    time_counts = {}
    for apt in appointments:
        time_counts[apt.appointment_time] = time_counts.get(apt.appointment_time, 0) + 1
    
    # Max 2 appointments per time slot
    full_slots = [time for time, count in time_counts.items() if count >= 2]
    return jsonify(full_slots)

# ========= ERROR HANDLERS =========
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ========= MAIN ENTRY POINT =========
if __name__ == '__main__':
    with app.app_context():
        if check_and_fix_database():
            print("\n" + "="*70)
            print("✨ VALLY'S DIVINE HAIR - SERVER READY! ✨")
            print("="*70)
            print("\n✅ Database is properly configured")
            print("✅ All columns confirmed present")
            print("✅ Password validation: 8+ chars, uppercase, lowercase, number, special char")
            print("\n🔐 DEFAULT ADMIN ACCOUNT:")
            print("   Email: admin@vallys.com")
            print("   Password: Admin123")
            print("\n🌐 PUBLIC PAGES (Browse Without Login):")
            print("   🏠 Home: http://127.0.0.1:5000")
            print("   💇 Services: http://127.0.0.1:5000/services")
            print("   🎨 Portfolio: http://127.0.0.1:5000/portfolio")
            print("   ℹ️  About: http://127.0.0.1:5000/about")
            print("\n🔐 PROTECTED PAGES (Login Required):")
            print("   📅 Book: http://127.0.0.1:5000/book")
            print("   📋 My Appointments: http://127.0.0.1:5000/my-appointments")
            print("   🔍 Check Status: http://127.0.0.1:5000/check-status")
            print("   💬 Contact: http://127.0.0.1:5000/contact")
            print("\n🔓 AUTH PAGES:")
            print("   🔐 Login: http://127.0.0.1:5000/login")
            print("   ✨ Register: http://127.0.0.1:5000/register")
            print("\n👑 ADMIN URLS (Login as admin first!):")
            print("   📊 Dashboard: http://127.0.0.1:5000/admin/dashboard")
            print("   📋 Appointments: http://127.0.0.1:5000/admin/appointments")
            print("   📨 Messages: http://127.0.0.1:5000/admin/messages")
            print("   🎨 Portfolio: http://127.0.0.1:5000/admin/portfolio")
            print("   ➕ Add Portfolio Item: http://127.0.0.1:5000/admin/portfolio/add")
            print("="*70 + "\n")
        else:
            print("\n❌ Database setup failed. Please check MySQL connection.")
            print("   Make sure MySQL is running and hair_salon_db exists.")
            exit(1)
    
    app.run(debug=True)