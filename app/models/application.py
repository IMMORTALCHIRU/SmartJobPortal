from bson import ObjectId
from datetime import datetime
from app import mongo


class Application:
    STATUS_APPLIED = 'applied'
    STATUS_INTERVIEW_PENDING = 'interview_pending'
    STATUS_INTERVIEW_COMPLETED = 'interview_completed'
    STATUS_SHORTLISTED = 'shortlisted'
    STATUS_REJECTED = 'rejected'

    def __init__(self, app_data):
        self.id = str(app_data.get('_id'))
        self.candidate_id = str(app_data.get('candidate_id'))
        self.job_id = str(app_data.get('job_id'))
        self.employer_id = str(app_data.get('employer_id'))
        self.resume_id = str(app_data.get('resume_id', ''))
        self.resume_score = app_data.get('resume_score', 0)
        self.interview_id = str(app_data.get('interview_id', '')) if app_data.get('interview_id') else ''
        self.interview_score = app_data.get('interview_score', 0)
        self.status = app_data.get('status', self.STATUS_APPLIED)
        self.applied_at = app_data.get('applied_at', datetime.utcnow())
        self.updated_at = app_data.get('updated_at', datetime.utcnow())
        self.notes = app_data.get('notes', '')

    @staticmethod
    def create(candidate_id, job_id, employer_id, resume_id, resume_score):
        app_data = {
            'candidate_id': ObjectId(candidate_id),
            'job_id': ObjectId(job_id),
            'employer_id': ObjectId(employer_id),
            'resume_id': ObjectId(resume_id),
            'resume_score': resume_score,
            'interview_id': None,
            'interview_score': 0,
            'status': Application.STATUS_APPLIED,
            'applied_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'notes': '',
        }
        result = mongo.db.applications.insert_one(app_data)
        app_data['_id'] = result.inserted_id
        return Application(app_data)

    @staticmethod
    def get_by_id(app_id):
        try:
            app_data = mongo.db.applications.find_one({'_id': ObjectId(app_id)})
            if app_data:
                return Application(app_data)
        except Exception:
            pass
        return None

    @staticmethod
    def get_by_candidate(candidate_id):
        apps = mongo.db.applications.find(
            {'candidate_id': ObjectId(candidate_id)}
        ).sort('applied_at', -1)
        return [Application(a) for a in apps]

    @staticmethod
    def get_by_job(job_id):
        apps = mongo.db.applications.find(
            {'job_id': ObjectId(job_id)}
        ).sort('resume_score', -1)
        return [Application(a) for a in apps]

    @staticmethod
    def get_by_employer(employer_id):
        apps = mongo.db.applications.find(
            {'employer_id': ObjectId(employer_id)}
        ).sort('applied_at', -1)
        return [Application(a) for a in apps]

    @staticmethod
    def get_by_candidate_and_job(candidate_id, job_id):
        app_data = mongo.db.applications.find_one({
            'candidate_id': ObjectId(candidate_id),
            'job_id': ObjectId(job_id)
        })
        if app_data:
            return Application(app_data)
        return None

    @staticmethod
    def count_by_employer(employer_id):
        return mongo.db.applications.count_documents({'employer_id': ObjectId(employer_id)})

    @staticmethod
    def count_by_employer_and_status(employer_id, status):
        return mongo.db.applications.count_documents({
            'employer_id': ObjectId(employer_id),
            'status': status
        })

    @staticmethod
    def count_by_candidate(candidate_id):
        return mongo.db.applications.count_documents({'candidate_id': ObjectId(candidate_id)})

    def update_status(self, status, notes=''):
        mongo.db.applications.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'status': status, 'notes': notes, 'updated_at': datetime.utcnow()}}
        )
        self.status = status

    def attach_interview(self, interview_id):
        """Attach a scheduled interview to this application without marking it completed."""
        try:
            mongo.db.applications.update_one(
                {'_id': ObjectId(self.id)},
                {'$set': {'interview_id': ObjectId(interview_id), 'updated_at': datetime.utcnow()}}
            )
            self.interview_id = str(interview_id)
            return True
        except Exception:
            return False

    def set_interview(self, interview_id, interview_score=0):
        mongo.db.applications.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {
                'interview_id': ObjectId(interview_id),
                'interview_score': interview_score,
                'status': Application.STATUS_INTERVIEW_COMPLETED,
                'updated_at': datetime.utcnow()
            }}
        )

    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'job_id': self.job_id,
            'employer_id': self.employer_id,
            'resume_score': self.resume_score,
            'interview_score': self.interview_score,
            'status': self.status,
            'applied_at': self.applied_at,
        }
