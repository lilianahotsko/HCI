"""
Database initialization script for deployment.
Run this after deploying to initialize the database.
"""
from app import app
from database import db
from preprocess_data import create_movie_tasks, create_book_tasks, load_movies_from_csv, load_books_from_csv
import os

def init_database():
    """Initialize database with schema, data, and tasks"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("\nLoading movies...")
        from models import Movie
        if Movie.query.count() == 0:
            csv_path = os.getenv('TMDB_CSV_PATH', 'tmdb_5000_movies.csv')
            if os.path.exists(csv_path):
                load_movies_from_csv(csv_path)
            else:
                print(f"⚠️  Movies CSV not found at {csv_path}")
                print("   Set TMDB_CSV_PATH environment variable or upload CSV file")
        else:
            print(f"Movies already loaded ({Movie.query.count()} movies)")
        
        print("\nLoading books...")
        from models import Book
        if Book.query.count() == 0:
            books_csv_path = os.getenv('BOOKS_CSV_PATH', 'books.csv')
            if os.path.exists(books_csv_path):
                load_books_from_csv(books_csv_path)
            else:
                print(f"⚠️  Books CSV not found at {books_csv_path}")
                print("   Set BOOKS_CSV_PATH environment variable or upload CSV file")
        else:
            print(f"Books already loaded ({Book.query.count()} books)")
        
        print("\nCreating tasks...")
        create_movie_tasks()
        create_book_tasks()
        
        print("\n✅ Database initialization complete!")
        print("\nNext step: Run 'python generate_ground_truth.py' to generate ground truth answers")

if __name__ == '__main__':
    init_database()

