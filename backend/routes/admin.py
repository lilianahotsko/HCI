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

@bp.route('/init-data', methods=['POST'])
def init_data():
    """Manually trigger data loading from CSV files"""
    try:
        with app.app_context():
            from preprocess_data import load_movies_from_csv, load_books_from_csv, create_movie_tasks, create_book_tasks
            import os
            
            results = {
                'movies_loaded': 0,
                'books_loaded': 0,
                'tasks_created': 0,
                'errors': []
            }
            
            # Load movies
            if Movie.query.count() == 0:
                csv_path = os.getenv('TMDB_CSV_PATH', 'tmdb_5000_movies.csv')
                if os.path.exists(csv_path):
                    load_movies_from_csv(csv_path)
                    results['movies_loaded'] = Movie.query.count()
                else:
                    results['errors'].append(f'Movies CSV not found at {csv_path}')
            
            # Load books
            if Book.query.count() == 0:
                books_csv_path = os.getenv('BOOKS_CSV_PATH', 'books.csv')
                if os.path.exists(books_csv_path):
                    load_books_from_csv(books_csv_path)
                    results['books_loaded'] = Book.query.count()
                else:
                    results['errors'].append(f'Books CSV not found at {books_csv_path}')
            
            # Create tasks
            before_tasks = Task.query.count()
            create_movie_tasks()
            create_book_tasks()
            results['tasks_created'] = Task.query.count() - before_tasks
            
            return jsonify({
                'success': True,
                **results,
                'total_movies': Movie.query.count(),
                'total_books': Book.query.count(),
                'total_tasks': Task.query.count()
            }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
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

