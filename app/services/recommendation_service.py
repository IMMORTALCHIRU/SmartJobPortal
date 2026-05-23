from app.models.recommendation import Recommendation
from app.models.resume import Resume
from app.models.interview import MockInterview
from app.config import Config

class RecommendationService:
    
    # Course recommendations by field
    COURSES = {
        'Data Science': [
            {'name': 'Machine Learning by Andrew NG', 'url': 'https://www.coursera.org/learn/machine-learning', 'platform': 'Coursera'},
            {'name': 'Deep Learning Specialization', 'url': 'https://www.coursera.org/specializations/deep-learning', 'platform': 'Coursera'},
            {'name': 'Data Science Professional Certificate', 'url': 'https://www.coursera.org/professional-certificates/ibm-data-science', 'platform': 'Coursera'},
            {'name': 'Python for Data Science', 'url': 'https://www.datacamp.com/tracks/data-scientist-with-python', 'platform': 'DataCamp'},
        ],
        'Web Development': [
            {'name': 'The Complete Web Developer Course', 'url': 'https://www.udemy.com/course/the-complete-web-developer-course-2/', 'platform': 'Udemy'},
            {'name': 'Full Stack Web Developer Nanodegree', 'url': 'https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044', 'platform': 'Udacity'},
            {'name': 'React - The Complete Guide', 'url': 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/', 'platform': 'Udemy'},
            {'name': 'Node.js Developer Course', 'url': 'https://www.udemy.com/course/the-complete-nodejs-developer-course-2/', 'platform': 'Udemy'},
        ],
        'Mobile Development': [
            {'name': 'Flutter & Dart Development Course', 'url': 'https://www.udemy.com/course/flutter-dart-the-complete-flutter-app-development-course/', 'platform': 'Udemy'},
            {'name': 'iOS App Development with Swift', 'url': 'https://www.coursera.org/specializations/app-development', 'platform': 'Coursera'},
            {'name': 'Android Development for Beginners', 'url': 'https://developer.android.com/courses', 'platform': 'Google'},
            {'name': 'React Native - The Practical Guide', 'url': 'https://www.udemy.com/course/react-native-the-practical-guide/', 'platform': 'Udemy'},
        ],
        'DevOps': [
            {'name': 'Docker and Kubernetes Complete Guide', 'url': 'https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/', 'platform': 'Udemy'},
            {'name': 'AWS Certified Solutions Architect', 'url': 'https://www.udemy.com/course/aws-certified-solutions-architect-associate/', 'platform': 'Udemy'},
            {'name': 'DevOps Engineering Course', 'url': 'https://www.coursera.org/professional-certificates/devops-engineer', 'platform': 'Coursera'},
            {'name': 'Terraform - Getting Started', 'url': 'https://www.pluralsight.com/courses/terraform-getting-started', 'platform': 'Pluralsight'},
        ],
        'Backend Development': [
            {'name': 'Python Backend Development', 'url': 'https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp/', 'platform': 'Udemy'},
            {'name': 'Node.js Backend Mastery', 'url': 'https://www.udemy.com/course/nodejs-express-mongodb-bootcamp/', 'platform': 'Udemy'},
            {'name': 'REST API Design', 'url': 'https://www.udacity.com/course/designing-restful-apis--ud388', 'platform': 'Udacity'},
            {'name': 'Database Design Course', 'url': 'https://www.freecodecamp.org/news/database-design-course/', 'platform': 'freeCodeCamp'},
        ],
        'Frontend Development': [
            {'name': 'Advanced CSS and Sass', 'url': 'https://www.udemy.com/course/advanced-css-and-sass/', 'platform': 'Udemy'},
            {'name': 'JavaScript - The Complete Guide', 'url': 'https://www.udemy.com/course/javascript-the-complete-guide-2020-beginner-advanced/', 'platform': 'Udemy'},
            {'name': 'React Developer Nanodegree', 'url': 'https://www.udacity.com/course/react-nanodegree--nd019', 'platform': 'Udacity'},
            {'name': 'Frontend Web Developer', 'url': 'https://www.udacity.com/course/front-end-web-developer-nanodegree--nd0011', 'platform': 'Udacity'},
        ]
    }
    
    @classmethod
    def generate_job_recommendations(cls, user_id):
        """Generate job role recommendations based on resume and interview performance"""
        # Get latest resume
        resume = Resume.get_latest_by_user(user_id)
        if not resume:
            return None
        
        skills = [s.lower() for s in resume.skills]
        experience_years = resume.experience_years
        
        # Get interview performance
        interviews = MockInterview.get_completed_by_user(user_id, limit=10)
        avg_score = sum(i.score for i in interviews) / len(interviews) if interviews else 0
        
        # Calculate role scores
        role_scores = {}
        
        for role, required_skills in Config.JOB_ROLE_MAPPINGS.items():
            # Calculate skill match
            matched = sum(1 for skill in required_skills if skill.lower() in skills)
            skill_match = matched / len(required_skills) if required_skills else 0
            
            # Factor in experience
            exp_factor = min(experience_years / 5, 1)  # Max factor at 5 years
            
            # Factor in interview performance
            interview_factor = avg_score / 100 if avg_score else 0.5
            
            # Combined score
            score = (skill_match * 0.5) + (exp_factor * 0.25) + (interview_factor * 0.25)
            role_scores[role] = round(score * 100, 2)
        
        # Sort and get top roles
        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
        top_roles = [{'role': role, 'match_score': score} for role, score in sorted_roles[:5]]
        
        # Get recommended courses
        predicted_field = resume.predicted_field
        courses = cls.COURSES.get(predicted_field, cls.COURSES['Web Development'])[:3]
        
        # Get recommended skills
        recommended_skills = resume.recommended_skills[:8]
        
        rec_data = {
            'recommended_roles': top_roles,
            'recommended_courses': courses,
            'recommended_skills': recommended_skills,
            'based_on_resume': resume.id,
            'confidence_scores': role_scores
        }
        
        return Recommendation.update_or_create(user_id, rec_data)
    
    @classmethod
    def get_interview_type_recommendations(cls, user_id):
        """Recommend interview types based on resume and weak areas"""
        resume = Resume.get_latest_by_user(user_id)
        if not resume:
            return Config.INTERVIEW_TYPES[:4]
        
        skills = [s.lower() for s in resume.skills]
        predicted_field = resume.predicted_field
        
        # Map fields to interview types
        field_interviews = {
            'Data Science': ['Machine Learning', 'Python Programming', 'Database'],
            'Web Development': ['Web Development', 'JavaScript', 'System Design'],
            'Backend Development': ['Python Programming', 'Database', 'System Design'],
            'Frontend Development': ['JavaScript', 'Web Development'],
            'Mobile Development': ['Data Structures & Algorithms', 'System Design'],
            'DevOps': ['DevOps', 'System Design', 'Database']
        }
        
        recommended = field_interviews.get(predicted_field, Config.INTERVIEW_TYPES[:3])
        
        # Always include DSA
        if 'Data Structures & Algorithms' not in recommended:
            recommended.insert(0, 'Data Structures & Algorithms')
        
        return recommended[:4]