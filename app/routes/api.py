from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.analytics_service import AnalyticsService
from app.models.interview import MockInterview
from app.models.question import Question

api_bp = Blueprint('api', __name__)

@api_bp.route('/analytics')
@login_required
def get_analytics():
    analytics = AnalyticsService.get_user_analytics(current_user.id)
    return jsonify(analytics)

@api_bp.route('/chart-data')
@login_required
def get_chart_data():
    chart_data = AnalyticsService.get_performance_chart_data(current_user.id)
    return jsonify(chart_data)

@api_bp.route('/interviews')
@login_required
def get_interviews():
    status = request.args.get('status')
    interviews = MockInterview.get_by_user(current_user.id, status)
    return jsonify([i.to_dict() for i in interviews])

@api_bp.route('/question/<question_id>')
@login_required
def get_question(question_id):
    question = Question.get_by_id(question_id)
    if question:
        return jsonify(question.to_dict(include_answer=False))
    return jsonify({'error': 'Question not found'}), 404