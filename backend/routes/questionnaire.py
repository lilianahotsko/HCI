"""
Questionnaire routes: SUS, NASA-TLX, trust, preference
"""
from flask import Blueprint, request, jsonify
from database import db
from models import QuestionnaireResponse
from datetime import datetime
import json

bp = Blueprint('questionnaire', __name__, url_prefix='/api/questionnaire')

@bp.route('', methods=['POST'])
def submit_questionnaire():
    """Submit questionnaire responses"""
    data = request.json
    participant_id = data.get('participant_id')
    interface_type = data.get('interface_type')
    questionnaire_type = data.get('questionnaire_type')
    responses = data.get('responses', {})
    
    if not participant_id or not questionnaire_type:
        return jsonify({'error': 'participant_id and questionnaire_type required'}), 400
    
    questionnaire = QuestionnaireResponse(
        participant_id=participant_id,
        interface_type=interface_type,
        questionnaire_type=questionnaire_type,
        responses=json.dumps(responses)
    )
    
    db.session.add(questionnaire)
    db.session.commit()
    
    return jsonify({'status': 'submitted', 'questionnaire_id': questionnaire.id}), 200

