"""
Fix old tasks that don't have proper task_set values.
Old tasks (T01-T06, B01-B06) should be deleted or updated.
"""
from app import app
from database import db
from models import Task

def fix_old_tasks():
    """
    Remove or update old tasks that don't have proper task_set values.
    Old task IDs: T01-T06 (movies), B01-B06 (books)
    New task IDs: T01A-T06A, T01B-T06B, T01C-T06C (movies)
                  B01A-B06A, B01B-B06B, B01C-B06C (books)
    """
    with app.app_context():
        # Find old tasks (without A/B/C suffix)
        # Old tasks: T01-T06, B01-B06 (no letter suffix)
        # New tasks: T01A-T06A, T01B-T06B, T01C-T06C, B01A-B06A, etc.
        from sqlalchemy import or_
        
        # Get all movie tasks
        all_movie_tasks = Task.query.filter(Task.dataset_type == 'movies').all()
        # Filter out ones ending in A, B, or C
        old_movie_tasks = [t for t in all_movie_tasks if not (t.task_id.endswith('A') or t.task_id.endswith('B') or t.task_id.endswith('C'))]
        
        # Get all book tasks
        all_book_tasks = Task.query.filter(Task.dataset_type == 'books').all()
        # Filter out ones ending in A, B, or C
        old_book_tasks = [t for t in all_book_tasks if not (t.task_id.endswith('A') or t.task_id.endswith('B') or t.task_id.endswith('C'))]
        
        print(f"Found {len(old_movie_tasks)} old movie tasks")
        print(f"Found {len(old_book_tasks)} old book tasks")
        
        if old_movie_tasks:
            print("\nOld movie tasks to remove:")
            for task in old_movie_tasks:
                print(f"  - {task.task_id}: {task.description[:60]}...")
        
        if old_book_tasks:
            print("\nOld book tasks to remove:")
            for task in old_book_tasks:
                print(f"  - {task.task_id}: {task.description[:60]}...")
        
        # Also check for tasks with NULL or incorrect task_set
        tasks_without_set = Task.query.filter(
            (Task.task_set.is_(None)) | (Task.task_set == '')
        ).all()
        
        print(f"\nFound {len(tasks_without_set)} tasks without task_set value")
        
        if tasks_without_set:
            print("Tasks without task_set:")
            for task in tasks_without_set:
                print(f"  - {task.task_id} ({task.dataset_type}, {task.interface_type})")
        
        # Delete old tasks
        total_deleted = 0
        if old_movie_tasks:
            for task in old_movie_tasks:
                db.session.delete(task)
                total_deleted += 1
        
        if old_book_tasks:
            for task in old_book_tasks:
                db.session.delete(task)
                total_deleted += 1
        
        # Update tasks without task_set (assign based on task_id pattern)
        updated = 0
        for task in tasks_without_set:
            if task.task_id.endswith('A'):
                task.task_set = 'A'
                updated += 1
            elif task.task_id.endswith('B'):
                task.task_set = 'B'
                updated += 1
            elif task.task_id.endswith('C'):
                task.task_set = 'C'
                updated += 1
            else:
                # Old task without suffix - delete it
                db.session.delete(task)
                total_deleted += 1
        
        db.session.commit()
        
        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Deleted: {total_deleted} old tasks")
        print(f"  Updated: {updated} tasks (assigned task_set)")
        print(f"{'='*60}")
        
        # Verify: Count tasks per interface and task_set
        print("\nVerification - Tasks per interface and task_set:")
        for interface in ['faceted', 'llm_assist', 'llm_only']:
            for dataset in ['movies', 'books']:
                for task_set in ['A', 'B', 'C']:
                    count = Task.query.filter_by(
                        interface_type=interface,
                        dataset_type=dataset,
                        task_set=task_set
                    ).count()
                    if count > 0:
                        print(f"  {interface:12s} | {dataset:6s} | Set {task_set}: {count} tasks")
        
        # Check for any remaining issues
        print("\nChecking for issues...")
        for interface in ['faceted', 'llm_assist', 'llm_only']:
            for dataset in ['movies', 'books']:
                total = Task.query.filter_by(
                    interface_type=interface,
                    dataset_type=dataset
                ).count()
                if total != 6:  # Should be 6 (2 per task set)
                    print(f"  ⚠️  {interface} - {dataset}: {total} tasks (expected 6)")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        print("DRY RUN MODE - No changes will be made")
        print("Remove --dry-run flag to actually delete/update tasks")
    else:
        fix_old_tasks()

