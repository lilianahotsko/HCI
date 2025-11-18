"""
Data Access Layer: Handles structured queries on the movies dataset
"""
from database import db
from models import Movie
from sqlalchemy import and_, or_
import json

def run_structured_query(filters=None, sort=None, limit=1000):
    """
    Execute a structured query on movies table
    
    Args:
        filters: dict with keys like:
            - genres: list of genre strings
            - lead_gender: string ('female', 'male', 'mixed', 'unknown')
            - release_year_min: int
            - release_year_max: int
            - runtime_min: int
            - runtime_max: int
            - budget_min: float
            - budget_max: float
            - revenue_min: float
            - revenue_max: float
        sort: dict with 'field' and 'direction' ('asc' or 'desc')
        limit: max number of results
    
    Returns:
        list of Movie dicts
    """
    query = Movie.query
    
    if filters:
        # Genre filter (genres stored as JSON array string)
        if 'genres' in filters and filters['genres']:
            genre_conditions = []
            for genre in filters['genres']:
                genre_conditions.append(Movie.genres.contains(f'"{genre}"'))
            if genre_conditions:
                query = query.filter(or_(*genre_conditions))
        
        # Lead gender filter
        if 'lead_gender' in filters and filters['lead_gender']:
            query = query.filter(Movie.lead_gender == filters['lead_gender'])
        
        # Release year filters
        if 'release_year_min' in filters and filters['release_year_min']:
            query = query.filter(Movie.release_year >= filters['release_year_min'])
        if 'release_year_max' in filters and filters['release_year_max']:
            query = query.filter(Movie.release_year <= filters['release_year_max'])
        
        # Runtime filters
        if 'runtime_min' in filters and filters['runtime_min']:
            query = query.filter(Movie.runtime >= filters['runtime_min'])
        if 'runtime_max' in filters and filters['runtime_max']:
            query = query.filter(Movie.runtime <= filters['runtime_max'])
        
        # Budget filters
        if 'budget_min' in filters and filters['budget_min']:
            query = query.filter(Movie.budget >= filters['budget_min'])
        if 'budget_max' in filters and filters['budget_max']:
            query = query.filter(Movie.budget <= filters['budget_max'])
        
        # Revenue filters
        if 'revenue_min' in filters and filters['revenue_min']:
            query = query.filter(Movie.revenue >= filters['revenue_min'])
        if 'revenue_max' in filters and filters['revenue_max']:
            query = query.filter(Movie.revenue <= filters['revenue_max'])
    
    # Sorting
    if sort:
        field = sort.get('field')
        direction = sort.get('direction', 'asc')
        
        if field == 'release_year':
            order_field = Movie.release_year
        elif field == 'runtime':
            order_field = Movie.runtime
        elif field == 'budget':
            order_field = Movie.budget
        elif field == 'revenue':
            order_field = Movie.revenue
        elif field == 'title':
            order_field = Movie.title
        else:
            order_field = Movie.id
        
        if direction == 'desc':
            query = query.order_by(order_field.desc())
        else:
            query = query.order_by(order_field.asc())
    else:
        query = query.order_by(Movie.id)
    
    # Limit results
    movies = query.limit(limit).all()
    return [movie.to_dict() for movie in movies]

def get_movie_by_id(movie_id):
    """Get a single movie by ID"""
    movie = Movie.query.get(movie_id)
    return movie.to_dict() if movie else None

def get_movies_by_ids(movie_ids):
    """Get multiple movies by their IDs"""
    movies = Movie.query.filter(Movie.id.in_(movie_ids)).all()
    return [movie.to_dict() for movie in movies]

def get_all_genres():
    """Get all unique genres from the database"""
    movies = Movie.query.all()
    genres_set = set()
    for movie in movies:
        if movie.genres:
            try:
                genres = json.loads(movie.genres)
                genres_set.update(genres)
            except:
                pass
    return sorted(list(genres_set))

def get_statistics():
    """Get dataset statistics"""
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

