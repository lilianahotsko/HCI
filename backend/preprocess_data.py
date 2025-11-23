"""
Data preprocessing script: Load TMDB 5000 dataset into database
This script expects a CSV file with TMDB movie data
"""
import pandas as pd
import json
from app import app
from database import db
from models import Movie, Task, Book
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

def parse_publication_year(date_value):
    """Extract publication year from various date formats"""
    if pd.isna(date_value):
        return None
    try:
        parsed = pd.to_datetime(str(date_value), errors='coerce')
        return int(parsed.year) if not pd.isna(parsed) else None
    except Exception:
        return None

def load_books_from_csv(csv_path):
    """Load books from CSV file"""
    print(f"Loading books from {csv_path}...")
    df = pd.read_csv(
        csv_path,
        on_bad_lines='skip',
        engine='python'
    )
    df.columns = [col.strip() for col in df.columns]
    
    print(f"Found {len(df)} books in CSV")
    
    books_added = 0
    for idx, row in df.iterrows():
        try:
            goodreads_id = int(row.get('bookID')) if pd.notna(row.get('bookID')) else None
            
            if goodreads_id and Book.query.filter_by(goodreads_id=goodreads_id).first():
                continue
            
            book = Book(
                goodreads_id=goodreads_id,
                title=row.get('title', 'Unknown'),
                authors=row.get('authors', ''),
                average_rating=float(row.get('average_rating')) if pd.notna(row.get('average_rating')) else None,
                isbn=str(row.get('isbn')) if pd.notna(row.get('isbn')) else None,
                isbn13=str(row.get('isbn13')) if pd.notna(row.get('isbn13')) else None,
                language=row.get('language_code', '').strip() if isinstance(row.get('language_code'), str) else None,
                num_pages=int(row.get('num_pages')) if pd.notna(row.get('num_pages')) else None,
                ratings_count=int(row.get('ratings_count')) if pd.notna(row.get('ratings_count')) else None,
                text_reviews_count=int(row.get('text_reviews_count')) if pd.notna(row.get('text_reviews_count')) else None,
                publication_year=parse_publication_year(row.get('publication_date')),
                publisher=row.get('publisher', '')
            )
            
            db.session.add(book)
            books_added += 1
            
            if books_added % 250 == 0:
                print(f"Processed {books_added} books...")
                db.session.commit()
        except Exception as e:
            print(f"Error processing book row {idx}: {e}")
            continue
    
    db.session.commit()
    print(f"Successfully loaded {books_added} books into database")
    return books_added

def create_movie_tasks():
    """Create sample movie tasks for the experiment"""
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
        if Task.query.filter_by(task_id=task_data['task_id']).first():
            continue
        task = Task(
            task_id=task_data['task_id'],
            description=task_data['description'],
            complexity=task_data['complexity'],
            interface_type=task_data['interface_type'],
            dataset_type='movies',
            ground_truth=json.dumps(task_data['ground_truth'])
        )
        db.session.add(task)
    
    db.session.commit()
    print(f"Ensured {len(tasks)} movie sample tasks exist")

def create_book_tasks():
    """Create one sample task per interface for the books dataset"""
    tasks = [
        {
            'task_id': 'B01',
            'description': 'Find English-language books published after 2010 with fewer than 350 pages and highlight at least three options.',
            'complexity': 'simple',
            'interface_type': 'faceted',
            'ground_truth': []
        },
        {
            'task_id': 'B02',
            'description': 'Using natural language, locate highly rated non-English books (average rating above 4.2) with fewer than 500 pages that were published between 2000 and 2020.',
            'complexity': 'complex',
            'interface_type': 'llm_assist',
            'ground_truth': []
        },
        {
            'task_id': 'B03',
            'description': 'Ask the LLM-only interface for the highest-rated books over 400 pages with at least 50,000 ratings that were published before 2005.',
            'complexity': 'complex',
            'interface_type': 'llm_only',
            'ground_truth': []
        },
    ]
    
    for task_data in tasks:
        if Task.query.filter_by(task_id=task_data['task_id']).first():
            continue
        task = Task(
            task_id=task_data['task_id'],
            description=task_data['description'],
            complexity=task_data['complexity'],
            interface_type=task_data['interface_type'],
            dataset_type='books',
            ground_truth=json.dumps(task_data['ground_truth'])
        )
        db.session.add(task)
    
    db.session.commit()
    print(f"Ensured {len(tasks)} book sample tasks exist")

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
        
        # Check if books already exist
        if Book.query.count() > 0:
            print("Books already loaded. Skipping book data load.")
        else:
            books_csv_path = os.getenv('BOOKS_CSV_PATH', 'books.csv')
            if os.path.exists(books_csv_path):
                load_books_from_csv(books_csv_path)
            else:
                print(f"Books CSV file not found at {books_csv_path}")
                print("Place 'books.csv' in the backend directory or set BOOKS_CSV_PATH.")
        
        # Create sample tasks per dataset
        if Task.query.filter_by(dataset_type='movies').count() == 0:
            create_movie_tasks()
        else:
            print("Movie tasks already exist. Skipping movie task creation.")
        
        if Task.query.filter_by(dataset_type='books').count() == 0:
            create_book_tasks()
        else:
            print("Book tasks already exist. Skipping book task creation.")

