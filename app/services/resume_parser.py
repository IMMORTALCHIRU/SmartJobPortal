import os
import re
from PyPDF2 import PdfReader
from docx import Document
from app.config import Config

class ResumeParserService:
    
    # Comprehensive skill keywords
    SKILL_KEYWORDS = {
        'programming_languages': [
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift',
            'kotlin', 'go', 'rust', 'scala', 'r', 'matlab', 'perl', 'typescript',
            'objective-c', 'shell', 'bash', 'powershell', 'sql', 'html', 'css'
        ],
        'frameworks': [
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
            'node.js', 'rails', 'laravel', 'asp.net', 'fastapi', 'next.js',
            'nuxt.js', 'gatsby', 'svelte', 'ember', 'backbone', 'jquery',
            'bootstrap', 'tailwind', 'material-ui', 'redux', 'mobx'
        ],
        'databases': [
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'cassandra', 'oracle', 'sql server', 'sqlite', 'dynamodb',
            'firebase', 'neo4j', 'mariadb', 'couchdb'
        ],
        'cloud_devops': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
            'ansible', 'puppet', 'chef', 'circleci', 'travis ci', 'gitlab ci',
            'github actions', 'prometheus', 'grafana', 'nginx', 'apache'
        ],
        'data_science_ml': [
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'matplotlib', 'seaborn', 'spark', 'hadoop', 'tableau', 'power bi',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'data analysis', 'statistics', 'data visualization'
        ],
        'tools': [
            'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence',
            'slack', 'trello', 'asana', 'figma', 'sketch', 'adobe xd',
            'postman', 'swagger', 'vs code', 'intellij', 'eclipse'
        ],
        'mobile': [
            'android', 'ios', 'flutter', 'react native', 'xamarin', 'ionic',
            'swift', 'kotlin', 'objective-c', 'swiftui', 'jetpack compose'
        ]
    }
    
    EDUCATION_KEYWORDS = [
        'bachelor', 'master', 'phd', 'doctorate', 'b.tech', 'm.tech', 'b.e', 'm.e',
        'b.sc', 'm.sc', 'bca', 'mca', 'bba', 'mba', 'b.com', 'm.com', 'diploma',
        'certification', 'degree', 'university', 'college', 'institute', 'school'
    ]
    
    CERTIFICATION_KEYWORDS = [
        'certified', 'certification', 'certificate', 'aws certified', 'google certified',
        'microsoft certified', 'oracle certified', 'cisco', 'pmp', 'scrum master',
        'comptia', 'itil', 'six sigma', 'azure', 'gcp', 'professional'
    ]
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF file"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text, len(reader.pages)
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return "", 0
    
    @staticmethod
    def extract_text_from_docx(file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            # Estimate page count
            page_count = max(1, len(text) // 3000)
            return text, page_count
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            return "", 0
    
    @classmethod
    def extract_skills(cls, text):
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = set()
        
        for category, skills in cls.SKILL_KEYWORDS.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    found_skills.add(skill.title())
        
        return list(found_skills)
    
    @classmethod
    def extract_education(cls, text):
        """Extract education information"""
        text_lower = text.lower()
        education = []
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for keyword in cls.EDUCATION_KEYWORDS:
                if keyword in line_lower:
                    # Get context (current line and next few lines)
                    context = ' '.join(lines[i:i+3]).strip()
                    if context and len(context) > 10:
                        education.append(context)
                    break
        
        return list(set(education))[:5]  # Return unique, max 5
    
    @classmethod
    def extract_certifications(cls, text):
        """Extract certifications"""
        text_lower = text.lower()
        certifications = []
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            for keyword in cls.CERTIFICATION_KEYWORDS:
                if keyword in line_lower:
                    if len(line.strip()) > 5:
                        certifications.append(line.strip())
                    break
        
        return list(set(certifications))[:10]
    
    @staticmethod
    def estimate_experience_years(text):
        """Estimate years of experience from resume"""
        # Look for explicit mentions of years of experience
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience\s*[:\-]?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*(?:in|of)\s*(?:software|development|programming)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        # Count job entries as fallback
        job_indicators = ['present', 'current', '2024', '2023', '2022', '2021', '2020']
        job_count = sum(1 for indicator in job_indicators if indicator in text.lower())
        
        return min(job_count * 2, 15)  # Estimate 2 years per job, max 15
    
    @staticmethod
    def calculate_resume_score(resume_data):
        """Calculate resume score based on content"""
        score = 0
        
        # Skills (max 30 points)
        skill_count = len(resume_data.get('skills', []))
        skill_points = min(skill_count * 3, 30)
        score += skill_points
        
        # Education (max 15 points)
        edu_points = 15 if resume_data.get('education') else 0
        score += edu_points
        
        # Certifications (max 15 points)
        cert_count = len(resume_data.get('certifications', []))
        cert_points = min(cert_count * 5, 15)
        score += cert_points
        
        # Experience (max 20 points)
        exp_years = resume_data.get('experience_years', 0)
        exp_points = min(exp_years * 2, 20)
        score += exp_points
        
        # Resume sections (max 20 points)
        section_points = 0
        if resume_data.get('has_objective'):
            section_points += 4
        if resume_data.get('has_projects'):
            section_points += 5
        if resume_data.get('has_achievements'):
            section_points += 4
        if resume_data.get('has_hobbies'):
            section_points += 3
        if resume_data.get('has_declaration'):
            section_points += 4
        score += section_points
        
        breakdown = {
            'skills': round((skill_points / 30) * 100),
            'education': round((edu_points / 15) * 100),
            'experience': round((exp_points / 20) * 100),
            'keywords': min(round(((skill_count + cert_count) / 15) * 100), 100)
        }
        
        return min(score, 100), breakdown
    
    @staticmethod
    def determine_candidate_level(page_count, experience_years):
        """Determine candidate level based on resume"""
        if experience_years >= 5 or page_count >= 3:
            return 'Experienced'
        elif experience_years >= 2 or page_count == 2:
            return 'Intermediate'
        else:
            return 'Fresher'
    
    @classmethod
    def predict_field(cls, skills):
        """Predict career field based on skills"""
        skills_lower = [s.lower() for s in skills]
        
        field_scores = {
            'Data Science': 0,
            'Web Development': 0,
            'Mobile Development': 0,
            'DevOps': 0,
            'Backend Development': 0,
            'Frontend Development': 0
        }
        
        for skill in skills_lower:
            if skill in ['tensorflow', 'pytorch', 'keras', 'pandas', 'numpy', 
                        'machine learning', 'deep learning', 'data analysis']:
                field_scores['Data Science'] += 2
            if skill in ['react', 'angular', 'vue', 'html', 'css', 'javascript']:
                field_scores['Frontend Development'] += 2
                field_scores['Web Development'] += 1
            if skill in ['django', 'flask', 'node.js', 'express', 'spring', 'java', 'python']:
                field_scores['Backend Development'] += 2
                field_scores['Web Development'] += 1
            if skill in ['android', 'ios', 'flutter', 'react native', 'kotlin', 'swift']:
                field_scores['Mobile Development'] += 2
            if skill in ['docker', 'kubernetes', 'aws', 'azure', 'jenkins', 'terraform']:
                field_scores['DevOps'] += 2
        
        return max(field_scores, key=field_scores.get)
    
    @classmethod
    def get_recommended_skills(cls, predicted_field, current_skills):
        """Get recommended skills based on predicted field"""
        skill_recommendations = {
            'Data Science': ['TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy',
                           'Matplotlib', 'SQL', 'Statistics', 'Deep Learning', 'NLP'],
            'Web Development': ['React', 'Node.js', 'TypeScript', 'MongoDB', 'REST APIs',
                              'GraphQL', 'Docker', 'AWS', 'Git', 'Testing'],
            'Frontend Development': ['React', 'TypeScript', 'CSS3', 'Tailwind', 'Redux',
                                   'Webpack', 'Testing', 'Accessibility', 'Performance'],
            'Backend Development': ['Python', 'Node.js', 'PostgreSQL', 'Redis', 'Docker',
                                  'REST APIs', 'GraphQL', 'Microservices', 'AWS'],
            'Mobile Development': ['Flutter', 'React Native', 'Swift', 'Kotlin', 'Firebase',
                                 'REST APIs', 'Git', 'CI/CD', 'Testing'],
            'DevOps': ['Kubernetes', 'Terraform', 'AWS', 'CI/CD', 'Prometheus',
                      'Grafana', 'Linux', 'Python', 'Ansible', 'Security']
        }
        
        recommended = skill_recommendations.get(predicted_field, [])
        current_lower = [s.lower() for s in current_skills]
        
        return [skill for skill in recommended if skill.lower() not in current_lower]
    
    @classmethod
    def check_resume_sections(cls, text):
        """Check for important resume sections"""
        text_lower = text.lower()
        
        return {
            'has_objective': any(word in text_lower for word in ['objective', 'career objective', 'summary', 'profile']),
            'has_projects': any(word in text_lower for word in ['project', 'projects', 'portfolio']),
            'has_achievements': any(word in text_lower for word in ['achievement', 'achievements', 'accomplishment', 'award']),
            'has_hobbies': any(word in text_lower for word in ['hobby', 'hobbies', 'interest', 'interests']),
            'has_declaration': any(word in text_lower for word in ['declaration', 'declare', 'hereby'])
        }
    
    @classmethod
    def parse_resume(cls, file_path, filename):
        """Main method to parse resume and extract all information"""
        # Determine file type and extract text
        ext = filename.rsplit('.', 1)[-1].lower()
        
        if ext == 'pdf':
            raw_text, page_count = cls.extract_text_from_pdf(file_path)
        elif ext == 'docx':
            raw_text, page_count = cls.extract_text_from_docx(file_path)
        else:
            return None
        
        if not raw_text:
            return None
        
        # Extract information
        skills = cls.extract_skills(raw_text)
        education = cls.extract_education(raw_text)
        certifications = cls.extract_certifications(raw_text)
        experience_years = cls.estimate_experience_years(raw_text)
        sections = cls.check_resume_sections(raw_text)
        predicted_field = cls.predict_field(skills)
        recommended_skills = cls.get_recommended_skills(predicted_field, skills)
        candidate_level = cls.determine_candidate_level(page_count, experience_years)
        
        resume_data = {
            'filename': filename,
            'raw_text': raw_text,
            'page_count': page_count,
            'skills': skills,
            'education': education,
            'certifications': certifications,
            'experience_years': experience_years,
            'predicted_field': predicted_field,
            'recommended_skills': recommended_skills,
            'candidate_level': candidate_level,
            'technical_keywords': skills,
            **sections
        }
        
        score, breakdown = cls.calculate_resume_score(resume_data)
        resume_data['resume_score'] = score
        resume_data['score_breakdown'] = breakdown
        
        return resume_data