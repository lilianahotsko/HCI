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

def calculate_accuracy_metrics(selected_ids, ground_truth_ids):
    """
    Calculate precision, recall, and F1 score.
    
    Args:
        selected_ids: List of IDs selected by participant
        ground_truth_ids: List of correct IDs (ground truth)
    
    Returns:
        dict with precision, recall, f1, true_positives, false_positives, false_negatives
    """
    if not ground_truth_ids:
        # No ground truth available
        return {
            'precision': None,
            'recall': None,
            'f1_score': None,
            'true_positives': 0,
            'false_positives': len(selected_ids),
            'false_negatives': 0,
            'accuracy': None
        }
    
    # Convert to sets for easier comparison
    selected_set = set(selected_ids)
    ground_truth_set = set(ground_truth_ids)
    
    # Calculate metrics
    true_positives = len(selected_set & ground_truth_set)  # Intersection
    false_positives = len(selected_set - ground_truth_set)  # Selected but not correct
    false_negatives = len(ground_truth_set - selected_set)  # Correct but not selected
    
    # Precision: Of what was selected, how many were correct?
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    
    # Recall: Of what was correct, how many were found?
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    
    # F1 Score: Harmonic mean of precision and recall
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # Overall accuracy: (TP + TN) / Total, but we don't have true negatives in this context
    # So we use precision as a proxy for accuracy
    accuracy = precision
    
    return {
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1_score': round(f1_score, 4),
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'accuracy': round(accuracy, 4),
        'ground_truth_count': len(ground_truth_ids),
        'selected_count': len(selected_ids)
    }

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
        
        # Calculate task durations and accuracy
        results = []
        for key in task_ends:
            participant_id, task_id, interface_type = key
            if key in task_starts:
                duration = (task_ends[key]['timestamp'] - task_starts[key]).total_seconds()
                submission = task_ends[key]['submission']
                
                # Get task details
                task = Task.query.filter_by(task_id=task_id).first()
                
                # Get selected IDs (handle both 'selected_movie_ids' and 'selected_book_ids')
                selected_ids = submission.get('selected_movie_ids', []) or submission.get('selected_book_ids', []) or []
                
                # Get ground truth
                ground_truth_ids = []
                if task and task.ground_truth:
                    try:
                        ground_truth_ids = json.loads(task.ground_truth) if isinstance(task.ground_truth, str) else task.ground_truth
                    except:
                        ground_truth_ids = []
                
                # Calculate accuracy metrics
                accuracy_metrics = calculate_accuracy_metrics(selected_ids, ground_truth_ids)
                
                result = {
                    'participant_id': participant_id,
                    'task_id': task_id,
                    'interface_type': interface_type,
                    'task_description': task.description if task else None,
                    'complexity': task.complexity if task else None,
                    'dataset_type': task.dataset_type if task else None,
                    'duration_seconds': duration,
                    'selected_count': len(selected_ids),
                    'result_count': submission.get('result_count', 0),
                    'reformulations': submission.get('reformulations', 0),
                    'submission': submission
                }
                
                # Add accuracy metrics
                result.update(accuracy_metrics)
                
                results.append(result)
        
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
            
            # Duration statistics
            print(f"\nAverage Task Duration by Interface:")
            print(df.groupby('interface_type')['duration_seconds'].mean())
            
            # Reformulation statistics
            print(f"\nAverage Reformulations by Interface:")
            print(df.groupby('interface_type')['reformulations'].mean())
            
            # Accuracy statistics (only for tasks with ground truth)
            accuracy_df = df[df['precision'].notna()]
            if len(accuracy_df) > 0:
                print(f"\nAccuracy Metrics (tasks with ground truth: {len(accuracy_df)}/{len(df)}):")
                print(f"\nAverage Precision by Interface:")
                print(accuracy_df.groupby('interface_type')['precision'].mean())
                print(f"\nAverage Recall by Interface:")
                print(accuracy_df.groupby('interface_type')['recall'].mean())
                print(f"\nAverage F1 Score by Interface:")
                print(accuracy_df.groupby('interface_type')['f1_score'].mean())
                
                print(f"\nAverage Precision by Complexity:")
                print(accuracy_df.groupby('complexity')['precision'].mean())
                print(f"\nAverage Recall by Complexity:")
                print(accuracy_df.groupby('complexity')['recall'].mean())
            else:
                print("\n⚠️  No accuracy metrics available. Run 'python generate_ground_truth.py' to generate ground truth.")
        
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

