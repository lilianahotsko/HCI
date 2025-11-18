"""
Experiment Controller: Manages participant assignment, interface ordering, and task sequencing
"""
import random
import json
from database import db
from models import Participant, Task

# All possible interface orders (6 permutations)
INTERFACE_ORDERS = [
    ["faceted", "llm_assist", "llm_only"],
    ["faceted", "llm_only", "llm_assist"],
    ["llm_assist", "faceted", "llm_only"],
    ["llm_assist", "llm_only", "faceted"],
    ["llm_only", "faceted", "llm_assist"],
    ["llm_only", "llm_assist", "faceted"]
]

def get_or_create_participant(participant_id):
    """Get existing participant or create new one with randomized interface order"""
    try:
        participant = Participant.query.filter_by(participant_id=participant_id).first()
        
        if not participant:
            # Assign random interface order
            interface_order = random.choice(INTERFACE_ORDERS)
            participant = Participant(
                participant_id=participant_id,
                interface_order=json.dumps(interface_order)
            )
            db.session.add(participant)
            db.session.commit()
        
        return participant
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Database error: {str(e)}")

def get_experiment_plan(participant_id):
    """Returns the full experiment plan for a participant"""
    participant = get_or_create_participant(participant_id)
    
    if not participant.interface_order:
        interface_order = random.choice(INTERFACE_ORDERS)
        participant.interface_order = json.dumps(interface_order)
        db.session.commit()
    
    interface_order = json.loads(participant.interface_order)
    
    # Get tasks for each interface
    plan = {}
    for interface in interface_order:
        tasks = Task.query.filter_by(interface_type=interface).all()
        plan[interface] = [task.to_dict() for task in tasks]
    
    return {
        'participant_id': participant_id,
        'interface_order': interface_order,
        'tasks': plan,
        'consent_given': participant.consent_given
    }

def record_consent(participant_id):
    """Record that participant has given consent"""
    participant = get_or_create_participant(participant_id)
    from datetime import datetime
    participant.consent_given = True
    participant.consent_timestamp = datetime.utcnow()
    db.session.commit()
    return participant  # Return the Participant object, not dict

