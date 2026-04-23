import random
import numpy as np
from sentence_transformers import SentenceTransformer, util

class QuizGenerator:
    def __init__(self):
        # Load sentence transformer for semantic similarity
        try:
            self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        except:
            self.similarity_model = None
            print("Sentence transformer not available")
    
    def generate_quiz(self, notes, level='beginner', num_questions=5):
        """Generate quiz based on notes"""
        quiz = []
        
        # Extract content from notes
        content = []
        for section in notes.get('sections', []):
            content.append(section.get('heading', ''))
            content.extend(section.get('bullets', []))
        
        content.extend(notes.get('key_points', []))
        
        # Generate questions from content
        for i, item in enumerate(content[:num_questions]):
            if len(item) < 10:  # Skip too short items
                continue
            
            question = self._create_mcq(item, level)
            if question:
                quiz.append(question)
        
        # If not enough questions, add some default ones
        while len(quiz) < num_questions:
            quiz.append(self._default_question(len(quiz) + 1))
        
        return quiz[:num_questions]
    
    def _create_mcq(self, text, level):
        """Create MCQ from text snippet"""
        # Clean text
        text = text.replace('•', '').strip()
        
        if not text or len(text) < 10:
            return None
        
        # Create question
        if text.startswith('Section'):
            # Use as heading
            question_text = f"Which topic is discussed in this section?"
            correct = text
            distractors = [
                "Neural Networks",
                "Machine Learning Basics",
                "Deep Learning",
                "AI Fundamentals"
            ]
        else:
            # Use text as answer
            question_text = f"What is described by: '{text[:50]}...'?"
            correct = text[:30] + '...' if len(text) > 30 else text
            distractors = self._generate_distractors(text)
        
        # Shuffle options
        options = [correct] + distractors[:3]
        random.shuffle(options)
        
        return {
            'id': random.randint(1000, 9999),
            'question': question_text,
            'options': options,
            'correct': correct,
            'level': level
        }
    
    def _generate_distractors(self, text):
        """Generate distractor options"""
        # Common distractors based on topic
        if 'neural' in text.lower():
            return [
                "Computer Processing Unit",
                "Digital Circuit",
                "Data Storage System"
            ]
        elif 'learning' in text.lower():
            return [
                "Random Guessing",
                "Static Programming",
                "Rule-based System"
            ]
        else:
            return [
                "Alternative Concept A",
                "Alternative Concept B",
                "Alternative Concept C"
            ]
    
    def _default_question(self, q_num):
        """Generate default question"""
        questions = [
            {
                'id': 1001,
                'question': "What is the main function of a neural network?",
                'options': [
                    "Pattern recognition and learning",
                    "Data storage",
                    "Mathematical calculations only",
                    "Text editing"
                ],
                'correct': "Pattern recognition and learning",
                'level': 'beginner'
            },
            {
                'id': 1002,
                'question': "What is backpropagation?",
                'options': [
                    "A learning algorithm for neural networks",
                    "A data storage method",
                    "A type of computer virus",
                    "A programming language"
                ],
                'correct': "A learning algorithm for neural networks",
                'level': 'intermediate'
            },
            {
                'id': 1003,
                'question': "What are dendrites in a neuron?",
                'options': [
                    "Input receivers",
                    "Output transmitters",
                    "Storage units",
                    "Processing units"
                ],
                'correct': "Input receivers",
                'level': 'beginner'
            }
        ]
        
        return questions[(q_num - 1) % len(questions)]
    
    def evaluate_answers(self, quiz, user_answers):
        """Evaluate user answers with semantic similarity"""
        results = []
        
        for i, question in enumerate(quiz):
            if i >= len(user_answers):
                break
            
            user_answer = user_answers[i]
            correct_answer = question['correct']
            
            # Check exact match
            if user_answer == correct_answer:
                is_correct = True
                confidence = 1.0
            elif self.similarity_model:
                # Check semantic similarity
                embeddings = self.similarity_model.encode([user_answer, correct_answer])
                similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
                is_correct = similarity > 0.7
                confidence = similarity
            else:
                # Fallback to simple matching
                is_correct = user_answer.lower() in correct_answer.lower() or correct_answer.lower() in user_answer.lower()
                confidence = 0.5 if is_correct else 0.0
            
            results.append({
                'question_id': question.get('id', i),
                'question': question['question'],
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'correct': is_correct,
                'confidence': confidence
            })
        
        return results
    
    def detect_gaps(self, evaluation_results):
        """Detect knowledge gaps from evaluation"""
        weak_topics = []
        
        for result in evaluation_results:
            if not result['correct']:
                # Extract topic from question
                question = result['question']
                words = question.split()
                
                # Find key nouns
                for word in words:
                    if len(word) > 4 and word[0].isupper():
                        weak_topics.append(word)
                        break
        
        # Return unique weak topics
        return list(set(weak_topics))[:3]