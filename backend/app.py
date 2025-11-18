from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///hci_experiment.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize database
from database import db
db.init_app(app)

# Configure CORS - allow all origins for development
CORS(app, supports_credentials=True)

# Import models after db is initialized
from models import Movie, Participant, Task, LogEntry, QuestionnaireResponse

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
    app.run(host='0.0.0.0', port=5001, debug=True)

