"""
Logging routes: for logging various events
"""
from flask import Blueprint, request, jsonify
from database import db
from models import LogEntry
from datetime import datetime
import json

bp = Blueprint('logging', __name__, url_prefix='/api/log')

@bp.route('', methods=['POST'])
def log_event():
    """Generic event logging endpoint"""
    data = request.json
    participant_id = data.get('participant_id')
    interface_type = data.get('interface_type')
    task_id = data.get('task_id')
    event_type = data.get('event_type')
    payload = data.get('payload', {})
    
    if not participant_id or not event_type:
        return jsonify({'error': 'participant_id and event_type required'}), 400
    
    log_entry = LogEntry(
        participant_id=participant_id,
        interface_type=interface_type,
        task_id=task_id,
        event_type=event_type,
        payload=json.dumps(payload) if payload else None
    )
    
    db.session.add(log_entry)
    db.session.commit()
    
    return jsonify({'status': 'logged', 'log_id': log_entry.id}), 200

@bp.route('/task/start', methods=['POST'])
def start_task():
    """Log task start"""
    data = request.json
    participant_id = data.get('participant_id')
    task_id = data.get('task_id')
    interface_type = data.get('interface_type')
    
    return log_event_internal(participant_id, interface_type, task_id, 'task_started', {})

@bp.route('/task/end', methods=['POST'])
def end_task():
    """Log task end with submission"""
    data = request.json
    participant_id = data.get('participant_id')
    task_id = data.get('task_id')
    interface_type = data.get('interface_type')
    submission = data.get('submission', {})
    
    return log_event_internal(participant_id, interface_type, task_id, 'task_completed', submission)

def log_event_internal(participant_id, interface_type, task_id, event_type, payload):
    """Internal helper for logging"""
    log_entry = LogEntry(
        participant_id=participant_id,
        interface_type=interface_type,
        task_id=task_id,
        event_type=event_type,
        payload=json.dumps(payload) if payload else None
    )
    
    db.session.add(log_entry)
    db.session.commit()
    
    return jsonify({'status': 'logged', 'log_id': log_entry.id}), 200

