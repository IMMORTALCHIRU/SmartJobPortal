from bson import ObjectId
from datetime import datetime
from app import mongo


class JobPosting:
    def __init__(self, job_data):
        self.id = str(job_data.get('_id'))
        self.employer_id = str(job_data.get('employer_id'))
        self.title = job_data.get('title', '')
        self.company_name = job_data.get('company_name', '')
        self.company_logo = job_data.get('company_logo', '')
        self.description = job_data.get('description', '')
        self.required_skills = job_data.get('required_skills', [])
        self.experience_required = job_data.get('experience_required', 0)
        self.education_required = job_data.get('education_required', '')
        self.location = job_data.get('location', '')
        self.job_type = job_data.get('job_type', 'Full-time')
        self.salary_range = job_data.get('salary_range', '')
        self.field = job_data.get('field', '')
        self.min_resume_score = job_data.get('min_resume_score', 50)
        self.interview_criteria_score = job_data.get('interview_criteria_score', 60)
        self.num_questions = job_data.get('num_questions', 10)
        self.difficulty = job_data.get('difficulty', 'medium')
        self.is_active = job_data.get('is_active', True)
        self.created_at = job_data.get('created_at', datetime.utcnow())
        self.deadline = job_data.get('deadline')
        self.applicant_count = job_data.get('applicant_count', 0)

    @staticmethod
    def create(employer_id, job_data):
        job_data['employer_id'] = ObjectId(employer_id)
        job_data['created_at'] = datetime.utcnow()
        job_data['is_active'] = True
        job_data['applicant_count'] = 0
        result = mongo.db.job_postings.insert_one(job_data)
        job_data['_id'] = result.inserted_id
        return JobPosting(job_data)

    @staticmethod
    def get_by_id(job_id):
        try:
            job_data = mongo.db.job_postings.find_one({'_id': ObjectId(job_id)})
            if job_data:
                return JobPosting(job_data)
        except Exception:
            pass
        return None

    @staticmethod
    def get_by_employer(employer_id, active_only=False):
        query = {'employer_id': ObjectId(employer_id)}
        if active_only:
            query['is_active'] = True
        jobs = mongo.db.job_postings.find(query).sort('created_at', -1)
        return [JobPosting(j) for j in jobs]

    @staticmethod
    def get_all_active():
        jobs = mongo.db.job_postings.find({'is_active': True}).sort('created_at', -1)
        return [JobPosting(j) for j in jobs]

    @staticmethod
    def get_matching_jobs(skills, experience_years, limit=10):
        """Get jobs that match candidate skills"""
        skills_lower = [s.lower() for s in skills]
        all_jobs = list(mongo.db.job_postings.find({'is_active': True}))
        scored_jobs = []
        for job_data in all_jobs:
            job = JobPosting(job_data)
            required = [s.lower() for s in job.required_skills]
            if not required:
                continue
            matched = sum(1 for s in required if s in skills_lower)
            skill_match = matched / len(required)
            exp_ok = experience_years >= job.experience_required
            score = (skill_match * 0.7) + (0.3 if exp_ok else 0)
            if score > 0.2:
                scored_jobs.append((score, job))
        scored_jobs.sort(key=lambda x: x[0], reverse=True)
        return [j for _, j in scored_jobs[:limit]]

    @staticmethod
    def count_active():
        return mongo.db.job_postings.count_documents({'is_active': True})

    def update(self, data):
        allowed = [
            'title', 'description', 'required_skills', 'experience_required',
            'education_required', 'location', 'job_type', 'salary_range',
            'field', 'min_resume_score', 'interview_criteria_score',
            'num_questions', 'difficulty', 'is_active', 'deadline'
        ]
        update_data = {k: v for k, v in data.items() if k in allowed}
        if update_data:
            mongo.db.job_postings.update_one(
                {'_id': ObjectId(self.id)},
                {'$set': update_data}
            )

    def delete(self):
        mongo.db.job_postings.delete_one({'_id': ObjectId(self.id)})

    def increment_applicants(self):
        mongo.db.job_postings.update_one(
            {'_id': ObjectId(self.id)},
            {'$inc': {'applicant_count': 1}}
        )

    def to_dict(self):
        return {
            'id': self.id,
            'employer_id': self.employer_id,
            'title': self.title,
            'company_name': self.company_name,
            'company_logo': self.company_logo,
            'description': self.description,
            'required_skills': self.required_skills,
            'experience_required': self.experience_required,
            'education_required': self.education_required,
            'location': self.location,
            'job_type': self.job_type,
            'salary_range': self.salary_range,
            'field': self.field,
            'min_resume_score': self.min_resume_score,
            'interview_criteria_score': self.interview_criteria_score,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'applicant_count': self.applicant_count,
        }
