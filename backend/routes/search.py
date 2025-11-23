"""
Search routes: faceted, LLM-assisted, and LLM-only search endpoints
"""
from flask import Blueprint, request, jsonify
from database import db
from models import LogEntry
from data_access import run_structured_query
from llm_integration import parse_nl_to_filters, answer_with_rag, retrieve_items_for_rag
from datetime import datetime
import json

bp = Blueprint('search', __name__, url_prefix='/api/search')

VALID_DATASETS = {'movies', 'books'}
LANGUAGE_LABELS = {
    'eng': 'English',
    'spa': 'Spanish',
    'fre': 'French',
    'ger': 'German',
    'ita': 'Italian',
    'rus': 'Russian',
    'por': 'Portuguese',
    'ara': 'Arabic',
    'chi': 'Chinese',
    'jpn': 'Japanese',
    'mul': 'Multiple',
    'en-US': 'English (US)'
}

def normalize_dataset_type(value):
    """Ensure dataset_type is one of the supported options."""
    return value if value in VALID_DATASETS else 'movies'

def log_event(participant_id, interface_type, task_id, event_type, payload):
    """Helper to log events"""
    log_entry = LogEntry(
        participant_id=participant_id,
        interface_type=interface_type,
        task_id=task_id,
        event_type=event_type,
        payload=json.dumps(payload) if payload else None
    )
    db.session.add(log_entry)
    db.session.commit()

@bp.route('/faceted', methods=['POST'])
def faceted_search():
    """Faceted search endpoint"""
    data = request.json
    participant_id = data.get('participant_id')
    task_id = data.get('task_id')
    filters = data.get('filters', {})
    sort = data.get('sort')
    dataset_type = normalize_dataset_type(data.get('dataset_type', 'movies'))
    
    # Log filter change
    log_event(participant_id, 'faceted', task_id, 'filter_change', {
        'filters': filters,
        'sort': sort,
        'dataset_type': dataset_type
    })
    
    # Execute query
    results = run_structured_query(filters=filters, sort=sort, dataset_type=dataset_type)
    
    # Log query execution
    log_event(participant_id, 'faceted', task_id, 'query_executed', {
        'result_count': len(results),
        'result_ids': [r['id'] for r in results],
        'dataset_type': dataset_type
    })
    
    return jsonify({
        'results': results,
        'count': len(results),
        'dataset_type': dataset_type
    }), 200

@bp.route('/llm_assist/parse', methods=['POST'])
def llm_assist_parse():
    """Parse NL query for LLM-assisted interface"""
    data = request.json
    participant_id = data.get('participant_id')
    task_id = data.get('task_id')
    nl_query = data.get('nl_query')
    dataset_type = normalize_dataset_type(data.get('dataset_type', 'movies'))
    
    if not nl_query:
        return jsonify({'error': 'nl_query required'}), 400
    
    # Log NL query
    log_event(participant_id, 'llm_assist', task_id, 'nl_query_sent', {
        'query': nl_query,
        'dataset_type': dataset_type
    })
    
    # Parse query
    parsed = parse_nl_to_filters(nl_query, dataset_type=dataset_type)
    
    # Log parsed preview
    log_event(participant_id, 'llm_assist', task_id, 'parsed_preview', {
        'parsed_query': parsed,
        'dataset_type': dataset_type
    })
    
    return jsonify({
        'parsed_query': parsed,
        'human_readable': format_parsed_query(parsed, dataset_type),
        'dataset_type': dataset_type
    }), 200

@bp.route('/llm_assist/execute', methods=['POST'])
def llm_assist_execute():
    """Execute parsed query for LLM-assisted interface"""
    data = request.json
    participant_id = data.get('participant_id')
    task_id = data.get('task_id')
    parsed_query = data.get('parsed_query', {})
    dataset_type = normalize_dataset_type(data.get('dataset_type', 'movies'))
    
    filters = parsed_query.get('filters', {})
    sort = parsed_query.get('sort')
    
    # Log confirmation
    log_event(participant_id, 'llm_assist', task_id, 'query_confirmed', {
        'parsed_query': parsed_query,
        'dataset_type': dataset_type
    })
    
    # Execute query
    results = run_structured_query(filters=filters, sort=sort, dataset_type=dataset_type)
    
    # Log execution
    log_event(participant_id, 'llm_assist', task_id, 'query_executed', {
        'result_count': len(results),
        'result_ids': [r['id'] for r in results],
        'dataset_type': dataset_type
    })
    
    return jsonify({
        'results': results,
        'count': len(results),
        'dataset_type': dataset_type
    }), 200

@bp.route('/llm_only', methods=['POST'])
def llm_only_search():
    """LLM-only search with RAG"""
    data = request.json
    participant_id = data.get('participant_id')
    task_id = data.get('task_id')
    nl_query = data.get('nl_query')
    dataset_type = normalize_dataset_type(data.get('dataset_type', 'movies'))
    
    if not nl_query:
        return jsonify({'error': 'nl_query required'}), 400
    
    # Log NL query
    log_event(participant_id, 'llm_only', task_id, 'nl_query_sent', {
        'query': nl_query,
        'dataset_type': dataset_type
    })
    
    # Retrieve relevant records
    retrieved_items = retrieve_items_for_rag(nl_query, run_structured_query, dataset_type=dataset_type)
    
    # Log retrieval
    log_event(participant_id, 'llm_only', task_id, 'retrieval_completed', {
        'retrieved_count': len(retrieved_items),
        'retrieved_ids': [m['id'] for m in retrieved_items],
        'dataset_type': dataset_type
    })
    
    # Generate RAG answer
    answer = answer_with_rag(nl_query, retrieved_items, dataset_type=dataset_type)
    
    # Log answer generation
    log_event(participant_id, 'llm_only', task_id, 'answer_generated', {
        'answer': answer,
        'result_count': len(retrieved_items),
        'dataset_type': dataset_type
    })
    
    return jsonify({
        'answer': answer,
        'results': retrieved_items,
        'count': len(retrieved_items),
        'dataset_type': dataset_type
    }), 200

def format_parsed_query(parsed, dataset_type='movies'):
    """Format parsed query into human-readable string"""
    parts = []
    
    filters = parsed.get('filters', {})
    if dataset_type == 'books':
        if filters.get('languages'):
            language_names = [LANGUAGE_LABELS.get(code, code) for code in filters['languages']]
            parts.append(f"Languages: {', '.join(language_names)}")
        if filters.get('author_keyword'):
            parts.append(f"Author includes '{filters['author_keyword']}'")
        if filters.get('publication_year_min'):
            parts.append(f"Publication year: {filters['publication_year_min']}+")
        if filters.get('publication_year_max'):
            parts.append(f"Publication year: ≤{filters['publication_year_max']}")
        if filters.get('num_pages_min'):
            parts.append(f"Pages: ≥{filters['num_pages_min']}")
        if filters.get('num_pages_max'):
            parts.append(f"Pages: ≤{filters['num_pages_max']}")
        if filters.get('average_rating_min'):
            parts.append(f"Average rating: ≥{filters['average_rating_min']}")
        if filters.get('average_rating_max'):
            parts.append(f"Average rating: ≤{filters['average_rating_max']}")
        if filters.get('ratings_count_min'):
            parts.append(f"Ratings count: ≥{filters['ratings_count_min']:,}")
        if filters.get('ratings_count_max'):
            parts.append(f"Ratings count: ≤{filters['ratings_count_max']:,}")
    else:
        if filters.get('genres'):
            parts.append(f"Genres: {', '.join(filters['genres'])}")
        if filters.get('lead_gender'):
            parts.append(f"Lead gender: {filters['lead_gender'].title()}")
        if filters.get('release_year_min'):
            parts.append(f"Release year: {filters['release_year_min']}+")
        if filters.get('release_year_max'):
            parts.append(f"Release year: ≤{filters['release_year_max']}")
        if filters.get('runtime_min'):
            parts.append(f"Runtime: ≥{filters['runtime_min']} min")
        if filters.get('runtime_max'):
            parts.append(f"Runtime: ≤{filters['runtime_max']} min")
        if filters.get('budget_max'):
            parts.append(f"Budget: ≤${filters['budget_max']:,.0f}")
        if filters.get('budget_min'):
            parts.append(f"Budget: ≥${filters['budget_min']:,.0f}")
        if filters.get('revenue_max'):
            parts.append(f"Revenue: ≤${filters['revenue_max']:,.0f}")
        if filters.get('revenue_min'):
            parts.append(f"Revenue: ≥${filters['revenue_min']:,.0f}")
    
    sort = parsed.get('sort', {})
    if sort.get('field'):
        direction = "descending" if sort.get('direction') == 'desc' else "ascending"
        sort_field = sort.get('field')
        parts.append(f"Sort: {sort_field} ({direction})")
    
    return "; ".join(parts) if parts else "No filters applied"

