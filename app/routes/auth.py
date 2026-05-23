import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.models.user import User
from app import mongo
import re

auth_bp = Blueprint('auth', __name__)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, ""

def redirect_by_role(user):
    if user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif user.role == 'employer':
        if not user.is_approved:
            return redirect(url_for('auth.pending'))
        return redirect(url_for('employer.dashboard'))
    else:
        return redirect(url_for('candidate.dashboard'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('auth/login.html')

        user = User.get_by_email(email)

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('auth/login.html')
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect_by_role(user)
        else:
            flash('Invalid email or password.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()

        errors = []

        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not validate_email(email):
            errors.append('Please enter a valid email address.')
        if User.get_by_email(email):
            errors.append('An account with this email already exists.')
        valid_password, password_error = validate_password(password)
        if not valid_password:
            errors.append(password_error)
        if password != confirm_password:
            errors.append('Passwords do not match.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html', name=name, email=email, phone=phone, location=location)

        user = User.create(name, email, password, role='candidate',
                           extra_data={'phone': phone, 'location': location})
        login_user(user)
        flash(f'Welcome to Smart Job Portal, {name}! Upload your resume to get started.', 'success')
        return redirect(url_for('candidate.dashboard'))

    return render_template('auth/register.html')


@auth_bp.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        company_name = request.form.get('company_name', '').strip()
        company_description = request.form.get('company_description', '').strip()
        company_website = request.form.get('company_website', '').strip()
        company_size = request.form.get('company_size', '').strip()
        industry = request.form.get('industry', '').strip()
        years_in_business = request.form.get('years_in_business', '').strip()
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()

        errors = []

        if not name or len(name) < 2:
            errors.append('Contact person name must be at least 2 characters.')
        if not validate_email(email):
            errors.append('Please enter a valid email address.')
        if User.get_by_email(email):
            errors.append('An account with this email already exists.')
        valid_password, password_error = validate_password(password)
        if not valid_password:
            errors.append(password_error)
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if not company_name:
            errors.append('Company name is required.')
        if not industry:
            errors.append('Industry is required.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register_employer.html',
                                   name=name, email=email, company_name=company_name,
                                   company_description=company_description,
                                   company_website=company_website, industry=industry,
                                   years_in_business=years_in_business, phone=phone, location=location)

        company_logo = ''
        logo_file = request.files.get('company_logo')
        if logo_file and logo_file.filename and allowed_image(logo_file.filename):
            logo_filename = secure_filename(f"logo_{email.replace('@', '_')}_{logo_file.filename}")
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], logo_filename)
            logo_file.save(logo_path)
            company_logo = logo_filename

        extra_data = {
            'company_name': company_name,
            'company_logo': company_logo,
            'company_description': company_description,
            'company_website': company_website,
            'company_size': company_size,
            'industry': industry,
            'years_in_business': years_in_business,
            'phone': phone,
            'location': location,
        }
        User.create(name, email, password, role='employer', extra_data=extra_data)
        flash('Registration submitted! Your account is pending admin approval.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_employer.html')


@auth_bp.route('/pending')
@login_required
def pending():
    if current_user.role != 'employer':
        return redirect_by_role(current_user)
    if current_user.is_approved:
        return redirect(url_for('employer.dashboard'))
    return render_template('auth/pending.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))