from bson import ObjectId
from datetime import datetime
from app import mongo

class Feedback:
    def __init__(self, feedback_data):
        self.id = str(feedback_data.get('_id'))
        self.user_id = str(feedback_data.get('user_id'))
        self.interview_id = str(feedback_data.get('interview_id'))
        self.feedback_summary = feedback_data.get('feedback_summary', '')
        self.strong_topics = feedback_data.get('strong_topics', [])
        self.weak_topics = feedback_data.get('weak_topics', [])
        self.improvement_suggestions = feedback_data.get('improvement_suggestions', [])
        self.score = feedback_data.get('score', 0)
        self.created_at = feedback_data.get('created_at', datetime.utcnow())
        self.topic_scores = feedback_data.get('topic_scores', {})
    
    @staticmethod
    def create(user_id, interview_id, feedback_data):
        feedback_data['user_id'] = ObjectId(user_id)
        feedback_data['interview_id'] = ObjectId(interview_id)
        feedback_data['created_at'] = datetime.utcnow()
        result = mongo.db.feedback.insert_one(feedback_data)
        feedback_data['_id'] = result.inserted_id
        return Feedback(feedback_data)
    
    @staticmethod
    def get_by_interview(interview_id):
        try:
            feedback_data = mongo.db.feedback.find_one({'interview_id': ObjectId(interview_id)})
            if feedback_data:
                return Feedback(feedback_data)
        except:
            pass
        return None
    
    @staticmethod
    def get_by_user(user_id, limit=10):
        feedbacks = mongo.db.feedback.find(
            {'user_id': ObjectId(user_id)}
        ).sort('created_at', -1).limit(limit)
        return [Feedback(f) for f in feedbacks]
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'interview_id': self.interview_id,
            'feedback_summary': self.feedback_summary,
            'strong_topics': self.strong_topics,
            'weak_topics': self.weak_topics,
            'improvement_suggestions': self.improvement_suggestions,
            'score': self.score,
            'created_at': self.created_at,
            'topic_scores': self.topic_scores
        }