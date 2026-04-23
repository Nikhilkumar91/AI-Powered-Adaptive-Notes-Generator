# database.py - Database configuration and connection

import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                database='adaptive_notes',
                user='root',
                password=''  # Change this to your MySQL password
            )
            if self.connection.is_connected():
                logger.info("✅ Connected to MySQL database")
                return True
        except Error as e:
            logger.error(f"❌ Database connection error: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """Execute a query and return cursor"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor
        except Error as e:
            logger.error(f"Query error: {e}")
            return None
    
    # ========== USER METHODS ==========
    def create_user(self, username, email, password_hash):
        """Create a new user"""
        query = """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """
        cursor = self.execute_query(query, (username, email, password_hash))
        if cursor:
            return cursor.lastrowid
        return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %s"
        cursor = self.execute_query(query, (email,))
        if cursor:
            return cursor.fetchone()
        return None
    
    # ========== LECTURE METHODS ==========
    def save_lecture(self, user_id, filename, file_path, file_size, duration=None):
        """Save lecture information to database"""
        query = """
            INSERT INTO lectures (user_id, filename, file_path, file_size, duration)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor = self.execute_query(query, (user_id, filename, file_path, file_size, duration))
        if cursor:
            lecture_id = cursor.lastrowid
            logger.info(f"✅ Lecture saved with ID: {lecture_id}")
            return lecture_id
        return None
    
    def get_lecture(self, lecture_id):
        """Get lecture by ID"""
        query = "SELECT * FROM lectures WHERE id = %s"
        cursor = self.execute_query(query, (lecture_id,))
        if cursor:
            return cursor.fetchone()
        return None
    
    def get_user_lectures(self, user_id, limit=10):
        """Get recent lectures for a user"""
        query = """
            SELECT * FROM lectures 
            WHERE user_id = %s 
            ORDER BY uploaded_at DESC 
            LIMIT %s
        """
        cursor = self.execute_query(query, (user_id, limit))
        if cursor:
            return cursor.fetchall()
        return []
    
    # ========== TRANSCRIPTION METHODS ==========
    def save_transcription(self, lecture_id, full_text, word_count=None):
        """Save transcribed text to database"""
        if word_count is None:
            word_count = len(full_text.split())
        
        query = """
            INSERT INTO transcriptions (lecture_id, full_text, word_count)
            VALUES (%s, %s, %s)
        """
        cursor = self.execute_query(query, (lecture_id, full_text, word_count))
        if cursor:
            logger.info(f"✅ Transcription saved for lecture {lecture_id}")
            return cursor.lastrowid
        return None
    
    def get_transcription(self, lecture_id):
        """Get transcription for a lecture"""
        query = """
            SELECT full_text, word_count, created_at 
            FROM transcriptions 
            WHERE lecture_id = %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        cursor = self.execute_query(query, (lecture_id,))
        if cursor:
            return cursor.fetchone()
        return None
    
    # ========== NOTES METHODS ==========
    def save_notes(self, lecture_id, level, title, summary, key_points, detailed_notes):
        """Save generated notes to database"""
        query = """
            INSERT INTO notes (lecture_id, level, title, summary, key_points, content)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        # Convert to JSON strings
        key_points_json = json.dumps(key_points)
        detailed_notes_json = json.dumps(detailed_notes)
        
        cursor = self.execute_query(query, (lecture_id, level, title, summary, key_points_json, detailed_notes_json))
        if cursor:
            logger.info(f"✅ Notes saved for lecture {lecture_id} at {level} level")
            return cursor.lastrowid
        return None
    
    def get_notes(self, lecture_id, level):
        """Get notes for a lecture at specific level"""
        query = """
            SELECT title, summary, key_points, content, created_at
            FROM notes 
            WHERE lecture_id = %s AND level = %s
            ORDER BY created_at DESC 
            LIMIT 1
        """
        cursor = self.execute_query(query, (lecture_id, level))
        if cursor:
            result = cursor.fetchone()
            if result:
                # Parse JSON fields
                result['key_points'] = json.loads(result['key_points']) if result['key_points'] else []
                result['content'] = json.loads(result['content']) if result['content'] else {}
                return result
        return None
    
    # ========== DIAGRAM METHODS ==========
    def save_diagram(self, lecture_id, image_path, caption, extracted_text, frame_number):
        """Save extracted diagram to database"""
        query = """
            INSERT INTO diagrams (lecture_id, image_path, caption, extracted_text, frame_number)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor = self.execute_query(query, (lecture_id, image_path, caption, extracted_text, frame_number))
        if cursor:
            logger.info(f"✅ Diagram saved for lecture {lecture_id}")
            return cursor.lastrowid
        return None
    
    def get_diagrams(self, lecture_id, limit=10):
        """Get diagrams for a lecture"""
        query = """
            SELECT image_path, caption, extracted_text, frame_number
            FROM diagrams 
            WHERE lecture_id = %s 
            ORDER BY frame_number ASC 
            LIMIT %s
        """
        cursor = self.execute_query(query, (lecture_id, limit))
        if cursor:
            return cursor.fetchall()
        return []
    
    # ========== QUIZ METHODS ==========
    def save_quiz(self, lecture_id, level, questions):
        """Save generated quiz to database"""
        query = """
            INSERT INTO quizzes (lecture_id, level, questions)
            VALUES (%s, %s, %s)
        """
        questions_json = json.dumps(questions)
        cursor = self.execute_query(query, (lecture_id, level, questions_json))
        if cursor:
            logger.info(f"✅ Quiz saved for lecture {lecture_id} at {level} level")
            return cursor.lastrowid
        return None
    
    def get_quiz(self, lecture_id, level):
        """Get quiz for a lecture at specific level"""
        query = """
            SELECT id, questions, created_at
            FROM quizzes 
            WHERE lecture_id = %s AND level = %s
            ORDER BY created_at DESC 
            LIMIT 1
        """
        cursor = self.execute_query(query, (lecture_id, level))
        if cursor:
            result = cursor.fetchone()
            if result:
                result['questions'] = json.loads(result['questions']) if result['questions'] else []
                return result
        return None
    
    def save_quiz_attempt(self, user_id, quiz_id, answers, score, weak_topics):
        """Save user's quiz attempt"""
        query = """
            INSERT INTO quiz_attempts (user_id, quiz_id, answers, score, weak_topics)
            VALUES (%s, %s, %s, %s, %s)
        """
        answers_json = json.dumps(answers)
        weak_topics_json = json.dumps(weak_topics)
        cursor = self.execute_query(query, (user_id, quiz_id, answers_json, score, weak_topics_json))
        if cursor:
            logger.info(f"✅ Quiz attempt saved for user {user_id}")
            return cursor.lastrowid
        return None
    
    # ========== PERFORMANCE METHODS ==========
    def save_performance(self, user_id, lecture_id, quiz_score, time_spent):
        """Save user performance data"""
        query = """
            INSERT INTO performance (user_id, lecture_id, quiz_score, time_spent)
            VALUES (%s, %s, %s, %s)
        """
        cursor = self.execute_query(query, (user_id, lecture_id, quiz_score, time_spent))
        if cursor:
            logger.info(f"✅ Performance saved for user {user_id}")
            return cursor.lastrowid
        return None
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")

# Create a global database instance
db = Database()