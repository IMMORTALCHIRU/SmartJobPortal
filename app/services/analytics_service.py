from app.models.interview import MockInterview
from app.models.feedback import Feedback
from app.models.resume import Resume
from datetime import datetime, timedelta
from collections import defaultdict

class AnalyticsService:
    
    @staticmethod
    def get_user_analytics(user_id):
        """Get comprehensive analytics for a user"""
        interviews = MockInterview.get_completed_by_user(user_id, limit=50)
        feedbacks = Feedback.get_by_user(user_id, limit=50)
        resume = Resume.get_latest_by_user(user_id)
        
        analytics = {
            'total_interviews': len(interviews),
            'average_score': 0,
            'best_score': 0,
            'worst_score': 100,
            'score_trend': [],
            'interviews_by_type': {},
            'skill_proficiency': {},
            'weak_areas': [],
            'strong_areas': [],
            'improvement_rate': 0,
            'recent_activity': []
        }
        
        if not interviews:
            return analytics
        
        # Calculate basic stats
        scores = [i.score for i in interviews]
        analytics['average_score'] = round(sum(scores) / len(scores), 2)
        analytics['best_score'] = max(scores)
        analytics['worst_score'] = min(scores)
        
        # Score trend (last 10 interviews)
        recent_interviews = sorted(interviews, key=lambda x: x.completed_at or datetime.min)[-10:]
        analytics['score_trend'] = [
            {
                'date': i.completed_at.strftime('%Y-%m-%d') if i.completed_at else '',
                'score': i.score,
                'type': i.interview_type
            }
            for i in recent_interviews
        ]
        
        # Interviews by type
        type_stats = defaultdict(lambda: {'count': 0, 'total_score': 0, 'scores': []})
        for interview in interviews:
            itype = interview.interview_type
            type_stats[itype]['count'] += 1
            type_stats[itype]['total_score'] += interview.score
            type_stats[itype]['scores'].append(interview.score)
        
        analytics['interviews_by_type'] = {
            itype: {
                'count': data['count'],
                'average_score': round(data['total_score'] / data['count'], 2),
                'best_score': max(data['scores']),
                'worst_score': min(data['scores'])
            }
            for itype, data in type_stats.items()
        }
        
        # Skill proficiency from feedback
        topic_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
        for feedback in feedbacks:
            for topic, data in feedback.topic_scores.items():
                topic_performance[topic]['correct'] += data.get('correct', 0)
                topic_performance[topic]['total'] += data.get('total', 0)
        
        analytics['skill_proficiency'] = {
            topic: round(data['correct'] / data['total'] * 100, 2) if data['total'] > 0 else 0
            for topic, data in topic_performance.items()
        }
        
        # Strong and weak areas
        for topic, proficiency in analytics['skill_proficiency'].items():
            if proficiency >= 70:
                analytics['strong_areas'].append(topic)
            elif proficiency < 50:
                analytics['weak_areas'].append(topic)
        
        # Improvement rate (comparing first 5 vs last 5 interviews)
        if len(interviews) >= 10:
            sorted_interviews = sorted(interviews, key=lambda x: x.completed_at or datetime.min)
            first_5_avg = sum(i.score for i in sorted_interviews[:5]) / 5
            last_5_avg = sum(i.score for i in sorted_interviews[-5:]) / 5
            analytics['improvement_rate'] = round(last_5_avg - first_5_avg, 2)
        
        # Recent activity
        analytics['recent_activity'] = [
            {
                'type': 'interview',
                'description': f"{i.interview_type} - Score: {i.score}%",
                'date': i.completed_at.strftime('%Y-%m-%d %H:%M') if i.completed_at else '',
                'score': i.score
            }
            for i in recent_interviews[-5:]
        ]
        
        return analytics
    
    @staticmethod
    def get_performance_chart_data(user_id):
        """Get data formatted for charts"""
        interviews = MockInterview.get_completed_by_user(user_id, limit=20)
        
        if not interviews:
            return {
                'line_chart': {'labels': [], 'data': []},
                'radar_chart': {'labels': [], 'data': []},
                'bar_chart': {'labels': [], 'data': []}
            }
        
        # Line chart data (score over time)
        sorted_interviews = sorted(interviews, key=lambda x: x.completed_at or datetime.min)
        line_data = {
            'labels': [i.completed_at.strftime('%m/%d') if i.completed_at else '' for i in sorted_interviews],
            'data': [i.score for i in sorted_interviews]
        }
        
        # Radar chart data (skill proficiency)
        feedbacks = Feedback.get_by_user(user_id, limit=20)
        topic_scores = defaultdict(list)
        for feedback in feedbacks:
            for topic, data in feedback.topic_scores.items():
                if data.get('total', 0) > 0:
                    topic_scores[topic].append(data.get('percentage', 0))
        
        radar_data = {
            'labels': list(topic_scores.keys())[:8],
            'data': [round(sum(scores) / len(scores), 2) for scores in list(topic_scores.values())[:8]]
        }
        
        # Bar chart data (interviews by type)
        type_counts = defaultdict(int)
        type_scores = defaultdict(list)
        for interview in interviews:
            type_counts[interview.interview_type] += 1
            type_scores[interview.interview_type].append(interview.score)
        
        bar_data = {
            'labels': list(type_counts.keys()),
            'data': [round(sum(type_scores[t]) / len(type_scores[t]), 2) for t in type_counts.keys()]
        }
        
        return {
            'line_chart': line_data,
            'radar_chart': radar_data,
            'bar_chart': bar_data
        }