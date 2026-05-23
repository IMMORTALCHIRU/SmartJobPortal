from flask import Blueprint, redirect, url_for
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def main():
    """Redirect to the correct dashboard based on user role."""
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'employer':
        if not current_user.is_approved:
            return redirect(url_for('auth.pending'))
        return redirect(url_for('employer.dashboard'))
    else:
        return redirect(url_for('candidate.dashboard'))