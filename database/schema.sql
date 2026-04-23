-- Create database
CREATE DATABASE IF NOT EXISTS adaptive_notes;
USE adaptive_notes;

-- Users table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lectures table
CREATE TABLE lectures (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    duration INT, -- in seconds
    language VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Transcriptions table
CREATE TABLE transcriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    lecture_id INT,
    full_text TEXT,
    word_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lecture_id) REFERENCES lectures(id) ON DELETE CASCADE
);

-- Notes table
CREATE TABLE notes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    lecture_id INT,
    level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    title VARCHAR(255),
    content JSON, -- Store structured notes as JSON
    summary TEXT,
    key_points JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lecture_id) REFERENCES lectures(id) ON DELETE CASCADE
);

-- Diagrams table
CREATE TABLE diagrams (
    id INT PRIMARY KEY AUTO_INCREMENT,
    lecture_id INT,
    image_path VARCHAR(500),
    caption VARCHAR(255),
    extracted_text TEXT,
    frame_number INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lecture_id) REFERENCES lectures(id) ON DELETE CASCADE
);

-- Quizzes table
CREATE TABLE quizzes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    lecture_id INT,
    level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    questions JSON, -- Store quiz questions as JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lecture_id) REFERENCES lectures(id) ON DELETE CASCADE
);

-- Quiz attempts table
CREATE TABLE quiz_attempts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    quiz_id INT,
    answers JSON,
    score FLOAT,
    weak_topics JSON,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

-- Performance tracking table
CREATE TABLE performance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    lecture_id INT,
    quiz_score FLOAT,
    time_spent INT, -- in seconds
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (lecture_id) REFERENCES lectures(id) ON DELETE CASCADE
);