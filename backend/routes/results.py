"""
API routes for viewing and exporting experiment results
"""
from flask import Blueprint, jsonify, send_file, render_template_string
from app import app
from database import db
from models import Participant, Task, LogEntry, QuestionnaireResponse
try:
    from analyze_results import (
        analyze_task_performance,
        analyze_questionnaires,
        get_all_participants,
        get_task_logs,
        export_to_csv
    )
except ImportError as e:
    print(f"Warning: Could not import analyze_results: {e}")
    # Define fallback functions
    def analyze_task_performance():
        return []
    def analyze_questionnaires():
        return []
    def get_all_participants():
        return []
    def get_task_logs():
        return []
    def export_to_csv():
        pass

import json
import os
import tempfile
import zipfile
from datetime import datetime
try:
    import pandas as pd
except ImportError:
    pd = None

bp = Blueprint('results', __name__, url_prefix='/api/results')

@bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Render results dashboard HTML page"""
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HCI Experiment Results Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        header {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        h1 { color: #2c3e50; }
        .btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            text-decoration: none;
            display: inline-block;
            transition: background 0.3s;
        }
        .btn:hover { background: #2980b9; }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #229954; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-card h3 {
            color: #7f8c8d;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }
        .section {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .section h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }
        tr:hover { background: #f8f9fa; }
        .loading {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }
        .error {
            background: #e74c3c;
            color: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-faceted { background: #3498db; color: white; }
        .badge-llm_assist { background: #9b59b6; color: white; }
        .badge-llm_only { background: #e67e22; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Experiment Results Dashboard</h1>
            <div>
                <button class="btn btn-success" onclick="downloadResults()">📥 Download All Results</button>
                <button class="btn" onclick="refreshData()">🔄 Refresh</button>
            </div>
        </header>

        <div id="loading" class="loading">Loading data...</div>
        <div id="error" class="error" style="display:none;"></div>

        <div id="content" style="display:none;">
            <div class="stats-grid" id="stats"></div>
            
            <div class="section">
                <h2>📈 Task Performance by Interface</h2>
                <div id="task-performance"></div>
            </div>

            <div class="section">
                <h2>📝 Questionnaire Responses</h2>
                <div id="questionnaires"></div>
            </div>

            <div class="section">
                <h2>👥 Participants</h2>
                <div id="participants"></div>
            </div>
        </div>
    </div>

    <script>
        async function loadData() {
            try {
                const [summary, tasks, questionnaires, participants] = await Promise.all([
                    fetch('/api/results/summary').then(r => r.json()),
                    fetch('/api/results/tasks').then(r => r.json()),
                    fetch('/api/results/questionnaires').then(r => r.json()),
                    fetch('/api/results/participants').then(r => r.json())
                ]);

                document.getElementById('loading').style.display = 'none';
                document.getElementById('content').style.display = 'block';

                renderStats(summary);
                renderTaskPerformance(tasks, summary);
                renderQuestionnaires(questionnaires);
                renderParticipants(participants);
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
                document.getElementById('error').textContent = 'Error loading data: ' + error.message;
            }
        }

        function renderStats(summary) {
            const stats = document.getElementById('stats');
            stats.innerHTML = `
                <div class="stat-card">
                    <h3>Total Participants</h3>
                    <div class="value">${summary.total_participants || 0}</div>
                </div>
                <div class="stat-card">
                    <h3>Task Completions</h3>
                    <div class="value">${summary.total_task_completions || 0}</div>
                </div>
                <div class="stat-card">
                    <h3>Questionnaires</h3>
                    <div class="value">${summary.total_questionnaires || 0}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Logs</h3>
                    <div class="value">${summary.total_logs || 0}</div>
                </div>
            `;
        }

        function renderTaskPerformance(tasks, summary) {
            const container = document.getElementById('task-performance');
            
            if (!tasks || tasks.length === 0) {
                container.innerHTML = '<p>No task performance data available yet.</p>';
                return;
            }

            let html = '<table><thead><tr>';
            html += '<th>Interface</th><th>Tasks</th><th>Avg Duration (s)</th><th>Avg Precision</th><th>Avg Recall</th><th>Avg F1 Score</th>';
            html += '</tr></thead><tbody>';

            if (summary.by_interface) {
                Object.entries(summary.by_interface).forEach(([interface, data]) => {
                    html += `<tr>
                        <td><span class="badge badge-${interface}">${interface}</span></td>
                        <td>${data.count}</td>
                        <td>${data.avg_duration_seconds ? data.avg_duration_seconds.toFixed(1) : 'N/A'}</td>
                        <td>${data.avg_precision ? data.avg_precision.toFixed(3) : 'N/A'}</td>
                        <td>${data.avg_recall ? data.avg_recall.toFixed(3) : 'N/A'}</td>
                        <td>${data.avg_f1_score ? data.avg_f1_score.toFixed(3) : 'N/A'}</td>
                    </tr>`;
                });
            }

            html += '</tbody></table>';
            container.innerHTML = html;
        }

        function renderQuestionnaires(questionnaires) {
            const container = document.getElementById('questionnaires');
            
            if (!questionnaires || questionnaires.length === 0) {
                container.innerHTML = '<p>No questionnaire responses yet.</p>';
                return;
            }

            let html = '<table><thead><tr>';
            html += '<th>Participant</th><th>Interface</th><th>Type</th><th>Submitted</th>';
            html += '</tr></thead><tbody>';

            questionnaires.forEach(q => {
                html += `<tr>
                    <td>${q.participant_id}</td>
                    <td><span class="badge badge-${q.interface_type}">${q.interface_type}</span></td>
                    <td>${q.questionnaire_type}</td>
                    <td>${new Date(q.submitted_at).toLocaleString()}</td>
                </tr>`;
            });

            html += '</tbody></table>';
            container.innerHTML = html;
        }

        function renderParticipants(participants) {
            const container = document.getElementById('participants');
            
            if (!participants || participants.length === 0) {
                container.innerHTML = '<p>No participants yet.</p>';
                return;
            }

            let html = '<table><thead><tr>';
            html += '<th>Participant ID</th><th>Consent</th><th>Interface Order</th><th>Created</th>';
            html += '</tr></thead><tbody>';

            participants.forEach(p => {
                html += `<tr>
                    <td>${p.participant_id}</td>
                    <td>${p.consent_given ? '✓' : '✗'}</td>
                    <td>${p.interface_order ? p.interface_order.join(' → ') : 'N/A'}</td>
                    <td>${new Date(p.created_at).toLocaleString()}</td>
                </tr>`;
            });

            html += '</tbody></table>';
            container.innerHTML = html;
        }

        function downloadResults() {
            window.location.href = '/api/results/export';
        }

        function refreshData() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('content').style.display = 'none';
            loadData();
        }

        // Load data on page load
        loadData();
    </script>
</body>
</html>
    """
    return render_template_string(html)

@bp.route('/summary', methods=['GET'])
def get_summary():
    """Get summary statistics"""
    with app.app_context():
        participants = Participant.query.all()
        task_perf = analyze_task_performance()
        
        summary = {
            'total_participants': len(participants),
            'total_task_completions': len(task_perf),
            'total_questionnaires': QuestionnaireResponse.query.count(),
            'total_logs': LogEntry.query.count()
        }
        
        if task_perf and pd is not None:
            try:
                df = pd.DataFrame(task_perf)
                
                summary['by_interface'] = {}
                for interface in df['interface_type'].unique():
                    interface_df = df[df['interface_type'] == interface]
                    summary['by_interface'][interface] = {
                        'count': len(interface_df),
                        'avg_duration_seconds': float(interface_df['duration_seconds'].mean()) if len(interface_df) > 0 else 0,
                        'avg_precision': float(interface_df['precision'].mean()) if interface_df['precision'].notna().any() else None,
                        'avg_recall': float(interface_df['recall'].mean()) if interface_df['recall'].notna().any() else None,
                        'avg_f1_score': float(interface_df['f1_score'].mean()) if interface_df['f1_score'].notna().any() else None
                    }
            except Exception as e:
                print(f"Error calculating interface stats: {e}")
                summary['by_interface'] = {}
        
        return jsonify(summary), 200

@bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all task performance data"""
    with app.app_context():
        results = analyze_task_performance()
        return jsonify(results), 200

@bp.route('/questionnaires', methods=['GET'])
def get_questionnaires():
    """Get all questionnaire responses"""
    with app.app_context():
        results = analyze_questionnaires()
        return jsonify(results), 200

@bp.route('/participants', methods=['GET'])
def get_participants():
    """Get all participant data"""
    with app.app_context():
        results = get_all_participants()
        return jsonify(results), 200

@bp.route('/export', methods=['GET'])
def export_results():
    """Export all results as CSV files in a ZIP archive"""
    with app.app_context():
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Change to temp directory and export
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            # Export CSV files
            export_to_csv()
            
            # Create ZIP file
            zip_filename = f'experiment_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
            zip_path = os.path.join(temp_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in os.listdir(temp_dir):
                    if file.endswith('.csv'):
                        zipf.write(file, file)
            
            os.chdir(original_dir)
            
            return send_file(
                zip_path,
                mimetype='application/zip',
                as_attachment=True,
                download_name=zip_filename
            )
        except Exception as e:
            os.chdir(original_dir)
            return jsonify({'error': str(e)}), 500

@bp.route('/export/json', methods=['GET'])
def export_json():
    """Export all results as JSON"""
    with app.app_context():
        data = {
            'exported_at': datetime.utcnow().isoformat(),
            'participants': get_all_participants(),
            'task_performance': analyze_task_performance(),
            'questionnaires': analyze_questionnaires(),
            'logs': get_task_logs()
        }
        
        return jsonify(data), 200

