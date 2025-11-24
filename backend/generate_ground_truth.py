"""
Generate ground truth answers for all tasks by parsing task descriptions
and executing queries to find matching results.
"""
import json
import re
from app import app
from database import db
from models import Task, Movie, Book
from data_access import run_structured_query
from llm_integration import parse_nl_to_filters

def parse_task_description_to_filters(task_description, dataset_type='movies'):
    """
    Parse task description to extract filters by running the correct query.
    Uses LLM parsing to ensure accurate filter extraction from natural language.
    """
    # Clean up the description - remove interface-specific instructions
    description = task_description
    
    # Remove interface-specific prefixes (case-insensitive)
    prefixes_to_remove = [
        'use the llm-assist interface to ',
        'use the llm-only interface to ',
        'ask the llm-assist interface for ',
        'ask the llm-only interface for ',
        'ask the assistant for ',
        'using natural language, ',
        'using the llm-assist interface, ',
        'using the llm-only interface, ',
        'find all ',
        'find ',
        'locate ',
        'surface ',
        'retrieve ',
        'identify ',
        'recommend ',
    ]
    
    cleaned_description = description.lower()
    for prefix in prefixes_to_remove:
        if cleaned_description.startswith(prefix.lower()):
            cleaned_description = cleaned_description[len(prefix):].strip()
            break
    
    # Use LLM to parse the query - this ensures we get the correct filters
    # The LLM parsing uses the same logic as the actual interface
    try:
        parsed = parse_nl_to_filters(cleaned_description, dataset_type=dataset_type)
        filters = parsed.get('filters', {})
        sort = parsed.get('sort', None)
        
        # Validate that we got some filters
        if filters:
            return filters, sort
        else:
            print(f"  Warning: LLM parsing returned empty filters")
            return {}, None
            
    except Exception as e:
        print(f"  Error: LLM parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return {}, None

def extract_filters_from_description(task_description, dataset_type='movies'):
    """
    Extract filters from task description using pattern matching.
    This is a fallback if LLM parsing fails.
    """
    filters = {}
    description = task_description.lower()
    
    if dataset_type == 'movies':
        # Extract genres
        genre_patterns = {
            'drama': 'Drama',
            'thriller': 'Thriller',
            'comedy': 'Comedy',
            'action': 'Action',
            'adventure': 'Adventure',
            'science fiction': 'Science Fiction',
            'sci-fi': 'Science Fiction',
            'mystery': 'Mystery',
            'crime': 'Crime',
            'horror': 'Horror',
            'romantic comedy': 'Romance',
            'romance': 'Romance',
            'animated': 'Animation',
            'animation': 'Animation',
            'family': 'Family',
            'documentary': 'Documentary',
            'war': 'War',
            'history': 'History',
            'biographical': 'Biography',
            'biography': 'Biography',
            'musical': 'Music',
            'music': 'Music',
            'western': 'Western',
        }
        
        genres_found = []
        for pattern, genre in genre_patterns.items():
            if pattern in description:
                genres_found.append(genre)
        if genres_found:
            filters['genres'] = genres_found
        
        # Extract lead gender
        if 'female lead' in description or 'female-led' in description:
            filters['lead_gender'] = 'female'
        elif 'male lead' in description or 'male-led' in description:
            filters['lead_gender'] = 'male'
        elif 'mixed-gender' in description or 'mixed gender' in description:
            filters['lead_gender'] = 'mixed'
        
        # Extract release year
        year_patterns = [
            (r'released after (\d{4})', 'release_year_min'),
            (r'released before (\d{4})', 'release_year_max'),
            (r'released between (\d{4}) and (\d{4})', 'release_year_range'),
            (r'from (\d{4})', 'release_year_min'),
            (r'(\d{4})s', 'release_year_decade'),
        ]
        
        for pattern, filter_type in year_patterns:
            match = re.search(pattern, description)
            if match:
                if filter_type == 'release_year_min':
                    filters['release_year_min'] = int(match.group(1)) + 1
                elif filter_type == 'release_year_max':
                    filters['release_year_max'] = int(match.group(1)) - 1
                elif filter_type == 'release_year_range':
                    filters['release_year_min'] = int(match.group(1))
                    filters['release_year_max'] = int(match.group(2))
        
        # Extract runtime
        runtime_patterns = [
            (r'runtime under (\d+)', 'runtime_max'),
            (r'runtime over (\d+)', 'runtime_min'),
            (r'runtime between (\d+) and (\d+)', 'runtime_range'),
            (r'under (\d+) minutes', 'runtime_max'),
            (r'over (\d+) minutes', 'runtime_min'),
        ]
        
        for pattern, filter_type in runtime_patterns:
            match = re.search(pattern, description)
            if match:
                if filter_type == 'runtime_max':
                    filters['runtime_max'] = int(match.group(1))
                elif filter_type == 'runtime_min':
                    filters['runtime_min'] = int(match.group(1))
        
        # Extract budget
        budget_patterns = [
            (r'budget under \$(\d+)M', 'budget_max'),
            (r'budget over \$(\d+)M', 'budget_min'),
            (r'budget between \$(\d+)M and \$(\d+)M', 'budget_range'),
            (r'budget below \$(\d+)M', 'budget_max'),
            (r'budget above \$(\d+)M', 'budget_min'),
        ]
        
        for pattern, filter_type in budget_patterns:
            match = re.search(pattern, description)
            if match:
                if filter_type == 'budget_max':
                    filters['budget_max'] = int(match.group(1)) * 1000000
                elif filter_type == 'budget_min':
                    filters['budget_min'] = int(match.group(1)) * 1000000
        
        # Extract revenue
        revenue_patterns = [
            (r'revenue over \$(\d+)M', 'revenue_min'),
            (r'revenue above \$(\d+)M', 'revenue_min'),
            (r'revenues over \$(\d+)M', 'revenue_min'),
            (r'revenues above \$(\d+)M', 'revenue_min'),
            (r'revenue below \$(\d+)M', 'revenue_max'),
            (r'revenues below \$(\d+)M', 'revenue_max'),
        ]
        
        for pattern, filter_type in revenue_patterns:
            match = re.search(pattern, description)
            if match:
                if filter_type == 'revenue_min':
                    filters['revenue_min'] = int(match.group(1)) * 1000000
                elif filter_type == 'revenue_max':
                    filters['revenue_max'] = int(match.group(1)) * 1000000
        
        # Extract language
        if 'non-english' in description or 'non english' in description:
            # This would need special handling - exclude English
            pass
    
    elif dataset_type == 'books':
        # Extract language
        if 'english-language' in description or 'english language' in description:
            filters['languages'] = ['eng']
        elif 'non-english' in description or 'non english' in description:
            # Would need to exclude English - for now, skip
            pass
        
        # Extract publication year
        year_patterns = [
            (r'published after (\d{4})', 'publication_year_min'),
            (r'published before (\d{4})', 'publication_year_max'),
            (r'published between (\d{4}) and (\d{4})', 'publication_year_range'),
        ]
        
        for pattern, filter_type in year_patterns:
            match = re.search(pattern, description)
            if match:
                if filter_type == 'publication_year_min':
                    filters['publication_year_min'] = int(match.group(1)) + 1
                elif filter_type == 'publication_year_max':
                    filters['publication_year_max'] = int(match.group(1)) - 1
                elif filter_type == 'publication_year_range':
                    filters['publication_year_min'] = int(match.group(1))
                    filters['publication_year_max'] = int(match.group(2))
        
        # Extract pages
        page_patterns = [
            (r'fewer than (\d+) pages', 'num_pages_max'),
            (r'under (\d+) pages', 'num_pages_max'),
            (r'over (\d+) pages', 'num_pages_min'),
            (r'more than (\d+) pages', 'num_pages_min'),
            (r'between (\d+) and (\d+) pages', 'num_pages_range'),
        ]
        
        for pattern, filter_type in page_patterns:
            match = re.search(pattern, description)
            if match:
                if filter_type == 'num_pages_max':
                    filters['num_pages_max'] = int(match.group(1)) - 1
                elif filter_type == 'num_pages_min':
                    filters['num_pages_min'] = int(match.group(1)) + 1
        
        # Extract rating
        rating_patterns = [
            (r'average rating above ([\d.]+)', 'average_rating_min'),
            (r'average rating over ([\d.]+)', 'average_rating_min'),
            (r'at least ([\d.]+) average rating', 'average_rating_min'),
            (r'rating above ([\d.]+)', 'average_rating_min'),
        ]
        
        for pattern, filter_type in rating_patterns:
            match = re.search(pattern, description)
            if match:
                filters['average_rating_min'] = float(match.group(1))
        
        # Extract ratings count
        ratings_count_patterns = [
            (r'more than ([\d,]+) ratings', 'ratings_count_min'),
            (r'over ([\d,]+) ratings', 'ratings_count_min'),
            (r'at least ([\d,]+) ratings', 'ratings_count_min'),
        ]
        
        for pattern, filter_type in ratings_count_patterns:
            match = re.search(pattern, description)
            if match:
                count_str = match.group(1).replace(',', '')
                filters['ratings_count_min'] = int(count_str)
    
    return filters, None

def generate_ground_truth_for_task(task):
    """
    Generate ground truth for a single task by parsing its description
    and executing the CORRECT query that matches the task requirements.
    
    This uses the same LLM parsing logic as the actual interfaces to ensure
    the ground truth query matches what users would execute.
    """
    print(f"\nProcessing task: {task.task_id}")
    print(f"  Description: {task.description}")
    print(f"  Dataset: {task.dataset_type}, Interface: {task.interface_type}")
    
    # Parse task description using LLM (same as actual interface)
    filters, sort = parse_task_description_to_filters(task.description, task.dataset_type)
    
    # Fallback to pattern matching if LLM fails
    if not filters or len(filters) == 0:
        print("  ⚠️  LLM parsing returned no filters, trying pattern matching fallback...")
        filters, sort = extract_filters_from_description(task.description, task.dataset_type)
    
    if not filters:
        print("  ✗ ERROR: Could not extract filters from description")
        print("  Task description may be unclear or unsupported")
        return []
    
    print(f"  Extracted filters: {json.dumps(filters, indent=4)}")
    if sort:
        print(f"  Sort: {sort}")
    
    # Execute the CORRECT query using the EXACT same query function as the interface
    # This ensures ground truth matches what users would actually get when they use the interface
    try:
        # Use the same run_structured_query function that the interfaces use
        # This guarantees the query logic is identical
        results = run_structured_query(
            filters=filters, 
            sort=sort, 
            limit=10000,  # High limit to get all matching results (ground truth should be complete)
            dataset_type=task.dataset_type
        )
        result_ids = [r['id'] for r in results]
        
        print(f"  ✓ Query executed successfully using run_structured_query()")
        print(f"  ✓ Found {len(result_ids)} matching results (ground truth)")
        
        # Show sample results for verification
        if result_ids:
            if len(result_ids) <= 10:
                print(f"  All result IDs: {result_ids}")
            else:
                print(f"  Sample IDs (first 5): {result_ids[:5]}")
                print(f"  ... and {len(result_ids) - 5} more")
        else:
            print(f"  ⚠️  WARNING: No results found!")
            print(f"     This could mean:")
            print(f"     - Task filters are too restrictive")
            print(f"     - Data doesn't match the criteria")
            print(f"     - Query parsing may need adjustment")
        
        return result_ids
        
    except Exception as e:
        print(f"  ✗ ERROR executing query: {e}")
        print(f"     This indicates a problem with the query execution")
        import traceback
        traceback.print_exc()
        return None  # Return None to indicate error (vs [] which means no results)

def generate_all_ground_truth():
    """
    Generate ground truth for all tasks by running the CORRECT queries.
    Uses the same query logic as the actual interfaces to ensure accuracy.
    """
    with app.app_context():
        tasks = Task.query.order_by(Task.task_id).all()
        print(f"\n{'='*80}")
        print(f"GROUND TRUTH GENERATION")
        print(f"{'='*80}")
        print(f"\nFound {len(tasks)} tasks to process")
        print(f"This will run the CORRECT queries for each task to generate ground truth.\n")
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        empty_results_count = 0
        
        for task in tasks:
            # Skip if ground truth already exists (unless force mode)
            existing_gt = json.loads(task.ground_truth) if task.ground_truth else []
            if existing_gt:
                print(f"\n⏭️  Skipping {task.task_id} - ground truth already exists ({len(existing_gt)} results)")
                skipped_count += 1
                continue
            
            # Generate ground truth by running the CORRECT query
            # This uses the same query logic as the actual interfaces
            ground_truth_ids = generate_ground_truth_for_task(task)
            
            if ground_truth_ids is None:
                # None means error occurred during query execution
                error_count += 1
                print(f"  ✗ Failed to generate ground truth for {task.task_id}")
            elif len(ground_truth_ids) > 0:
                # Successfully found results
                task.ground_truth = json.dumps(ground_truth_ids)
                db.session.add(task)
                updated_count += 1
            else:
                # Empty list means query ran successfully but found no results
                task.ground_truth = json.dumps([])
                db.session.add(task)
                empty_results_count += 1
                print(f"  ⚠️  WARNING: Task {task.task_id} has 0 matching results")
        
        # Commit all updates
        db.session.commit()
        
        print("\n" + "=" * 80)
        print(f"\nSUMMARY:")
        print(f"  ✓ Successfully updated: {updated_count} tasks")
        print(f"  ⏭️  Skipped (already had GT): {skipped_count} tasks")
        print(f"  ⚠️  Empty results (0 matches): {empty_results_count} tasks")
        print(f"  ✗ Errors: {error_count} tasks")
        print(f"  Total processed: {len(tasks)} tasks")
        
        # Print detailed statistics
        print("\n" + "=" * 80)
        print("GROUND TRUTH STATISTICS BY TASK:")
        print("=" * 80)
        
        tasks_with_gt = Task.query.filter(Task.ground_truth.isnot(None)).order_by(Task.task_id).all()
        
        # Group by dataset and interface
        stats_by_type = {}
        for task in tasks_with_gt:
            gt = json.loads(task.ground_truth) if task.ground_truth else []
            key = f"{task.dataset_type}_{task.interface_type}"
            if key not in stats_by_type:
                stats_by_type[key] = []
            stats_by_type[key].append(len(gt))
        
        # Print per task
        for task in tasks_with_gt:
            gt = json.loads(task.ground_truth) if task.ground_truth else []
            status = "✓" if len(gt) > 0 else "⚠️"
            print(f"  {status} {task.task_id:8s} ({task.dataset_type:6s}, {task.interface_type:12s}): {len(gt):4d} results")
        
        # Print summary by type
        print("\n" + "=" * 80)
        print("AVERAGE RESULTS BY DATASET AND INTERFACE:")
        print("=" * 80)
        for key, counts in sorted(stats_by_type.items()):
            dataset, interface = key.split('_')
            avg = sum(counts) / len(counts) if counts else 0
            print(f"  {dataset:6s} - {interface:12s}: {avg:6.1f} results (from {len(counts)} tasks)")
        
        print("\n" + "=" * 80)
        print("✓ Ground truth generation complete!")
        print("=" * 80)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        # Force regenerate all ground truth
        print("Force mode: Regenerating all ground truth...")
        with app.app_context():
            tasks = Task.query.all()
            for task in tasks:
                task.ground_truth = None
            db.session.commit()
    
    generate_all_ground_truth()

