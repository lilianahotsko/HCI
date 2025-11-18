"""
Create visualizations from experiment results
Generates charts and plots for task performance, questionnaires, and comparisons
"""
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from app import app
from database import db
from models import Participant, Task, LogEntry, QuestionnaireResponse

# Get the project root directory (parent of backend)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')
VIZ_DIR = os.path.join(RESULTS_DIR, 'visualizations')

# Create visualizations directory if it doesn't exist
os.makedirs(VIZ_DIR, exist_ok=True)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

def load_data():
    """Load data from CSV files or database"""
    task_file = os.path.join(RESULTS_DIR, 'task_performance.csv')
    q_file = os.path.join(RESULTS_DIR, 'questionnaire_responses.csv')
    
    task_df = None
    q_df = None
    
    if os.path.exists(task_file):
        task_df = pd.read_csv(task_file)
    if os.path.exists(q_file):
        q_df = pd.read_csv(q_file)
    
    return task_df, q_df

def plot_task_duration_by_interface(task_df):
    """Plot task completion time by interface type"""
    if task_df is None or task_df.empty:
        print("No task performance data available")
        return
    
    plt.figure(figsize=(10, 6))
    
    # Box plot
    ax = sns.boxplot(data=task_df, x='interface_type', y='duration_seconds', 
                     palette='Set2')
    ax.set_xlabel('Interface Type', fontsize=12)
    ax.set_ylabel('Task Duration (seconds)', fontsize=12)
    ax.set_title('Task Completion Time by Interface', fontsize=14, fontweight='bold')
    ax.set_xticklabels(['Faceted', 'LLM-Assisted', 'LLM-Only'])
    
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'task_duration_by_interface.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: task_duration_by_interface.png")

def plot_reformulations_by_interface(task_df):
    """Plot reformulation counts by interface"""
    if task_df is None or task_df.empty:
        return
    
    plt.figure(figsize=(10, 6))
    
    # Bar plot showing average reformulations
    reform_data = task_df.groupby('interface_type')['reformulations'].mean().reset_index()
    
    ax = sns.barplot(data=reform_data, x='interface_type', y='reformulations', 
                     palette='Set2')
    ax.set_xlabel('Interface Type', fontsize=12)
    ax.set_ylabel('Average Reformulations', fontsize=12)
    ax.set_title('Average Number of Reformulations by Interface', fontsize=14, fontweight='bold')
    ax.set_xticklabels(['Faceted', 'LLM-Assisted', 'LLM-Only'])
    
    # Add value labels on bars
    for i, v in enumerate(reform_data['reformulations']):
        ax.text(i, v + 0.05, f'{v:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'reformulations_by_interface.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: reformulations_by_interface.png")

def plot_sus_scores(q_df):
    """Plot SUS scores by interface"""
    if q_df is None or q_df.empty:
        return
    
    sus_df = q_df[q_df['questionnaire_type'] == 'SUS'].copy()
    if sus_df.empty:
        print("No SUS questionnaire data available")
        return
    
    # Calculate SUS scores (1-5 scale, need to convert to 0-100)
    # SUS: odd items (1,3,5,7,9) score = scale position - 1
    #      even items (2,4,6,8,10) score = 5 - scale position
    # Total SUS = sum * 2.5 (0-100 scale)
    
    sus_scores = []
    for idx, row in sus_df.iterrows():
        score = 0
        for i in range(10):
            key = str(i)
            if key in row and pd.notna(row[key]):
                value = int(row[key])
                if (i + 1) % 2 == 1:  # Odd items
                    score += (value - 1)
                else:  # Even items
                    score += (5 - value)
        sus_scores.append(score * 2.5)
    
    sus_df['sus_score'] = sus_scores
    
    plt.figure(figsize=(10, 6))
    ax = sns.boxplot(data=sus_df, x='interface_type', y='sus_score', palette='Set2')
    ax.set_xlabel('Interface Type', fontsize=12)
    ax.set_ylabel('SUS Score (0-100)', fontsize=12)
    ax.set_title('System Usability Scale (SUS) Scores by Interface', fontsize=14, fontweight='bold')
    ax.set_xticklabels(['Faceted', 'LLM-Assisted', 'LLM-Only'])
    ax.axhline(y=68, color='r', linestyle='--', label='Average SUS Score (68)')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'sus_scores_by_interface.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: sus_scores_by_interface.png")

def plot_nasa_tlx(q_df):
    """Plot NASA-TLX scores by interface"""
    if q_df is None or q_df.empty:
        return
    
    nasa_df = q_df[q_df['questionnaire_type'] == 'NASA_TLX'].copy()
    if nasa_df.empty:
        print("No NASA-TLX questionnaire data available")
        return
    
    # Get NASA-TLX dimensions
    dimensions = ['mental_demand', 'physical_demand', 'temporal_demand', 
                  'performance', 'effort', 'frustration']
    
    # Calculate average scores for each dimension by interface
    nasa_data = []
    for interface in nasa_df['interface_type'].unique():
        if pd.isna(interface):
            continue
        interface_data = nasa_df[nasa_df['interface_type'] == interface]
        for dim in dimensions:
            if dim in interface_data.columns:
                values = interface_data[dim].dropna()
                if not values.empty:
                    nasa_data.append({
                        'interface_type': interface,
                        'dimension': dim.replace('_', ' ').title(),
                        'score': values.mean()
                    })
    
    if not nasa_data:
        return
    
    nasa_plot_df = pd.DataFrame(nasa_data)
    
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(data=nasa_plot_df, x='dimension', y='score', hue='interface_type', 
                     palette='Set2')
    ax.set_xlabel('NASA-TLX Dimension', fontsize=12)
    ax.set_ylabel('Average Score (0-100)', fontsize=12)
    ax.set_title('NASA-TLX Workload Scores by Interface', fontsize=14, fontweight='bold')
    ax.legend(title='Interface Type', labels=['Faceted', 'LLM-Assisted', 'LLM-Only'])
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'nasa_tlx_by_interface.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: nasa_tlx_by_interface.png")

def plot_trust_scores(q_df):
    """Plot trust questionnaire scores by interface"""
    if q_df is None or q_df.empty:
        return
    
    trust_df = q_df[q_df['questionnaire_type'] == 'trust'].copy()
    if trust_df.empty:
        print("No trust questionnaire data available")
        return
    
    # Get trust questions
    trust_cols = [col for col in trust_df.columns if col.startswith('trust_')]
    
    trust_data = []
    for interface in trust_df['interface_type'].unique():
        if pd.isna(interface):
            continue
        interface_data = trust_df[trust_df['interface_type'] == interface]
        for col in trust_cols:
            values = interface_data[col].dropna()
            if not values.empty:
                trust_data.append({
                    'interface_type': interface,
                    'question': col.replace('trust_', '').replace('_', ' ').title(),
                    'score': values.mean()
                })
    
    if not trust_data:
        return
    
    trust_plot_df = pd.DataFrame(trust_data)
    
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(data=trust_plot_df, x='question', y='score', hue='interface_type', 
                     palette='Set2')
    ax.set_xlabel('Trust Question', fontsize=12)
    ax.set_ylabel('Average Score (1-7)', fontsize=12)
    ax.set_title('Trust Ratings by Interface', fontsize=14, fontweight='bold')
    ax.legend(title='Interface Type', labels=['Faceted', 'LLM-Assisted', 'LLM-Only'])
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'trust_scores_by_interface.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: trust_scores_by_interface.png")

def plot_preference_scores(q_df):
    """Plot preference questionnaire scores"""
    if q_df is None or q_df.empty:
        return
    
    pref_df = q_df[q_df['questionnaire_type'] == 'preference'].copy()
    if pref_df.empty:
        print("No preference questionnaire data available")
        return
    
    metrics = ['ease_of_use', 'efficiency', 'satisfaction']
    
    pref_data = []
    for interface in pref_df['interface_type'].unique():
        if pd.isna(interface):
            continue
        interface_data = pref_df[pref_df['interface_type'] == interface]
        for metric in metrics:
            if metric in interface_data.columns:
                values = interface_data[metric].dropna().astype(float)
                if not values.empty:
                    pref_data.append({
                        'interface_type': interface,
                        'metric': metric.replace('_', ' ').title(),
                        'score': values.mean()
                    })
    
    if not pref_data:
        return
    
    pref_plot_df = pd.DataFrame(pref_data)
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=pref_plot_df, x='metric', y='score', hue='interface_type', 
                     palette='Set2')
    ax.set_xlabel('Metric', fontsize=12)
    ax.set_ylabel('Average Score (1-7)', fontsize=12)
    ax.set_title('User Preference Ratings by Interface', fontsize=14, fontweight='bold')
    ax.legend(title='Interface Type', labels=['Faceted', 'LLM-Assisted', 'LLM-Only'])
    ax.set_ylim(0, 7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'preference_scores_by_interface.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: preference_scores_by_interface.png")

def plot_task_complexity_comparison(task_df):
    """Compare task performance by complexity"""
    if task_df is None or task_df.empty or 'complexity' not in task_df.columns:
        return
    
    plt.figure(figsize=(12, 6))
    
    # Duration by complexity and interface
    ax = sns.boxplot(data=task_df, x='complexity', y='duration_seconds', 
                     hue='interface_type', palette='Set2')
    ax.set_xlabel('Task Complexity', fontsize=12)
    ax.set_ylabel('Task Duration (seconds)', fontsize=12)
    ax.set_title('Task Duration by Complexity and Interface', fontsize=14, fontweight='bold')
    ax.legend(title='Interface Type', labels=['Faceted', 'LLM-Assisted', 'LLM-Only'])
    
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'task_duration_by_complexity.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: task_duration_by_complexity.png")

def create_summary_dashboard(task_df, q_df):
    """Create a summary dashboard with multiple metrics"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Experiment Results Summary Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Task Duration
    if task_df is not None and not task_df.empty:
        sns.boxplot(data=task_df, x='interface_type', y='duration_seconds', 
                   palette='Set2', ax=axes[0, 0])
        axes[0, 0].set_title('Task Duration by Interface')
        axes[0, 0].set_xlabel('Interface Type')
        axes[0, 0].set_ylabel('Duration (seconds)')
        axes[0, 0].set_xticklabels(['Faceted', 'LLM-Assisted', 'LLM-Only'])
    
    # 2. Reformulations
    if task_df is not None and not task_df.empty:
        reform_data = task_df.groupby('interface_type')['reformulations'].mean().reset_index()
        sns.barplot(data=reform_data, x='interface_type', y='reformulations', 
                   palette='Set2', ax=axes[0, 1])
        axes[0, 1].set_title('Average Reformulations')
        axes[0, 1].set_xlabel('Interface Type')
        axes[0, 1].set_ylabel('Reformulations')
        axes[0, 1].set_xticklabels(['Faceted', 'LLM-Assisted', 'LLM-Only'])
    
    # 3. SUS Scores
    if q_df is not None and not q_df.empty:
        sus_df = q_df[q_df['questionnaire_type'] == 'SUS'].copy()
        if not sus_df.empty:
            # Calculate SUS scores (simplified)
            sus_scores = []
            for idx, row in sus_df.iterrows():
                score = 0
                for i in range(10):
                    key = str(i)
                    if key in row and pd.notna(row[key]):
                        value = int(row[key])
                        if (i + 1) % 2 == 1:
                            score += (value - 1)
                        else:
                            score += (5 - value)
                sus_scores.append(score * 2.5)
            sus_df['sus_score'] = sus_scores
            
            sns.boxplot(data=sus_df, x='interface_type', y='sus_score', 
                       palette='Set2', ax=axes[1, 0])
            axes[1, 0].set_title('SUS Scores by Interface')
            axes[1, 0].set_xlabel('Interface Type')
            axes[1, 0].set_ylabel('SUS Score')
            axes[1, 0].set_xticklabels(['Faceted', 'LLM-Assisted', 'LLM-Only'])
    
    # 4. Preference Scores
    if q_df is not None and not q_df.empty:
        pref_df = q_df[q_df['questionnaire_type'] == 'preference'].copy()
        if not pref_df.empty:
            metrics = ['ease_of_use', 'efficiency', 'satisfaction']
            pref_data = []
            for interface in pref_df['interface_type'].unique():
                if pd.isna(interface):
                    continue
                interface_data = pref_df[pref_df['interface_type'] == interface]
                for metric in metrics:
                    if metric in interface_data.columns:
                        values = interface_data[metric].dropna().astype(float)
                        if not values.empty:
                            pref_data.append({
                                'interface_type': interface,
                                'metric': metric.replace('_', ' ').title(),
                                'score': values.mean()
                            })
            
            if pref_data:
                pref_plot_df = pd.DataFrame(pref_data)
                sns.barplot(data=pref_plot_df, x='metric', y='score', hue='interface_type', 
                           palette='Set2', ax=axes[1, 1])
                axes[1, 1].set_title('User Preferences')
                axes[1, 1].set_xlabel('Metric')
                axes[1, 1].set_ylabel('Score (1-7)')
                axes[1, 1].legend(title='Interface Type', labels=['Faceted', 'LLM-Assisted', 'LLM-Only'])
                axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'summary_dashboard.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: summary_dashboard.png")

def main():
    """Generate all visualizations"""
    print(f"\n{'='*60}")
    print("Generating Visualizations")
    print(f"{'='*60}\n")
    print(f"Output directory: {VIZ_DIR}\n")
    
    # Load data
    task_df, q_df = load_data()
    
    if task_df is None and q_df is None:
        print("No data files found. Please run 'python analyze_results.py export' first.")
        return
    
    # Generate individual visualizations
    plot_task_duration_by_interface(task_df)
    plot_reformulations_by_interface(task_df)
    plot_sus_scores(q_df)
    plot_nasa_tlx(q_df)
    plot_trust_scores(q_df)
    plot_preference_scores(q_df)
    plot_task_complexity_comparison(task_df)
    
    # Generate summary dashboard
    create_summary_dashboard(task_df, q_df)
    
    print(f"\n{'='*60}")
    print(f"✓ All visualizations created in: {VIZ_DIR}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()

