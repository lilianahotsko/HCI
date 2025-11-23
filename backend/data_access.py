"""
Data Access Layer: Handles structured queries on the movies dataset
"""
from database import db
from models import Movie, Book
from sqlalchemy import and_, or_
import json

def run_structured_query(filters=None, sort=None, limit=1000, dataset_type='movies'):
    """
    Execute a structured query on the selected dataset.
    """
    if dataset_type == 'books':
        return _run_books_query(filters or {}, sort, limit)
    return _run_movies_query(filters or {}, sort, limit)

def _run_movies_query(filters, sort, limit):
    query = Movie.query
    
    # Genre filter (genres stored as JSON array string)
    genres = filters.get('genres')
    if genres:
        genre_conditions = [Movie.genres.contains(f'"{genre}"') for genre in genres]
        if genre_conditions:
            query = query.filter(or_(*genre_conditions))
    
    # Lead gender filter
    if filters.get('lead_gender'):
        query = query.filter(Movie.lead_gender == filters['lead_gender'])
    
    # Release year filters
    if filters.get('release_year_min'):
        query = query.filter(Movie.release_year >= filters['release_year_min'])
    if filters.get('release_year_max'):
        query = query.filter(Movie.release_year <= filters['release_year_max'])
    
    # Runtime filters
    if filters.get('runtime_min'):
        query = query.filter(Movie.runtime >= filters['runtime_min'])
    if filters.get('runtime_max'):
        query = query.filter(Movie.runtime <= filters['runtime_max'])
    
    # Budget filters
    if filters.get('budget_min'):
        query = query.filter(Movie.budget >= filters['budget_min'])
    if filters.get('budget_max'):
        query = query.filter(Movie.budget <= filters['budget_max'])
    
    # Revenue filters
    if filters.get('revenue_min'):
        query = query.filter(Movie.revenue >= filters['revenue_min'])
    if filters.get('revenue_max'):
        query = query.filter(Movie.revenue <= filters['revenue_max'])
    
    query = _apply_movie_sort(query, sort)
    movies = query.limit(limit).all()
    return [movie.to_dict() for movie in movies]

def _run_books_query(filters, sort, limit):
    query = Book.query
    
    languages = filters.get('languages')
    if languages:
        query = query.filter(Book.language.in_(languages))
    
    author_keyword = filters.get('author_keyword')
    if author_keyword:
        query = query.filter(Book.authors.ilike(f"%{author_keyword}%"))
    
    if filters.get('publication_year_min'):
        query = query.filter(Book.publication_year >= filters['publication_year_min'])
    if filters.get('publication_year_max'):
        query = query.filter(Book.publication_year <= filters['publication_year_max'])
    
    if filters.get('num_pages_min'):
        query = query.filter(Book.num_pages >= filters['num_pages_min'])
    if filters.get('num_pages_max'):
        query = query.filter(Book.num_pages <= filters['num_pages_max'])
    
    if filters.get('average_rating_min'):
        query = query.filter(Book.average_rating >= filters['average_rating_min'])
    if filters.get('average_rating_max'):
        query = query.filter(Book.average_rating <= filters['average_rating_max'])
    
    if filters.get('ratings_count_min'):
        query = query.filter(Book.ratings_count >= filters['ratings_count_min'])
    if filters.get('ratings_count_max'):
        query = query.filter(Book.ratings_count <= filters['ratings_count_max'])
    
    query = _apply_book_sort(query, sort)
    books = query.limit(limit).all()
    return [book.to_dict() for book in books]

def _apply_movie_sort(query, sort):
    if not sort:
        return query.order_by(Movie.id)
    
    field = sort.get('field')
    direction = sort.get('direction', 'asc')
    
    field_map = {
        'release_year': Movie.release_year,
        'runtime': Movie.runtime,
        'budget': Movie.budget,
        'revenue': Movie.revenue,
        'title': Movie.title
    }
    order_field = field_map.get(field, Movie.id)
    return query.order_by(order_field.desc() if direction == 'desc' else order_field.asc())

def _apply_book_sort(query, sort):
    if not sort:
        return query.order_by(Book.id)
    
    field = sort.get('field')
    direction = sort.get('direction', 'asc')
    
    field_map = {
        'publication_year': Book.publication_year,
        'num_pages': Book.num_pages,
        'average_rating': Book.average_rating,
        'ratings_count': Book.ratings_count,
        'title': Book.title
    }
    order_field = field_map.get(field, Book.id)
    return query.order_by(order_field.desc() if direction == 'desc' else order_field.asc())

def get_movie_by_id(movie_id):
    """Get a single movie by ID"""
    movie = Movie.query.get(movie_id)
    return movie.to_dict() if movie else None

def get_movies_by_ids(movie_ids):
    """Get multiple movies by their IDs"""
    movies = Movie.query.filter(Movie.id.in_(movie_ids)).all()
    return [movie.to_dict() for movie in movies]

def get_all_genres(dataset_type='movies'):
    """Get facet values (genres for movies, languages for books)."""
    if dataset_type == 'books':
        languages = (
            db.session.query(Book.language)
            .filter(Book.language.isnot(None))
            .distinct()
            .all()
        )
        return sorted([lang[0] for lang in languages if lang[0]])
    
    movies = Movie.query.all()
    genres_set = set()
    for movie in movies:
        if movie.genres:
            try:
                genres = json.loads(movie.genres)
                genres_set.update(genres)
            except Exception:
                pass
    return sorted(list(genres_set))

def get_statistics(dataset_type='movies'):
    """Get dataset statistics"""
    if dataset_type == 'books':
        total_books = Book.query.count()
        books_with_year = Book.query.filter(Book.publication_year.isnot(None)).count()
        books_with_pages = Book.query.filter(Book.num_pages.isnot(None)).count()
        books_with_rating = Book.query.filter(Book.average_rating.isnot(None)).count()
        return {
            'total_books': total_books,
            'books_with_year': books_with_year,
            'books_with_pages': books_with_pages,
            'books_with_rating': books_with_rating
        }
    
    total_movies = Movie.query.count()
    movies_with_year = Movie.query.filter(Movie.release_year.isnot(None)).count()
    movies_with_runtime = Movie.query.filter(Movie.runtime.isnot(None)).count()
    movies_with_budget = Movie.query.filter(Movie.budget.isnot(None)).count()
    movies_with_revenue = Movie.query.filter(Movie.revenue.isnot(None)).count()
    
    return {
        'total_movies': total_movies,
        'movies_with_year': movies_with_year,
        'movies_with_runtime': movies_with_runtime,
        'movies_with_budget': movies_with_budget,
        'movies_with_revenue': movies_with_revenue
    }

