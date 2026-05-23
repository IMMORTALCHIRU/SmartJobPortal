from bson import ObjectId
from datetime import datetime
from app import mongo


class MockInterview:
    def __init__(self, interview_data):
        self.id = str(interview_data.get('_id'))
        self.user_id = str(interview_data.get('user_id'))
        self.job_id = str(interview_data.get('job_id')) if interview_data.get('job_id') else None
        self.interview_type = interview_data.get('interview_type')
        self.difficulty = interview_data.get('difficulty', 'medium')
        self.scheduled_time = interview_data.get('scheduled_time')
        self.started_at = interview_data.get('started_at')
        self.completed_at = interview_data.get('completed_at')
        self.status = interview_data.get('status', 'scheduled')
        self.questions = interview_data.get('questions', [])
        self.answers = interview_data.get('answers', {})
        self.score = interview_data.get('score', 0)
        self.total_questions = interview_data.get('total_questions', 0)
        self.correct_answers = interview_data.get('correct_answers', 0)
        self.time_taken = interview_data.get('time_taken', 0)
        self.skills_tested = interview_data.get('skills_tested', [])
    
    @staticmethod
    def create(user_id, interview_data):
        interview_data['user_id'] = ObjectId(user_id)
        if interview_data.get('job_id'):
            interview_data['job_id'] = ObjectId(interview_data['job_id'])
        interview_data['status'] = 'scheduled'
        interview_data['created_at'] = datetime.utcnow()
        result = mongo.db.mock_interviews.insert_one(interview_data)
        interview_data['_id'] = result.inserted_id
        return MockInterview(interview_data)
    
    @staticmethod
    def get_by_id(interview_id):
        try:
            interview_data = mongo.db.mock_interviews.find_one({'_id': ObjectId(interview_id)})
            if interview_data:
                return MockInterview(interview_data)
        except:
            pass
        return None
    
    @staticmethod
    def get_by_user(user_id, status=None):
        query = {'user_id': ObjectId(user_id)}
        if status:
            query['status'] = status
        interviews = mongo.db.mock_interviews.find(query).sort('scheduled_time', -1)
        return [MockInterview(i) for i in interviews]
    
    @staticmethod
    def get_completed_by_user(user_id, limit=10):
        interviews = mongo.db.mock_interviews.find({
            'user_id': ObjectId(user_id),
            'status': 'completed'
        }).sort('completed_at', -1).limit(limit)
        return [MockInterview(i) for i in interviews]
    
    def update(self, data):
        mongo.db.mock_interviews.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': data}
        )
    
    def start(self):
        self.update({
            'status': 'in_progress',
            'started_at': datetime.utcnow()
        })
    
    def complete(self, answers, score, correct_answers, time_taken):
        self.update({
            'status': 'completed',
            'completed_at': datetime.utcnow(),
            'answers': answers,
            'score': score,
            'correct_answers': correct_answers,
            'time_taken': time_taken
        })
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'interview_type': self.interview_type,
            'difficulty': self.difficulty,
            'scheduled_time': self.scheduled_time,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'status': self.status,
            'score': self.score,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'time_taken': self.time_taken,
            'skills_tested': self.skills_tested
        }