"""
Analysis script for HCI experiment results
Extracts and analyzes participant data, task performance, and questionnaire responses
"""
import json
import os
from app import app
from database import db
from models import Participant, Task, LogEntry, QuestionnaireResponse, Movie
from datetime import datetime
from collections import defaultdict
import pandas as pd

# Get the project root directory (parent of backend)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

# Create results directory if it doesn't exist
os.makedirs(RESULTS_DIR, exist_ok=True)

def get_all_participants():
    """Get all participants"""
    with app.app_context():
        participants = Participant.query.all()
        return [p.to_dict() for p in participants]

def get_task_logs(participant_id=None, task_id=None, interface_type=None):
    """Get task-related logs"""
    with app.app_context():
        query = LogEntry.query
        
        if participant_id:
            query = query.filter_by(participant_id=participant_id)
        if task_id:
            query = query.filter_by(task_id=task_id)
        if interface_type:
            query = query.filter_by(interface_type=interface_type)
        
        logs = query.order_by(LogEntry.timestamp).all()
        return [log.to_dict() for log in logs]

def analyze_task_performance():
    """Analyze task completion times and accuracy"""
    with app.app_context():
        # Get all task start/end events
        task_starts = {}
        task_ends = {}
        
        logs = LogEntry.query.filter(
            LogEntry.event_type.in_(['task_started', 'task_completed'])
        ).order_by(LogEntry.timestamp).all()
        
        for log in logs:
            key = (log.participant_id, log.task_id, log.interface_type)
            payload = json.loads(log.payload) if log.payload else {}
            
            if log.event_type == 'task_started':
                task_starts[key] = log.timestamp
            elif log.event_type == 'task_completed':
                task_ends[key] = {
                    'timestamp': log.timestamp,
                    'submission': payload
                }
        
        # Calculate task durations
        results = []
        for key in task_ends:
            participant_id, task_id, interface_type = key
            if key in task_starts:
                duration = (task_ends[key]['timestamp'] - task_starts[key]).total_seconds()
                submission = task_ends[key]['submission']
                
                # Get task details
                task = Task.query.filter_by(task_id=task_id).first()
                
                results.append({
                    'participant_id': participant_id,
                    'task_id': task_id,
                    'interface_type': interface_type,
                    'task_description': task.description if task else None,
                    'complexity': task.complexity if task else None,
                    'duration_seconds': duration,
                    'selected_movie_count': len(submission.get('selected_movie_ids', [])),
                    'result_count': submission.get('result_count', 0),
                    'reformulations': submission.get('reformulations', 0),
                    'submission': submission
                })
        
        return results

def analyze_questionnaires():
    """Analyze questionnaire responses"""
    with app.app_context():
        questionnaires = QuestionnaireResponse.query.all()
        results = []
        
        for q in questionnaires:
            responses = json.loads(q.responses) if q.responses else {}
            results.append({
                'participant_id': q.participant_id,
                'interface_type': q.interface_type,
                'questionnaire_type': q.questionnaire_type,
                'responses': responses,
                'submitted_at': q.submitted_at.isoformat() if q.submitted_at else None
            })
        
        return results

def count_reformulations(participant_id, task_id, interface_type):
    """Count reformulations for a task"""
    with app.app_context():
        logs = LogEntry.query.filter_by(
            participant_id=participant_id,
            task_id=task_id,
            interface_type=interface_type
        ).order_by(LogEntry.timestamp).all()
        
        reformulation_events = ['nl_query_sent', 'filter_change', 'query_confirmed']
        reformulation_count = 0
        
        for log in logs:
            if log.event_type in reformulation_events:
                # Check if this is a reformulation (not the first query)
                if log.event_type == 'nl_query_sent':
                    # Count how many nl_query_sent events before a query_executed
                    reformulation_count += 1
        
        # Subtract 1 for the initial query (reformulations = total - 1)
        return max(0, reformulation_count - 1)

def export_to_csv():
    """Export all data to CSV files"""
    with app.app_context():
        print(f"Exporting data to: {RESULTS_DIR}\n")
        
        # Task performance
        task_perf = analyze_task_performance()
        if task_perf:
            df_tasks = pd.DataFrame(task_perf)
            filepath = os.path.join(RESULTS_DIR, 'task_performance.csv')
            df_tasks.to_csv(filepath, index=False)
            print(f"✓ Exported {len(task_perf)} task records to {filepath}")
        
        # Questionnaires
        questionnaires = analyze_questionnaires()
        if questionnaires:
            # Flatten questionnaire data
            q_data = []
            for q in questionnaires:
                row = {
                    'participant_id': q['participant_id'],
                    'interface_type': q['interface_type'],
                    'questionnaire_type': q['questionnaire_type'],
                    'submitted_at': q['submitted_at']
                }
                # Add individual responses
                for key, value in q['responses'].items():
                    row[key] = value
                q_data.append(row)
            
            df_q = pd.DataFrame(q_data)
            filepath = os.path.join(RESULTS_DIR, 'questionnaire_responses.csv')
            df_q.to_csv(filepath, index=False)
            print(f"✓ Exported {len(questionnaires)} questionnaire records to {filepath}")
        
        # All logs
        logs = get_task_logs()
        if logs:
            df_logs = pd.DataFrame(logs)
            filepath = os.path.join(RESULTS_DIR, 'all_logs.csv')
            df_logs.to_csv(filepath, index=False)
            print(f"✓ Exported {len(logs)} log entries to {filepath}")
        
        # Participants
        participants = get_all_participants()
        if participants:
            df_participants = pd.DataFrame(participants)
            filepath = os.path.join(RESULTS_DIR, 'participants.csv')
            df_participants.to_csv(filepath, index=False)
            print(f"✓ Exported {len(participants)} participant records to {filepath}")
        
        print(f"\n✓ All exports completed! Files saved to: {RESULTS_DIR}")

def print_summary():
    """Print summary statistics"""
    with app.app_context():
        print("\n" + "="*60)
        print("EXPERIMENT RESULTS SUMMARY")
        print("="*60)
        
        # Participants
        participants = Participant.query.all()
        print(f"\nTotal Participants: {len(participants)}")
        
        # Task performance
        task_perf = analyze_task_performance()
        if task_perf:
            df = pd.DataFrame(task_perf)
            print(f"\nTotal Task Completions: {len(task_perf)}")
            print(f"\nAverage Task Duration by Interface:")
            print(df.groupby('interface_type')['duration_seconds'].mean())
            print(f"\nAverage Reformulations by Interface:")
            print(df.groupby('interface_type')['reformulations'].mean())
        
        # Questionnaires
        questionnaires = QuestionnaireResponse.query.all()
        print(f"\nTotal Questionnaire Responses: {len(questionnaires)}")
        
        print("\n" + "="*60)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'export':
            export_to_csv()
        elif command == 'summary':
            print_summary()
        elif command == 'tasks':
            results = analyze_task_performance()
            print(json.dumps(results, indent=2, default=str))
        elif command == 'questionnaires':
            results = analyze_questionnaires()
            print(json.dumps(results, indent=2, default=str))
        elif command == 'participants':
            results = get_all_participants()
            print(json.dumps(results, indent=2, default=str))
        else:
            print("Usage:")
            print("  python analyze_results.py export      - Export all data to CSV")
            print("  python analyze_results.py summary    - Print summary statistics")
            print("  python analyze_results.py tasks      - Show task performance data")
            print("  python analyze_results.py questionnaires - Show questionnaire data")
            print("  python analyze_results.py participants - Show participant data")
    else:
        print_summary()
        print("\nUse 'python analyze_results.py export' to export data to CSV files")
        print("Use 'python analyze_results.py summary' for detailed statistics")

