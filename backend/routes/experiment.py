"""
Experiment control routes: participant management, consent, experiment plan
"""
from flask import Blueprint, request, jsonify
from database import db
from models import Participant
from experiment_controller import get_experiment_plan, record_consent, get_or_create_participant
from data_access import get_all_genres

bp = Blueprint('experiment', __name__, url_prefix='/api/experiment')

@bp.route('/participant', methods=['POST'])
def create_participant():
    """Create or get participant"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        participant_id = data.get('participant_id')
        
        if not participant_id:
            return jsonify({'error': 'participant_id required'}), 400
        
        participant = get_or_create_participant(participant_id)
        return jsonify(participant.to_dict()), 200
    except Exception as e:
        print(f"Error creating participant: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to create participant: {str(e)}'}), 500

@bp.route('/consent', methods=['POST'])
def give_consent():
    """Record participant consent"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        participant_id = data.get('participant_id')
        
        if not participant_id:
            return jsonify({'error': 'participant_id required'}), 400
        
        participant = record_consent(participant_id)
        return jsonify(participant.to_dict()), 200
    except Exception as e:
        print(f"Error recording consent: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to record consent: {str(e)}'}), 500

VALID_DATASETS = {'movies', 'books'}

def normalize_dataset_type(value):
    return value if value in VALID_DATASETS else 'movies'

@bp.route('/plan', methods=['GET'])
def get_plan():
    """Get experiment plan for a participant"""
    participant_id = request.args.get('participant_id')
    dataset_type = normalize_dataset_type(request.args.get('dataset_type', 'movies'))
    
    if not participant_id:
        return jsonify({'error': 'participant_id required'}), 400
    
    plan = get_experiment_plan(participant_id, dataset_type)
    return jsonify(plan), 200

@bp.route('/genres', methods=['GET'])
def get_genres():
    """Get all available genres"""
    dataset_type = normalize_dataset_type(request.args.get('dataset_type', 'movies'))
    genres = get_all_genres(dataset_type)
    facet_label = 'Genres' if dataset_type == 'movies' else 'Languages'
    facet_field = 'genres' if dataset_type == 'movies' else 'languages'
    return jsonify({
        'dataset_type': dataset_type,
        'facet_label': facet_label,
        'facet_field': facet_field,
        'values': genres,
        'genres': genres
    }), 200

