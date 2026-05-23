from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime
from app import mongo

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.name = user_data.get('name')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.role = user_data.get('role', 'candidate')  # candidate, employer, admin
        self.preferred_roles = user_data.get('preferred_roles', [])
        self.date_joined = user_data.get('date_joined', datetime.utcnow())
        self.profile_summary = user_data.get('profile_summary', '')
        self.avatar_color = user_data.get('avatar_color', '#1e40af')
        self._is_active = user_data.get('is_active', True)
        self.phone = user_data.get('phone', '')
        self.location = user_data.get('location', '')
        # Employer-specific fields
        self.company_name = user_data.get('company_name', '')
        self.company_logo = user_data.get('company_logo', '')
        self.company_description = user_data.get('company_description', '')
        self.company_website = user_data.get('company_website', '')
        self.company_size = user_data.get('company_size', '')
        self.industry = user_data.get('industry', '')
        self.years_in_business = user_data.get('years_in_business', '')
        self.is_approved = user_data.get('is_approved', False)

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    def is_candidate(self):
        return self.role == 'candidate'

    def is_employer(self):
        return self.role == 'employer'

    def is_admin(self):
        return self.role == 'admin'

    @staticmethod
    def create(name, email, password, role='candidate', extra_data=None):
        password_hash = generate_password_hash(password)
        user_data = {
            'name': name,
            'email': email.lower(),
            'password_hash': password_hash,
            'role': role,
            'preferred_roles': [],
            'date_joined': datetime.utcnow(),
            'profile_summary': '',
            'avatar_color': f'#{abs(hash(email)) % 0xFFFFFF:06x}',
            'is_active': True,
            'phone': '',
            'location': '',
        }
        if role == 'employer':
            user_data['is_approved'] = False
            if extra_data:
                user_data.update(extra_data)
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)
    
    @staticmethod
    def get_by_email(email):
        user_data = mongo.db.users.find_one({'email': email.lower()})
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_by_id(user_id):
        try:
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            pass
        return None
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_profile(self, data):
        allowed_fields = [
            'name', 'preferred_roles', 'profile_summary', 'phone', 'location',
            'company_name', 'company_description', 'company_website', 'company_logo',
            'company_size', 'industry', 'years_in_business'
        ]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        if update_data:
            mongo.db.users.update_one(
                {'_id': ObjectId(self.id)},
                {'$set': update_data}
            )
            return True
        return False

    @staticmethod
    def get_all_by_role(role):
        users = mongo.db.users.find({'role': role}).sort('date_joined', -1)
        return [User(u) for u in users]

    @staticmethod
    def get_pending_employers():
        users = mongo.db.users.find({'role': 'employer', 'is_approved': False}).sort('date_joined', -1)
        return [User(u) for u in users]

    @staticmethod
    def approve_employer(user_id):
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'is_approved': True}}
        )

    @staticmethod
    def set_active(user_id, is_active):
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'is_active': is_active}}
        )

    @staticmethod
    def delete_user(user_id):
        mongo.db.users.delete_one({'_id': ObjectId(user_id)})

    def get_initials(self):
        names = self.name.split()
        if len(names) >= 2:
            return (names[0][0] + names[1][0]).upper()
        return self.name[0:2].upper()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'preferred_roles': self.preferred_roles,
            'date_joined': self.date_joined,
            'profile_summary': self.profile_summary,
            'avatar_color': self.avatar_color,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'company_name': self.company_name,
            'company_logo': self.company_logo,
        }