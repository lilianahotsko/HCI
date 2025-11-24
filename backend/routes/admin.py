"""
Admin routes for database management
"""
from flask import Blueprint, jsonify
from app import app
from database import db
from models import Task, Movie, Book

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@bp.route('/init-tasks', methods=['POST'])
def init_tasks():
    """Manually trigger task creation"""
    try:
        with app.app_context():
            from preprocess_data import create_movie_tasks, create_book_tasks
            
            before_count = Task.query.count()
            create_movie_tasks()
            create_book_tasks()
            after_count = Task.query.count()
            
            return jsonify({
                'success': True,
                'message': f'Created {after_count - before_count} tasks',
                'total_tasks': after_count
            }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        with app.app_context():
            return jsonify({
                'movies': Movie.query.count(),
                'books': Book.query.count(),
                'tasks': Task.query.count(),
                'tasks_by_interface': {
                    'faceted': Task.query.filter_by(interface_type='faceted').count(),
                    'llm_assist': Task.query.filter_by(interface_type='llm_assist').count(),
                    'llm_only': Task.query.filter_by(interface_type='llm_only').count()
                },
                'tasks_by_dataset': {
                    'movies': Task.query.filter_by(dataset_type='movies').count(),
                    'books': Task.query.filter_by(dataset_type='books').count()
                }
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

