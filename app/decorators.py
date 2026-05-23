"""Shared route decorators for role-based access control."""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def candidate_required(f):
    """Requires user to be logged in as a candidate."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_candidate():
            flash('Access denied. Candidate access required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def employer_required(f):
    """Requires user to be logged in as an employer and approved."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_employer():
            flash('Access denied. Employer access required.', 'error')
            return redirect(url_for('main.index'))
        if not current_user.is_approved:
            flash('Your account is pending approval.', 'warning')
            return redirect(url_for('auth.pending'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Requires user to be logged in as an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('Access denied. Admin access required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
