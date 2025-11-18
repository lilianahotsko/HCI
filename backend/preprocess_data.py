"""
Data preprocessing script: Load TMDB 5000 dataset into database
This script expects a CSV file with TMDB movie data
"""
import pandas as pd
import json
from app import app
from database import db
from models import Movie, Task
import os

def extract_genres(genres_str):
    """Extract genres from JSON string or list"""
    if pd.isna(genres_str):
        return []
    try:
        if isinstance(genres_str, str):
            genres_list = json.loads(genres_str)
        else:
            genres_list = genres_str
        return [g.get('name', g) if isinstance(g, dict) else g for g in genres_list]
    except:
        return []

def determine_lead_gender(movie_data):
    """
    Determine lead actor gender (simplified heuristic)
    In a real scenario, you'd use cast data or external APIs
    For now, we'll use a placeholder approach
    """
    # This is a placeholder - in reality you'd analyze cast data
    # For now, randomly assign or use a default
    import random
    return random.choice(['female', 'male', 'mixed', 'unknown'])

def load_movies_from_csv(csv_path):
    """Load movies from CSV file"""
    print(f"Loading movies from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    print(f"Found {len(df)} movies in CSV")
    
    movies_added = 0
    for idx, row in df.iterrows():
        try:
            # Extract genres
            genres = extract_genres(row.get('genres', '[]'))
            
            # Create movie record
            movie = Movie(
                title=row.get('title', 'Unknown'),
                release_year=int(row.get('release_date', '1900')[:4]) if pd.notna(row.get('release_date')) else None,
                runtime=int(row.get('runtime', 0)) if pd.notna(row.get('runtime')) else None,
                genres=json.dumps(genres),
                lead_gender=determine_lead_gender(row),  # Placeholder
                budget=float(row.get('budget', 0)) if pd.notna(row.get('budget')) and row.get('budget') > 0 else None,
                revenue=float(row.get('revenue', 0)) if pd.notna(row.get('revenue')) and row.get('revenue') > 0 else None,
                language=row.get('original_language', 'en'),
                overview=row.get('overview', ''),
                tmdb_id=int(row.get('id', idx)) if pd.notna(row.get('id')) else None
            )
            
            db.session.add(movie)
            movies_added += 1
            
            if movies_added % 100 == 0:
                print(f"Processed {movies_added} movies...")
                db.session.commit()
                
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue
    
    db.session.commit()
    print(f"Successfully loaded {movies_added} movies into database")
    return movies_added

def create_sample_tasks():
    """Create sample tasks for the experiment"""
    tasks = [
        {
            'task_id': 'T01',
            'description': 'Find all movies released after 2015 with runtime under 100 minutes.',
            'complexity': 'simple',
            'interface_type': 'faceted',
            'ground_truth': []
        },
        {
            'task_id': 'T02',
            'description': 'Find all drama or thriller movies with a female lead, budget under $10M, sorted by highest revenue.',
            'complexity': 'complex',
            'interface_type': 'faceted',
            'ground_truth': []
        },
        {
            'task_id': 'T03',
            'description': 'Find all movies released after 2015 with runtime under 100 minutes.',
            'complexity': 'simple',
            'interface_type': 'llm_assist',
            'ground_truth': []
        },
        {
            'task_id': 'T04',
            'description': 'Find all drama or thriller movies with a female lead, budget under $10M, sorted by highest revenue.',
            'complexity': 'complex',
            'interface_type': 'llm_assist',
            'ground_truth': []
        },
        {
            'task_id': 'T05',
            'description': 'Find all movies released after 2015 with runtime under 100 minutes.',
            'complexity': 'simple',
            'interface_type': 'llm_only',
            'ground_truth': []
        },
        {
            'task_id': 'T06',
            'description': 'Find all drama or thriller movies with a female lead, budget under $10M, sorted by highest revenue.',
            'complexity': 'complex',
            'interface_type': 'llm_only',
            'ground_truth': []
        },
    ]
    
    for task_data in tasks:
        task = Task(
            task_id=task_data['task_id'],
            description=task_data['description'],
            complexity=task_data['complexity'],
            interface_type=task_data['interface_type'],
            ground_truth=json.dumps(task_data['ground_truth'])
        )
        db.session.add(task)
    
    db.session.commit()
    print(f"Created {len(tasks)} sample tasks")

if __name__ == '__main__':
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if movies already exist
        if Movie.query.count() > 0:
            print("Movies already loaded. Skipping data load.")
        else:
            # Look for TMDB CSV file
            csv_path = os.getenv('TMDB_CSV_PATH', 'tmdb_5000_movies.csv')
            if os.path.exists(csv_path):
                load_movies_from_csv(csv_path)
            else:
                print(f"CSV file not found at {csv_path}")
                print("Please download TMDB 5000 dataset and specify path in TMDB_CSV_PATH env var")
                print("Or place the CSV file in the backend directory as 'tmdb_5000_movies.csv'")
        
        # Create sample tasks
        if Task.query.count() == 0:
            create_sample_tasks()
        else:
            print("Tasks already exist. Skipping task creation.")

