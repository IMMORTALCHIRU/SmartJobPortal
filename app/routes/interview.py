from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.interview import MockInterview
from app.models.question import Question
from app.models.resume import Resume
from app.services.question_service import QuestionService
from app.services.feedback_service import FeedbackService
from app.services.recommendation_service import RecommendationService
from app.decorators import candidate_required
from app.config import Config
from datetime import datetime

interview_bp = Blueprint('interview', __name__)

@candidate_required
@interview_bp.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    if request.method == 'POST':
        interview_type = request.form.get('interview_type')
        difficulty = request.form.get('difficulty', 'medium')
        question_count = int(request.form.get('question_count', 10))
        
        if not interview_type:
            flash('Please select an interview type', 'error')
            return redirect(request.url)
        
        # Get user's resume for skill-based questions
        resume = Resume.get_latest_by_user(current_user.id)
        skills = resume.skills if resume else []
        
        # Get questions
        questions = QuestionService.get_questions_for_interview(
            interview_type, skills, difficulty, question_count
        )
        
        if not questions:
            flash('No questions available for this interview type. Please try another.', 'warning')
            return redirect(request.url)
        
        # Create interview
        interview_data = {
            'interview_type': interview_type,
            'difficulty': difficulty,
            'scheduled_time': datetime.utcnow(),
            'questions': [q.id for q in questions],
            'total_questions': len(questions),
            'skills_tested': list(set(tag for q in questions for tag in q.tags))
        }
        
        interview = MockInterview.create(current_user.id, interview_data)
        flash('Interview scheduled! Click Start to begin.', 'success')
        return redirect(url_for('interview.session', interview_id=interview.id))
    
    # Get recommended interview types
    recommended_types = RecommendationService.get_interview_type_recommendations(current_user.id)
    
    return render_template('interview/schedule.html', 
                          interview_types=Config.INTERVIEW_TYPES,
                          recommended_types=recommended_types)

@candidate_required
@interview_bp.route('/session/<interview_id>', methods=['GET', 'POST'])
@login_required
def session(interview_id):
    interview = MockInterview.get_by_id(interview_id)
    
    if not interview or interview.user_id != current_user.id:
        flash('Interview not found', 'error')
        return redirect(url_for('interview.schedule'))
    
    if interview.status == 'completed':
        return redirect(url_for('interview.results', interview_id=interview_id))
    
    if request.method == 'POST':
        # Process answers
        answers = {}
        for key, value in request.form.items():
            if key.startswith('answer_'):
                question_id = key.replace('answer_', '')
                answers[question_id] = value
        
        # Get questions and evaluate
        questions = [Question.get_by_id(qid) for qid in interview.questions]
        questions = [q for q in questions if q]  # Filter None
        
        evaluation = QuestionService.evaluate_answers(questions, answers)
        
        # Calculate time taken
        start_time = interview.started_at or datetime.utcnow()
        time_taken = (datetime.utcnow() - start_time).total_seconds()
        
        # Complete interview
        interview.complete(
            answers=answers,
            score=evaluation['score'],
            correct_answers=evaluation['correct'],
            time_taken=int(time_taken)
        )
        
        # Generate feedback
        FeedbackService.generate_feedback(current_user.id, interview_id, evaluation)
        
        # Update recommendations
        RecommendationService.generate_job_recommendations(current_user.id)
        
        flash('Interview completed! Check your results.', 'success')
        return redirect(url_for('interview.results', interview_id=interview_id))
    
    # Start interview if not started
    if interview.status == 'scheduled':
        interview.start()
    
    # Get questions
    questions = [Question.get_by_id(qid) for qid in interview.questions]
    questions = [q for q in questions if q]
    
    return render_template('interview/session.html', 
                          interview=interview, 
                          questions=questions)

@candidate_required
@interview_bp.route('/results/<interview_id>')
@login_required
def results(interview_id):
    interview = MockInterview.get_by_id(interview_id)
    
    if not interview or interview.user_id != current_user.id:
        flash('Interview not found', 'error')
        return redirect(url_for('interview.schedule'))
    
    if interview.status != 'completed':
        return redirect(url_for('interview.session', interview_id=interview_id))
    
    # Get feedback
    from app.models.feedback import Feedback
    feedback = Feedback.get_by_interview(interview_id)
    
    # Get questions with answers
    questions = [Question.get_by_id(qid) for qid in interview.questions]
    questions = [q for q in questions if q]
    
    # Create results with user answers
    results = []
    for question in questions:
        user_answer = interview.answers.get(question.id, '')
        is_correct = user_answer.strip().lower() == question.correct_answer.strip().lower()
        results.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct
        })
    
    return render_template('interview/results.html', 
                          interview=interview, 
                          feedback=feedback,
                          results=results)

@candidate_required
@interview_bp.route('/history')
@login_required
def history():
    interviews = MockInterview.get_by_user(current_user.id)
    return render_template('interview/history.html', interviews=interviews)