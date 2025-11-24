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
    """
    Create movie tasks with multiple unique sets (A, B, C) for each interface.
    This prevents repetition bias - each interface gets different tasks.
    Uses task_set field to group tasks: 'A', 'B', or 'C'
    """
    # Task Set A - First set of unique tasks
    tasks_set_a = [
        {
            'task_id': 'T01A',
            'description': 'Find all movies released after 2015 with runtime under 100 minutes.',
            'complexity': 'simple',
            'interface_type': 'faceted',
            'task_set': 'A',
            'ground_truth': []
        },
        {
            'task_id': 'T02A',
            'description': 'Find all drama or thriller movies with a female lead, budget under $10M, sorted by highest revenue.',
            'complexity': 'complex',
            'interface_type': 'faceted',
            'task_set': 'A',
            'ground_truth': []
        },
        {
            'task_id': 'T03A',
            'description': 'Use the LLM-assist interface to retrieve non-English comedies released between 2000 and 2015 with runtimes under 110 minutes.',
            'complexity': 'simple',
            'interface_type': 'llm_assist',
            'task_set': 'A',
            'ground_truth': []
        },
        {
            'task_id': 'T04A',
            'description': 'Ask the LLM-assist interface for science fiction or adventure films released after 2008 with budgets above $80M and revenues over $200M, sorted by revenue.',
            'complexity': 'complex',
            'interface_type': 'llm_assist',
            'task_set': 'A',
            'ground_truth': []
        },
        {
            'task_id': 'T05A',
            'description': 'Ask the LLM-only interface for mystery or crime movies released before 2000 with runtimes under 130 minutes and budgets below $40M.',
            'complexity': 'simple',
            'interface_type': 'llm_only',
            'task_set': 'A',
            'ground_truth': []
        },
        {
            'task_id': 'T06A',
            'description': 'Use the LLM-only interface to surface female-led drama or history movies released between 1995 and 2020 with budgets under $35M but revenues above $90M.',
            'complexity': 'complex',
            'interface_type': 'llm_only',
            'task_set': 'A',
            'ground_truth': []
        },
    ]
    
    # Task Set B - Second set of unique tasks (different scenarios)
    tasks_set_b = [
        {
            'task_id': 'T01B',
            'description': 'Locate action or adventure movies released between 2010 and 2020 with runtimes over 120 minutes.',
            'complexity': 'simple',
            'interface_type': 'faceted',
            'task_set': 'B',
            'ground_truth': []
        },
        {
            'task_id': 'T02B',
            'description': 'Find horror or thriller films with male leads, released after 2015, with budgets between $5M and $50M, sorted by release year.',
            'complexity': 'complex',
            'interface_type': 'faceted',
            'task_set': 'B',
            'ground_truth': []
        },
        {
            'task_id': 'T03B',
            'description': 'Using natural language, find romantic comedies from the 1990s with runtimes between 90 and 120 minutes.',
            'complexity': 'simple',
            'interface_type': 'llm_assist',
            'task_set': 'B',
            'ground_truth': []
        },
        {
            'task_id': 'T04B',
            'description': 'Ask the assistant to identify animated or family films released after 2010 with revenues exceeding $100M and budgets under $150M.',
            'complexity': 'complex',
            'interface_type': 'llm_assist',
            'task_set': 'B',
            'ground_truth': []
        },
        {
            'task_id': 'T05B',
            'description': 'Request from the LLM-only interface: documentary films released between 2005 and 2015 with runtimes over 90 minutes.',
            'complexity': 'simple',
            'interface_type': 'llm_only',
            'task_set': 'B',
            'ground_truth': []
        },
        {
            'task_id': 'T06B',
            'description': 'Use the LLM-only interface to find war or history movies from before 2010 with budgets over $30M but revenues below $100M, sorted by rating.',
            'complexity': 'complex',
            'interface_type': 'llm_only',
            'task_set': 'B',
            'ground_truth': []
        },
    ]
    
    # Task Set C - Third set of unique tasks (different scenarios)
    tasks_set_c = [
        {
            'task_id': 'T01C',
            'description': 'Find science fiction movies released after 2012 with runtimes under 150 minutes.',
            'complexity': 'simple',
            'interface_type': 'faceted',
            'task_set': 'C',
            'ground_truth': []
        },
        {
            'task_id': 'T02C',
            'description': 'Locate crime or mystery films with mixed-gender leads, released between 2000 and 2015, with revenues above $50M, sorted by budget descending.',
            'complexity': 'complex',
            'interface_type': 'faceted',
            'task_set': 'C',
            'ground_truth': []
        },
        {
            'task_id': 'T03C',
            'description': 'Using the LLM-assist interface, find fantasy or adventure movies from the 2000s with runtimes between 100 and 140 minutes.',
            'complexity': 'simple',
            'interface_type': 'llm_assist',
            'task_set': 'C',
            'ground_truth': []
        },
        {
            'task_id': 'T04C',
            'description': 'Ask the LLM-assist interface for biographical or historical dramas released after 2005 with budgets between $20M and $80M and revenues over $75M.',
            'complexity': 'complex',
            'interface_type': 'llm_assist',
            'task_set': 'C',
            'ground_truth': []
        },
        {
            'task_id': 'T05C',
            'description': 'Request from the LLM-only interface: musical or music-themed films released before 2010 with runtimes under 120 minutes.',
            'complexity': 'simple',
            'interface_type': 'llm_only',
            'task_set': 'C',
            'ground_truth': []
        },
        {
            'task_id': 'T06C',
            'description': 'Use the LLM-only interface to identify western or action-adventure films from 1990-2010 with budgets under $60M but revenues exceeding $80M.',
            'complexity': 'complex',
            'interface_type': 'llm_only',
            'task_set': 'C',
            'ground_truth': []
        },
    ]
    
    # Combine all task sets
    tasks = tasks_set_a + tasks_set_b + tasks_set_c
    
    for task_data in tasks:
        # Check if task already exists for this dataset_type
        if Task.query.filter_by(task_id=task_data['task_id'], dataset_type='movies').first():
            continue
        task = Task(
            task_id=task_data['task_id'],
            description=task_data['description'],
            complexity=task_data['complexity'],
            interface_type=task_data['interface_type'],
            dataset_type='movies',
            task_set=task_data.get('task_set', 'A'),  # Store task set
            ground_truth=json.dumps(task_data['ground_truth'])
        )
        db.session.add(task)
    
    db.session.commit()
    print(f"Ensured {len(tasks)} movie sample tasks exist (3 sets: A, B, C)")

def create_book_tasks():
    """
    Create book tasks with multiple unique sets (A, B, C) for each interface.
    This prevents repetition bias - each interface gets different tasks.
    """
    # Task Set A - First set of unique tasks
    tasks_set_a = [
        {
            'task_id': 'B01A',
            'description': 'Find English-language books published after 2010 with fewer than 350 pages and highlight at least three options.',
            'complexity': 'simple',
            'interface_type': 'faceted',
            'task_set': 'A',
            'ground_truth': []
        },
        {
            'task_id': 'B02A',
            'description': 'Surface award-winning or bestselling books published before 1990 that have at least 4.0 average rating and fewer than 450 pages.',
            'complexity': 'complex',
            'interface_type': 'faceted',
            'task_set': 'A',
            'ground_truth': []
        },
        {
            'task_id': 'B03A',
            'description': 'Using natural language, locate highly rated non-English books (average rating above 4.2) with fewer than 500 pages that were published between 2000 and 2020.',
            'complexity': 'complex',
            'interface_type': 'llm_assist',
            'task_set': 'A',
            'ground_truth': []
        },
        {
            'task_id': 'B04A',
            'description': 'Ask the assistant for contemporary memoirs published after 2015 with more than 30,000 ratings and summarize how they differ.',
            'complexity': 'complex',
            'interface_type': 'llm_assist',
            'task_set': 'A',
            'ground_truth': []
        },
        {
            'task_id': 'B05A',
            'description': 'Ask the LLM-only interface for the highest-rated books over 400 pages with at least 50,000 ratings that were published before 2005.',
            'complexity': 'complex',
            'interface_type': 'llm_only',
            'task_set': 'A',
            'ground_truth': []
        },
        {
            'task_id': 'B06A',
            'description': 'Use the LLM-only interface to recommend cozy mystery series starters under 350 pages that have more than 500 text reviews.',
            'complexity': 'simple',
            'interface_type': 'llm_only',
            'task_set': 'A',
            'ground_truth': []
        },
    ]
    
    # Task Set B - Second set of unique tasks
    tasks_set_b = [
        {
            'task_id': 'B01B',
            'description': 'Locate fiction books published between 2005 and 2015 with page counts between 200 and 400 pages.',
            'complexity': 'simple',
            'interface_type': 'faceted',
            'task_set': 'B',
            'ground_truth': []
        },
        {
            'task_id': 'B02B',
            'description': 'Find science fiction or fantasy novels published after 2000 with average ratings above 4.0 and more than 10,000 ratings, sorted by publication year.',
            'complexity': 'complex',
            'interface_type': 'faceted',
            'task_set': 'B',
            'ground_truth': []
        },
        {
            'task_id': 'B03B',
            'description': 'Using the LLM-assist interface, find historical fiction books from the 1980s and 1990s with fewer than 600 pages.',
            'complexity': 'simple',
            'interface_type': 'llm_assist',
            'task_set': 'B',
            'ground_truth': []
        },
        {
            'task_id': 'B04B',
            'description': 'Ask the assistant to identify young adult novels published after 2010 with ratings between 3.5 and 4.5 and more than 5,000 text reviews.',
            'complexity': 'complex',
            'interface_type': 'llm_assist',
            'task_set': 'B',
            'ground_truth': []
        },
        {
            'task_id': 'B05B',
            'description': 'Request from the LLM-only interface: classic literature books published before 1980 with over 300 pages and at least 20,000 ratings.',
            'complexity': 'simple',
            'interface_type': 'llm_only',
            'task_set': 'B',
            'ground_truth': []
        },
        {
            'task_id': 'B06B',
            'description': 'Use the LLM-only interface to find romance novels published between 2000 and 2015 with ratings above 4.0 but fewer than 15,000 ratings.',
            'complexity': 'complex',
            'interface_type': 'llm_only',
            'task_set': 'B',
            'ground_truth': []
        },
    ]
    
    # Task Set C - Third set of unique tasks
    tasks_set_c = [
        {
            'task_id': 'B01C',
            'description': 'Find mystery or thriller books published after 2012 with page counts under 450 pages.',
            'complexity': 'simple',
            'interface_type': 'faceted',
            'task_set': 'C',
            'ground_truth': []
        },
        {
            'task_id': 'B02C',
            'description': 'Locate biography or autobiography books published before 2010 with average ratings above 3.8 and more than 8,000 ratings, sorted by ratings count.',
            'complexity': 'complex',
            'interface_type': 'faceted',
            'task_set': 'C',
            'ground_truth': []
        },
        {
            'task_id': 'B03C',
            'description': 'Using the LLM-assist interface, find poetry collections or literary fiction published between 1995 and 2010 with fewer than 300 pages.',
            'complexity': 'simple',
            'interface_type': 'llm_assist',
            'task_set': 'C',
            'ground_truth': []
        },
        {
            'task_id': 'B04C',
            'description': 'Ask the assistant for self-help or psychology books published after 2008 with ratings between 4.0 and 4.8 and more than 25,000 ratings.',
            'complexity': 'complex',
            'interface_type': 'llm_assist',
            'task_set': 'C',
            'ground_truth': []
        },
        {
            'task_id': 'B05C',
            'description': 'Request from the LLM-only interface: adventure or travel books published before 2015 with over 250 pages and at least 12,000 ratings.',
            'complexity': 'simple',
            'interface_type': 'llm_only',
            'task_set': 'C',
            'ground_truth': []
        },
        {
            'task_id': 'B06C',
            'description': 'Use the LLM-only interface to identify horror or supernatural fiction published between 2005 and 2020 with ratings above 3.9 but fewer than 20,000 ratings.',
            'complexity': 'complex',
            'interface_type': 'llm_only',
            'task_set': 'C',
            'ground_truth': []
        },
    ]
    
    # Combine all task sets
    tasks = tasks_set_a + tasks_set_b + tasks_set_c
    
    for task_data in tasks:
        # Check if task already exists for this dataset_type
        if Task.query.filter_by(task_id=task_data['task_id'], dataset_type='books').first():
            continue
        task = Task(
            task_id=task_data['task_id'],
            description=task_data['description'],
            complexity=task_data['complexity'],
            interface_type=task_data['interface_type'],
            dataset_type='books',
            task_set=task_data.get('task_set', 'A'),  # Store task set
            ground_truth=json.dumps(task_data['ground_truth'])
        )
        db.session.add(task)
    
    db.session.commit()
    print(f"Ensured {len(tasks)} book sample tasks exist (3 sets: A, B, C)")

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
        
        # Ensure sample tasks per dataset exist (idempotent)
        create_movie_tasks()
        create_book_tasks()

