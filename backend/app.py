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

# Log database URL (without password for security)
if database_url.startswith('postgresql://'):
    # Mask password in logs
    import re
    masked_url = re.sub(r':([^:@]+)@', ':****@', database_url)
    print(f"Connecting to PostgreSQL database: {masked_url}")
else:
    print(f"Using SQLite database: {database_url}")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connection pool settings for PostgreSQL
if database_url.startswith('postgresql://'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 300,    # Recycle connections after 5 minutes
        'connect_args': {
            'connect_timeout': 10,  # 10 second timeout
            'sslmode': 'require'    # Require SSL for Render PostgreSQL
        }
    }

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
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
    except Exception as e:
        print(f"Warning: Could not inspect database: {e}")
        return  # Database not ready yet
    
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

# Initialize database schema (lazy - only when app context is available)
def init_database():
    """Initialize database schema - called on first request"""
    try:
        with app.app_context():
            # Test database connection first
            db.engine.connect()
            print("✓ Database connection successful")
            
            # Create tables
            db.create_all()
            print("✓ Database tables created/verified")
            
            # Ensure schema columns
            ensure_schema_columns()
            print("✓ Database schema verified")
            
            # Load data if database is empty
            from models import Task, Movie, Book
            movie_count = Movie.query.count()
            book_count = Book.query.count()
            
            if movie_count == 0 or book_count == 0:
                print("Loading data from CSV files...")
                try:
                    from preprocess_data import load_movies_from_csv, load_books_from_csv
                    import os
                    
                    if movie_count == 0:
                        csv_path = os.getenv('TMDB_CSV_PATH', 'tmdb_5000_movies.csv')
                        if os.path.exists(csv_path):
                            load_movies_from_csv(csv_path)
                            print(f"✓ Loaded {Movie.query.count()} movies")
                        else:
                            print(f"⚠️  Movies CSV not found at {csv_path}")
                    
                    if book_count == 0:
                        books_csv_path = os.getenv('BOOKS_CSV_PATH', 'books.csv')
                        if os.path.exists(books_csv_path):
                            load_books_from_csv(books_csv_path)
                            print(f"✓ Loaded {Book.query.count()} books")
                        else:
                            print(f"⚠️  Books CSV not found at {books_csv_path}")
                except Exception as e:
                    print(f"⚠️  Could not load data: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"✓ Data already loaded ({movie_count} movies, {book_count} books)")
            
            # Create tasks if they don't exist
            task_count = Task.query.count()
            if task_count == 0:
                print("Creating tasks...")
                try:
                    from preprocess_data import create_movie_tasks, create_book_tasks
                    create_movie_tasks()
                    create_book_tasks()
                    print(f"✓ Created tasks (total: {Task.query.count()})")
                except Exception as e:
                    print(f"⚠️  Could not create tasks: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"✓ Tasks already exist ({task_count} tasks)")
    except Exception as e:
        print(f"⚠️  Database initialization error: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail startup - database might not be ready yet

# Try to initialize database at startup, but don't fail if it's not ready
try:
    init_database()
except Exception as e:
    print(f"Warning: Could not initialize database at startup: {e}")
    print("Database will be initialized on first request")

# Import and register routes
def register_routes():
    try:
        from routes import experiment, search, logging_routes, questionnaire, results, admin
        app.register_blueprint(experiment.bp)
        app.register_blueprint(search.bp)
        app.register_blueprint(logging_routes.bp)
        app.register_blueprint(questionnaire.bp)
        app.register_blueprint(results.bp)
        app.register_blueprint(admin.bp)
    except Exception as e:
        print(f"Error registering routes: {e}")
        import traceback
        traceback.print_exc()
        # Register basic routes even if some routes fail
        try:
            from routes import experiment, search, logging_routes, questionnaire, admin
            app.register_blueprint(experiment.bp)
            app.register_blueprint(search.bp)
            app.register_blueprint(logging_routes.bp)
            app.register_blueprint(questionnaire.bp)
            app.register_blueprint(admin.bp)
        except:
            pass

register_routes()

# Track if database has been initialized
_db_initialized = False

# Ensure database is initialized before handling requests (Flask 2.x+ compatible)
@app.before_request
def ensure_db_initialized():
    """Ensure database is initialized before requests"""
    global _db_initialized
    if not _db_initialized:
        try:
            # Check if tables exist, if not initialize
            with app.app_context():
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                if not tables:
                    init_database()
                _db_initialized = True
        except Exception as e:
            # Database might not be ready yet, that's okay
            # Will retry on next request
            pass

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running'}), 200

@app.route('/api/test', methods=['GET', 'POST'])
def test():
    """Test endpoint to verify backend is accessible"""
    return {'status': 'ok', 'method': request.method, 'data': request.json if request.is_json else None}, 200

@app.route('/api/routes', methods=['GET'])
def list_routes():
    """List all registered routes for debugging"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return jsonify({'routes': routes}), 200

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

