from app.models.question import Question
from app import mongo

class QuestionService:
    
    @staticmethod
    def get_questions_for_interview(interview_type, skills=None, difficulty='medium', count=10):
        """Get questions for a mock interview"""
        # Map interview type to question category with fallbacks for all job fields
        category_mapping = {
            'Data Structures & Algorithms': 'DSA',
            'DSA': 'DSA',
            'Web Development': 'Web Development',
            'Machine Learning': 'Machine Learning',
            'System Design': 'System Design',
            'Database': 'Database',
            'Python Programming': 'Python',
            'Python': 'Python',
            'JavaScript': 'JavaScript',
            'JS': 'JavaScript',
            'DevOps': 'DevOps',
            'Technology': 'Python',  # Default for generic Technology field
            'Finance': 'System Design',
            'Healthcare': 'Database',
            'Marketing': 'Web Development',
            'Design': 'Web Development',
            'Operations': 'System Design',
            'Developer': 'Python'  # Common job title
        }
        
        category = category_mapping.get(interview_type, 'Python')  # Default to Python
        
        # Try to get questions by category at requested difficulty
        questions = []
        try:
            questions = Question.get_by_category(category, difficulty, count)
        except Exception:
            pass
        
        # If not enough questions, search by tags (skills)
        if len(questions) < count and skills:
            try:
                additional = Question.get_by_tags(skills, difficulty, count - len(questions))
                questions.extend(additional)
            except Exception:
                pass
        
        # If still not enough, try to get questions from any difficulty level
        if len(questions) < count:
            try:
                from app import mongo
                remaining = count - len(questions)
                # Try to get more questions without difficulty restriction
                all_questions = list(mongo.db.questions.aggregate([
                    {'$match': {}},
                    {'$sample': {'size': min(remaining, 100)}}
                ]))
                questions.extend([Question(q) for q in all_questions])
            except Exception:
                pass
        
        return questions[:count]
    
    @staticmethod
    def evaluate_answers(questions, user_answers):
        """Evaluate user answers and return score"""
        correct = 0
        results = []
        
        for question in questions:
            question_id = question.id
            user_answer = user_answers.get(question_id, '')
            is_correct = user_answer.strip().lower() == question.correct_answer.strip().lower()
            
            if is_correct:
                correct += 1
            
            results.append({
                'question_id': question_id,
                'question_text': question.question_text,
                'user_answer': user_answer,
                'correct_answer': question.correct_answer,
                'is_correct': is_correct,
                'explanation': question.explanation,
                'category': question.category
            })
        
        total = len(questions)
        score = (correct / total * 100) if total > 0 else 0
        
        return {
            'score': round(score, 2),
            'correct': correct,
            'total': total,
            'results': results
        }
    
    @staticmethod
    def get_topic_breakdown(results):
        """Get score breakdown by topic"""
        topic_scores = {}
        
        for result in results:
            category = result.get('category', 'General')
            if category not in topic_scores:
                topic_scores[category] = {'correct': 0, 'total': 0}
            
            topic_scores[category]['total'] += 1
            if result['is_correct']:
                topic_scores[category]['correct'] += 1
        
        # Calculate percentages
        for topic in topic_scores:
            total = topic_scores[topic]['total']
            correct = topic_scores[topic]['correct']
            topic_scores[topic]['percentage'] = round(correct / total * 100, 2) if total > 0 else 0
        
        return topic_scores