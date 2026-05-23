from app.models.feedback import Feedback
from app.services.question_service import QuestionService

class FeedbackService:
    
    @staticmethod
    def generate_feedback(user_id, interview_id, evaluation_results):
        """Generate AI-powered feedback based on interview results"""
        score = evaluation_results['score']
        results = evaluation_results['results']
        topic_scores = QuestionService.get_topic_breakdown(results)
        
        # Identify strong and weak topics
        strong_topics = []
        weak_topics = []
        
        for topic, data in topic_scores.items():
            if data['percentage'] >= 70:
                strong_topics.append(topic)
            elif data['percentage'] < 50:
                weak_topics.append(topic)
        
        # Generate feedback summary
        if score >= 80:
            summary = "Excellent performance! You demonstrated strong knowledge across most topics. "
        elif score >= 60:
            summary = "Good performance with room for improvement. You have a solid foundation but need to strengthen some areas. "
        elif score >= 40:
            summary = "Average performance. Focus on strengthening your weak areas through practice and study. "
        else:
            summary = "Needs improvement. We recommend revisiting the fundamentals and practicing more. "
        
        # Add specific observations
        if strong_topics:
            summary += f"You showed strength in: {', '.join(strong_topics)}. "
        if weak_topics:
            summary += f"Areas needing improvement: {', '.join(weak_topics)}. "
        
        # Generate improvement suggestions
        suggestions = FeedbackService.get_improvement_suggestions(weak_topics, score)
        
        feedback_data = {
            'feedback_summary': summary,
            'strong_topics': strong_topics,
            'weak_topics': weak_topics,
            'improvement_suggestions': suggestions,
            'score': score,
            'topic_scores': topic_scores
        }
        
        return Feedback.create(user_id, interview_id, feedback_data)
    
    @staticmethod
    def get_improvement_suggestions(weak_topics, score):
        """Generate improvement suggestions based on weak topics"""
        suggestions = []
        
        topic_suggestions = {
            'DSA': [
                "Practice daily coding problems on LeetCode or HackerRank",
                "Review fundamental data structures: Arrays, LinkedLists, Trees, Graphs",
                "Study common algorithms: Sorting, Searching, Dynamic Programming"
            ],
            'Python': [
                "Work through Python documentation and tutorials",
                "Practice with real-world projects",
                "Study Python best practices and design patterns"
            ],
            'JavaScript': [
                "Review ES6+ features and modern JavaScript",
                "Build interactive web applications",
                "Study async programming and promises"
            ],
            'Web Development': [
                "Build full-stack projects to gain practical experience",
                "Study HTTP, REST APIs, and web architecture",
                "Learn about security best practices"
            ],
            'Machine Learning': [
                "Complete online ML courses (Coursera, fast.ai)",
                "Implement algorithms from scratch for understanding",
                "Work on Kaggle competitions for practical experience"
            ],
            'System Design': [
                "Study system design fundamentals and patterns",
                "Read about real-world system architectures",
                "Practice designing scalable systems"
            ],
            'Database': [
                "Practice SQL queries and optimization",
                "Study database design principles",
                "Learn about different database types and use cases"
            ],
            'DevOps': [
                "Set up CI/CD pipelines for personal projects",
                "Learn container orchestration with Kubernetes",
                "Study cloud services (AWS, GCP, Azure)"
            ]
        }
        
        for topic in weak_topics:
            if topic in topic_suggestions:
                suggestions.extend(topic_suggestions[topic][:2])
        
        # Add general suggestions based on score
        if score < 50:
            suggestions.append("Consider taking structured online courses in your weak areas")
            suggestions.append("Form or join a study group for peer learning")
        
        return suggestions[:5]  # Return max 5 suggestions
    
    @staticmethod
    def get_user_weak_areas(user_id):
        """Analyze all user feedback to identify consistent weak areas"""
        feedbacks = Feedback.get_by_user(user_id, limit=10)
        
        if not feedbacks:
            return []
        
        topic_frequency = {}
        for feedback in feedbacks:
            for topic in feedback.weak_topics:
                topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
        
        # Sort by frequency and return topics that appear in multiple interviews
        sorted_topics = sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics if count >= 2]