from bson import ObjectId
from datetime import datetime
from app import mongo

class Question:
    def __init__(self, question_data):
        self.id = str(question_data.get('_id'))
        self.question_text = question_data.get('question_text')
        self.question_type = question_data.get('question_type', 'mcq')
        self.options = question_data.get('options', [])
        self.correct_answer = question_data.get('correct_answer')
        self.explanation = question_data.get('explanation', '')
        self.difficulty = question_data.get('difficulty', 'medium')
        self.category = question_data.get('category')
        self.tags = question_data.get('tags', [])
        self.points = question_data.get('points', 10)
    
    @staticmethod
    def create(question_data):
        question_data['created_at'] = datetime.utcnow()
        result = mongo.db.questions.insert_one(question_data)
        question_data['_id'] = result.inserted_id
        return Question(question_data)
    
    @staticmethod
    def get_by_id(question_id):
        try:
            question_data = mongo.db.questions.find_one({'_id': ObjectId(question_id)})
            if question_data:
                return Question(question_data)
        except:
            pass
        return None
    
    @staticmethod
    def get_by_category(category, difficulty=None, limit=10):
        query = {'category': category}
        if difficulty:
            query['difficulty'] = difficulty
        questions = mongo.db.questions.aggregate([
            {'$match': query},
            {'$sample': {'size': limit}}
        ])
        return [Question(q) for q in questions]
    
    @staticmethod
    def get_by_tags(tags, difficulty=None, limit=10):
        query = {'tags': {'$in': tags}}
        if difficulty:
            query['difficulty'] = difficulty
        questions = mongo.db.questions.aggregate([
            {'$match': query},
            {'$sample': {'size': limit}}
        ])
        return [Question(q) for q in questions]
    
    def to_dict(self, include_answer=False):
        data = {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'options': self.options,
            'difficulty': self.difficulty,
            'category': self.category,
            'tags': self.tags,
            'points': self.points
        }
        if include_answer:
            data['correct_answer'] = self.correct_answer
            data['explanation'] = self.explanation
        return data