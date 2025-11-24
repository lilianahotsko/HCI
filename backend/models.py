from database import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
import json

class Movie(db.Model):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    release_year = Column(Integer)
    runtime = Column(Integer)  # in minutes
    genres = Column(Text)  # JSON array stored as text
    lead_gender = Column(String(50))  # 'female', 'male', 'mixed', 'unknown'
    budget = Column(Float)
    revenue = Column(Float)
    language = Column(String(100))
    overview = Column(Text)
    tmdb_id = Column(Integer, unique=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_year': self.release_year,
            'runtime': self.runtime,
            'genres': json.loads(self.genres) if self.genres else [],
            'lead_gender': self.lead_gender,
            'budget': self.budget,
            'revenue': self.revenue,
            'language': self.language,
            'overview': self.overview
        }

class Book(db.Model):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    goodreads_id = Column(Integer, unique=True)
    title = Column(String(500), nullable=False)
    authors = Column(String(500))
    average_rating = Column(Float)
    isbn = Column(String(50))
    isbn13 = Column(String(50))
    language = Column(String(50))
    num_pages = Column(Integer)
    ratings_count = Column(Integer)
    text_reviews_count = Column(Integer)
    publication_year = Column(Integer)
    publisher = Column(String(255))
    
    def to_dict(self):
        return {
            'id': self.id,
            'goodreads_id': self.goodreads_id,
            'title': self.title,
            'authors': [a.strip() for a in self.authors.split('/') if a.strip()] if self.authors else [],
            'average_rating': self.average_rating,
            'isbn': self.isbn,
            'isbn13': self.isbn13,
            'language': self.language,
            'num_pages': self.num_pages,
            'ratings_count': self.ratings_count,
            'text_reviews_count': self.text_reviews_count,
            'publication_year': self.publication_year,
            'publisher': self.publisher
        }

class Participant(db.Model):
    __tablename__ = 'participants'
    
    id = Column(Integer, primary_key=True)
    participant_id = Column(String(100), unique=True, nullable=False)
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime)
    interface_order = Column(Text)  # JSON array: ["faceted", "llm_assist", "llm_only"]
    task_order = Column(Text)  # JSON object: {"faceted": ["T01", "B01", ...], "llm_assist": [...], ...}
    counterbalancing_condition = Column(Integer)  # Condition number for systematic assignment (0-5 for interface, 0-7 for task)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'consent_given': self.consent_given,
            'consent_timestamp': self.consent_timestamp.isoformat() if self.consent_timestamp else None,
            'interface_order': json.loads(self.interface_order) if self.interface_order else [],
            'task_order': json.loads(self.task_order) if self.task_order else {},
            'counterbalancing_condition': self.counterbalancing_condition,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    complexity = Column(String(20))  # 'simple' or 'complex'
    ground_truth = Column(Text)  # JSON array of movie IDs or description
    interface_type = Column(String(50))  # 'faceted', 'llm_assist', 'llm_only'
    dataset_type = Column(String(50), nullable=False, default='movies')
    task_set = Column(String(10), default='A')  # 'A', 'B', or 'C' - for unique task assignment
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'description': self.description,
            'complexity': self.complexity,
            'ground_truth': json.loads(self.ground_truth) if self.ground_truth else [],
            'interface_type': self.interface_type,
            'dataset_type': self.dataset_type or 'movies',
            'task_set': self.task_set or 'A'
        }

class LogEntry(db.Model):
    __tablename__ = 'log_entries'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    participant_id = Column(String(100), nullable=False)
    interface_type = Column(String(50))
    task_id = Column(String(50))
    event_type = Column(String(100), nullable=False)  # 'page_load', 'task_started', 'filter_change', etc.
    payload = Column(Text)  # JSON string
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'participant_id': self.participant_id,
            'interface_type': self.interface_type,
            'task_id': self.task_id,
            'event_type': self.event_type,
            'payload': json.loads(self.payload) if self.payload else {}
        }

class QuestionnaireResponse(db.Model):
    __tablename__ = 'questionnaire_responses'
    
    id = Column(Integer, primary_key=True)
    participant_id = Column(String(100), nullable=False)
    interface_type = Column(String(50))
    questionnaire_type = Column(String(50), nullable=False)  # 'SUS', 'NASA_TLX', 'trust', 'preference'
    responses = Column(Text, nullable=False)  # JSON object
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'interface_type': self.interface_type,
            'questionnaire_type': self.questionnaire_type,
            'responses': json.loads(self.responses) if self.responses else {},
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }

