from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import hashlib

db = SQLAlchemy()

# ========== USER MODEL (Login System) ==========
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()


# ========== LECTURE HISTORY TABLE ==========
class LectureHistory(db.Model):
    __tablename__ = 'lecture_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(200))
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    notes = db.relationship('SavedNotes', backref='lecture', lazy=True, cascade='all, delete-orphan')
    quizzes = db.relationship('SavedQuiz', backref='lecture', lazy=True, cascade='all, delete-orphan')


# ========== SAVED NOTES TABLE ==========
class SavedNotes(db.Model):
    __tablename__ = 'saved_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture_history.id'))
    level = db.Column(db.String(20))  # beginner, intermediate, advanced
    title = db.Column(db.String(200))
    summary = db.Column(db.Text)
    key_points = db.Column(db.Text)  # JSON format
    detailed_notes = db.Column(db.Text)  # JSON format
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ========== SAVED QUIZ RESULTS ==========
class SavedQuiz(db.Model):
    __tablename__ = 'saved_quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture_history.id'))
    level = db.Column(db.String(20))
    questions = db.Column(db.Text)  # JSON format
    user_answers = db.Column(db.Text)  # JSON format
    score = db.Column(db.Float)
    weak_topics = db.Column(db.Text)  # JSON format
    created_at = db.Column(db.DateTime, default=datetime.utcnow)