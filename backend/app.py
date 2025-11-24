from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import inspect, text
import os

load_dotenv()

app = Flask(__name__)

# Database configuration - support both SQLite (local) and PostgreSQL (production)
database_url = os.getenv('DATABASE_URL', 'sqlite:///hci_experiment.db')
# Render/Railway provide PostgreSQL URLs that start with postgres://, convert to postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize database
from database import db
db.init_app(app)

# Configure CORS
# In production, restrict to your frontend domain
# In development, allow all origins
frontend_url = os.getenv('FRONTEND_URL', '*')
if frontend_url == '*':
    CORS(app, supports_credentials=True)  # Development: allow all
else:
    CORS(app, origins=[frontend_url], supports_credentials=True)  # Production: specific domain

# Import models after db is initialized
from models import Movie, Book, Participant, Task, LogEntry, QuestionnaireResponse

def ensure_schema_columns():
    """Lightweight schema migrations for new columns/tables."""
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    # Ensure books table exists with expected columns
    def add_column_if_missing(table_name, column_name, column_type_sql, existing_cols=None):
        cols = existing_cols or {col['name'] for col in inspector.get_columns(table_name)}
        if column_name not in cols:
            with db.engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type_sql}"))
            if existing_cols is not None:
                existing_cols.add(column_name)
    
    book_columns_sql = {
        'goodreads_id': 'INTEGER',
        'title': 'VARCHAR(500)',
        'authors': 'VARCHAR(500)',
        'average_rating': 'FLOAT',
        'isbn': 'VARCHAR(50)',
        'isbn13': 'VARCHAR(50)',
        'language': 'VARCHAR(50)',
        'num_pages': 'INTEGER',
        'ratings_count': 'INTEGER',
        'text_reviews_count': 'INTEGER',
        'publication_year': 'INTEGER',
        'publisher': 'VARCHAR(255)'
    }
    
    if 'books' not in tables:
        Book.__table__.create(bind=db.engine, checkfirst=True)
        tables.append('books')
    else:
        # Ensure legacy tables gain any missing columns
        existing_cols = {col['name'] for col in inspector.get_columns('books')}
        for col_name, col_type in book_columns_sql.items():
            add_column_if_missing('books', col_name, col_type)
    
    if 'tasks' in tables:
        task_columns = {col['name'] for col in inspector.get_columns('tasks')}
        if 'dataset_type' not in task_columns:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN dataset_type VARCHAR(50) DEFAULT 'movies'"))
    
    if 'participants' in tables:
        participant_columns = {col['name'] for col in inspector.get_columns('participants')}
        if 'task_order' not in participant_columns:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE participants ADD COLUMN task_order TEXT"))
        if 'counterbalancing_condition' not in participant_columns:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE participants ADD COLUMN counterbalancing_condition INTEGER"))
    
    if 'tasks' in tables:
        task_columns = {col['name'] for col in inspector.get_columns('tasks')}
        if 'task_set' not in task_columns:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN task_set VARCHAR(10) DEFAULT 'A'"))

with app.app_context():
    db.create_all()
    ensure_schema_columns()

# Import and register routes
def register_routes():
    from routes import experiment, search, logging_routes, questionnaire
    app.register_blueprint(experiment.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(logging_routes.bp)
    app.register_blueprint(questionnaire.bp)

register_routes()

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running'}), 200

@app.route('/api/test', methods=['GET', 'POST'])
def test():
    """Test endpoint to verify backend is accessible"""
    return {'status': 'ok', 'method': request.method, 'data': request.json if request.is_json else None}, 200

# Handle OPTIONS requests for CORS preflight
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = response.headers
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Run on all interfaces (0.0.0.0) to allow access from frontend proxy
    # Using port 5001 because macOS AirPlay Receiver uses port 5000
    # In production, port comes from PORT environment variable
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False for production

