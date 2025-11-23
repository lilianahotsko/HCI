"""
LLM Integration Layer: Handles LLM calls for parsing NL queries and RAG-based answering
"""
import os
import json
import re

# Lazy initialization of OpenAI client
_client = None

def get_client():
    """Get or create OpenAI client (lazy initialization)"""
    global _client
    if _client is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        try:
            from openai import OpenAI
            _client = OpenAI(api_key=api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {e}")
    return _client

MOVIE_SCHEMA = """
The movies dataset has the following fields:
- title: string
- release_year: integer (year)
- runtime: integer (minutes)
- genres: array of strings (e.g., ["Drama", "Thriller", "Action"])
- lead_gender: string ("female", "male", "mixed", "unknown")
- budget: float (in dollars)
- revenue: float (in dollars)
- language: string
- overview: text description
"""

BOOK_SCHEMA = """
The books dataset has the following fields:
- title: string
- authors: string containing one or more authors separated by '/'
- publication_year: integer year (if known)
- num_pages: integer number of pages
- average_rating: float score between 0 and 5
- ratings_count: integer number of user ratings
- text_reviews_count: integer number of text reviews
- language: string language code (e.g., 'eng', 'spa', 'fre')
- publisher: string
"""

def parse_nl_to_filters(nl_query, dataset_type='movies', schema_metadata=None):
    """
    Parse a natural language query into structured filters and sort options
    
    Args:
        nl_query: natural language query string
        schema_metadata: optional schema description
    
    Returns:
        dict with 'filters' and 'sort' keys
    """
    schema = schema_metadata or (MOVIE_SCHEMA if dataset_type == 'movies' else BOOK_SCHEMA)
    
    if dataset_type == 'books':
        filter_block = """
{
    "filters": {
        "languages": ["list", "of", "language codes"] or null,
        "author_keyword": "string" or null,
        "publication_year_min": integer or null,
        "publication_year_max": integer or null,
        "num_pages_min": integer or null,
        "num_pages_max": integer or null,
        "average_rating_min": float or null,
        "average_rating_max": float or null,
        "ratings_count_min": integer or null,
        "ratings_count_max": integer or null
    },
    "sort": {
        "field": "publication_year" | "num_pages" | "average_rating" | "ratings_count" | "title" or null,
        "direction": "asc" | "desc" or null
    }
}
"""
        rules = """
- Only include filters explicitly mentioned in the query
- For languages, extract references to languages (e.g., "English books" -> ["eng"])
- For authors, capture key phrases like author names ("books by Stephen King" -> author_keyword: "Stephen King")
- Convert phrases like "after 2010" to publication_year_min: 2011
- Convert "under 400 pages" to num_pages_max: 399
- Convert rating/rating-count qualifiers to the appropriate filters
- Return null for fields that are not mentioned
"""
    else:
        filter_block = """
{
    "filters": {
        "genres": ["list", "of", "genres"] or null,
        "lead_gender": "female" | "male" | "mixed" | "unknown" or null,
        "release_year_min": integer or null,
        "release_year_max": integer or null,
        "runtime_min": integer or null,
        "runtime_max": integer or null,
        "budget_min": float or null,
        "budget_max": float or null,
        "revenue_min": float or null,
        "revenue_max": float or null
    },
    "sort": {
        "field": "release_year" | "runtime" | "budget" | "revenue" | "title" or null,
        "direction": "asc" | "desc" or null
    }
}
"""
        rules = """
- Only include filters that are explicitly mentioned in the query
- For genres, extract all mentioned genres (e.g., "dramas or thrillers" -> ["Drama", "Thriller"])
- For years, extract ranges (e.g., "after 2015" -> release_year_min: 2016, "before 2020" -> release_year_max: 2019)
- For runtime, convert to minutes (e.g., "under 100 minutes" -> runtime_max: 99)
- For budget/revenue, convert to numbers (e.g., "under $10M" -> budget_max: 10000000)
- For sorting, detect phrases like "sort by", "order by", "highest", "lowest"
- Return null for fields not mentioned
"""
    
    prompt = f"""You are a query parser for a {dataset_type} database. Convert the following natural language query into structured filters and sorting options.

{schema}

User query: "{nl_query}"

Parse this query and return ONLY a valid JSON object with this exact structure:
{filter_block}

Rules:
{rules}

Return ONLY the JSON object, no other text."""

    try:
        client = get_client()
        model = os.getenv('OPENAI_MODEL', 'gpt-4')
        
        messages = [
            {"role": "system", "content": "You are a precise query parser. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        # Try with temperature=0 first (for deterministic parsing)
        # If the model doesn't support it, retry without temperature parameter
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
                top_p=1
            )
        except Exception as temp_error:
            # If temperature=0 is not supported, retry without temperature
            if "temperature" in str(temp_error).lower() or "unsupported" in str(temp_error).lower():
                print(f"Model {model} doesn't support temperature=0, using default temperature")
                response = client.chat.completions.create(
                    model=model,
                    messages=messages
                )
            else:
                raise  # Re-raise if it's a different error
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON from response (in case LLM adds extra text)
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            content = json_match.group(0)
        
        parsed = json.loads(content)
        
        # Clean up: remove null values from filters
        if 'filters' in parsed:
            parsed['filters'] = {k: v for k, v in parsed['filters'].items() if v is not None and v != []}
        if 'sort' in parsed:
            parsed['sort'] = {k: v for k, v in parsed['sort'].items() if v is not None}
        
        return parsed
        
    except Exception as e:
        print(f"Error parsing NL query: {e}")
        return {
            'filters': {},
            'sort': {}
        }

def answer_with_rag(nl_query, retrieved_rows, dataset_type='movies'):
    """
    Generate a natural language answer using RAG on retrieved movie rows
    
    Args:
        nl_query: original natural language query
        retrieved_rows: list of movie dicts
    
    Returns:
        string: natural language answer
    """
    # Format retrieved rows as a table
    if dataset_type == 'books':
        header = "ID | Title | Authors | Year | Pages | Avg Rating | Language | Ratings Count\n"
    else:
        header = "ID | Title | Year | Runtime | Genres | Lead Gender | Budget | Revenue\n"
    table_text = header + "-" * 120 + "\n"
    
    for row in retrieved_rows[:50]:  # Limit to 50 rows for context
        if dataset_type == 'books':
            authors = ", ".join(row.get('authors', []))
            avg_rating_value = row.get('average_rating')
            avg_rating = f"{avg_rating_value:.2f}" if isinstance(avg_rating_value, (int, float)) else "N/A"
            ratings_count_value = row.get('ratings_count')
            ratings_count = f"{ratings_count_value:,}" if isinstance(ratings_count_value, (int, float)) else "N/A"
            table_text += f"{row.get('id')} | {row.get('title', 'N/A')} | {authors or 'N/A'} | {row.get('publication_year', 'N/A')} | {row.get('num_pages', 'N/A')} | {avg_rating} | {row.get('language', 'N/A')} | {ratings_count}\n"
        else:
            genres_str = ", ".join(row.get('genres', []))
            budget_str = f"${row.get('budget', 0):,.0f}" if row.get('budget') else "N/A"
            revenue_str = f"${row.get('revenue', 0):,.0f}" if row.get('revenue') else "N/A"
            table_text += f"{row.get('id')} | {row.get('title', 'N/A')} | {row.get('release_year', 'N/A')} | {row.get('runtime', 'N/A')} min | {genres_str} | {row.get('lead_gender', 'N/A')} | {budget_str} | {revenue_str}\n"
    
    prompt = f"""You are a helpful assistant answering questions about {dataset_type} from a database.

User question: "{nl_query}"

Here are the relevant records from the database:

{table_text}

Based on this data, provide a clear, concise answer to the user's question. Format your response as:
1. A brief summary statement (e.g., "I found X movies matching your criteria:")
2. A list of the results with key details (title plus the most relevant numeric attributes)
3. If sorting was requested, mention how they are ordered

Be specific and accurate. Only mention records that are actually in the table above."""

    try:
        client = get_client()
        model = os.getenv('OPENAI_MODEL', 'gpt-4')
        
        messages = [
            {"role": "system", "content": "You are a helpful movie database assistant. Provide clear, accurate answers based on the provided data."},
            {"role": "user", "content": prompt}
        ]
        
        # Try with temperature=0 first (for deterministic answers)
        # If the model doesn't support it, retry without temperature parameter
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
                top_p=1
            )
        except Exception as temp_error:
            # If temperature=0 is not supported, retry without temperature
            if "temperature" in str(temp_error).lower() or "unsupported" in str(temp_error).lower():
                print(f"Model {model} doesn't support temperature=0, using default temperature")
                response = client.chat.completions.create(
                    model=model,
                    messages=messages
                )
            else:
                raise  # Re-raise if it's a different error
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error generating RAG answer: {e}")
        noun = "movies" if dataset_type == 'movies' else "books"
        return f"I found {len(retrieved_rows)} {noun} matching your criteria. Please review the results below."

def retrieve_items_for_rag(nl_query, query_function, dataset_type='movies'):
    """
    Simple rule-based retrieval for RAG (can be enhanced with embeddings later)
    
    Args:
        nl_query: natural language query
        query_function: function to execute structured queries (run_structured_query)
    
    Returns:
        list of movie dicts
    """
    parsed = parse_nl_to_filters(nl_query, dataset_type=dataset_type)
    
    items = query_function(
        filters=parsed.get('filters', {}),
        sort=parsed.get('sort'),
        limit=100,
        dataset_type=dataset_type
    )
    
    return items

