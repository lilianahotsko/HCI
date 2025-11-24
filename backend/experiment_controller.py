"""
Experiment Controller: Manages participant assignment, interface ordering, and task sequencing
Following HCI best practices for experimental design:
- Counterbalancing for interface order (Latin Square)
- Balanced counterbalancing for task order within interfaces
- Systematic assignment to ensure equal representation of conditions
"""
import random
import json
from database import db
from models import Participant, Task
from collections import defaultdict

# All possible interface orders (6 permutations - Latin Square design)
INTERFACE_ORDERS = [
    ["faceted", "llm_assist", "llm_only"],
    ["faceted", "llm_only", "llm_assist"],
    ["llm_assist", "faceted", "llm_only"],
    ["llm_assist", "llm_only", "faceted"],
    ["llm_only", "faceted", "llm_assist"],
    ["llm_only", "llm_assist", "faceted"]
]

def _generate_balanced_task_orders(movie_tasks, book_tasks):
    """
    Generate balanced counterbalanced task orders following HCI principles.
    
    For each interface, we have:
    - 2 movie tasks (1 simple, 1 complex)
    - 2 book tasks (1 simple, 1 complex)
    - Total: 4 tasks
    
    HCI Counterbalancing Strategy:
    1. Balance dataset order (movies vs books)
    2. Balance complexity order (simple vs complex)
    3. Balance position effects (first half vs second half)
    4. Create multiple balanced orders
    
    Returns: List of balanced task order dictionaries
    """
    # Separate tasks by dataset and complexity
    movie_simple = [t for t in movie_tasks if t.complexity == 'simple']
    movie_complex = [t for t in movie_tasks if t.complexity == 'complex']
    book_simple = [t for t in book_tasks if t.complexity == 'simple']
    book_complex = [t for t in book_tasks if t.complexity == 'complex']
    
    # Ensure we have the expected structure
    if not (len(movie_simple) == 1 and len(movie_complex) == 1 and 
            len(book_simple) == 1 and len(book_complex) == 1):
        # Fallback: if structure differs, use simple randomization
        all_tasks = movie_tasks + book_tasks
        random.shuffle(all_tasks)
        return [[t.task_id for t in all_tasks]]
    
    ms = movie_simple[0].task_id
    mc = movie_complex[0].task_id
    bs = book_simple[0].task_id
    bc = book_complex[0].task_id
    
    # Generate balanced orders following HCI counterbalancing principles
    # Each order ensures:
    # - Equal representation of datasets in first/second half
    # - Equal representation of complexity in first/second half
    # - No systematic bias from order effects
    
    balanced_orders = [
        # Order 1: Movies first, simple first (within each dataset)
        [ms, mc, bs, bc],
        # Order 2: Movies first, complex first (within each dataset)
        [mc, ms, bc, bs],
        # Order 3: Books first, simple first (within each dataset)
        [bs, bc, ms, mc],
        # Order 4: Books first, complex first (within each dataset)
        [bc, bs, mc, ms],
        # Order 5: Alternating datasets, simple first
        [ms, bs, mc, bc],
        # Order 6: Alternating datasets, complex first
        [mc, bc, ms, bs],
        # Order 7: Alternating datasets, alternating complexity
        [ms, bc, mc, bs],
        # Order 8: Alternating datasets, reverse alternating complexity
        [mc, bs, ms, bc],
    ]
    
    return balanced_orders

def _assign_counterbalancing_condition(participant_id):
    """
    Assign a counterbalancing condition systematically based on participant ID.
    Uses modulo operation to ensure equal distribution across conditions.
    This ensures systematic assignment rather than pure randomization.
    """
    # Convert participant ID to a number for systematic assignment
    # Handle both numeric (P01 -> 1) and alphanumeric IDs
    try:
        # Extract numeric part if exists
        numeric_part = ''.join(filter(str.isdigit, participant_id))
        if numeric_part:
            participant_num = int(numeric_part)
        else:
            # Use hash for alphanumeric IDs
            participant_num = hash(participant_id) % 1000
    except:
        participant_num = hash(participant_id) % 1000
    
    return participant_num

def _get_task_set_assignment(interface_order, participant_num):
    """
    Assign task sets (A, B, C) to interfaces using Latin Square design.
    This ensures each interface gets unique tasks, preventing repetition bias.
    
    Latin Square for 3 interfaces × 3 task sets:
    Position 1: [A, B, C]
    Position 2: [B, C, A]
    Position 3: [C, A, B]
    
    Returns dict: {"faceted": "A", "llm_assist": "B", "llm_only": "C"}
    """
    # Latin Square assignments - ensures each task set appears once per interface position
    latin_square = [
        {'faceted': 'A', 'llm_assist': 'B', 'llm_only': 'C'},
        {'faceted': 'B', 'llm_assist': 'C', 'llm_only': 'A'},
        {'faceted': 'C', 'llm_assist': 'A', 'llm_only': 'B'},
    ]
    
    # Use participant number to select Latin Square row
    square_index = participant_num % len(latin_square)
    base_assignment = latin_square[square_index]
    
    # Map assignment to actual interface order
    # e.g., if interface_order is ['llm_assist', 'faceted', 'llm_only']
    # and base_assignment is {'faceted': 'A', 'llm_assist': 'B', 'llm_only': 'C'}
    # result should be {'llm_assist': 'B', 'faceted': 'A', 'llm_only': 'C'}
    assignment = {}
    for interface in interface_order:
        assignment[interface] = base_assignment[interface]
    
    return assignment

def _create_hci_balanced_task_order(interface_order, counterbalancing_condition=None, participant_num=None):
    """
    Create HCI-compliant balanced task order for each interface.
    
    Strategy:
    1. Assign unique task sets (A, B, C) to each interface using Latin Square
    2. For each interface, get tasks from assigned task set
    3. Generate balanced counterbalanced orders within the task set
    4. This ensures no repetition bias - each interface gets different tasks
    
    Args:
        interface_order: List of interface types in order
        counterbalancing_condition: Optional condition number for systematic assignment
        participant_num: Participant number for task set assignment
    
    Returns dict: {"faceted": [task_ids...], "llm_assist": [...], ...}
    """
    task_order = {}
    
    # Get task set assignment using Latin Square
    if participant_num is not None:
        task_set_assignment = _get_task_set_assignment(interface_order, participant_num)
    else:
        # Fallback: random assignment
        task_sets = ['A', 'B', 'C']
        random.shuffle(task_sets)
        task_set_assignment = {interface: task_sets[i % 3] for i, interface in enumerate(interface_order)}
    
    for interface in interface_order:
        # Get assigned task set for this interface
        assigned_task_set = task_set_assignment[interface]
        
        # Get tasks from assigned task set for this interface
        # IMPORTANT: Only get tasks that have the correct task_set value
        # This ensures we don't include old tasks without proper task_set assignment
        movie_tasks = Task.query.filter(
            Task.interface_type == interface,
            Task.dataset_type == 'movies',
            Task.task_set == assigned_task_set
        ).all()
        book_tasks = Task.query.filter(
            Task.interface_type == interface,
            Task.dataset_type == 'books',
            Task.task_set == assigned_task_set
        ).all()
        
        # Debug: Log what we found
        if len(movie_tasks) != 2 or len(book_tasks) != 2:
            print(f"  Warning: Expected 2 movie + 2 book tasks for {interface} (set {assigned_task_set}), "
                  f"but found {len(movie_tasks)} movie + {len(book_tasks)} book tasks")
            if len(movie_tasks) != 2:
                print(f"    Movie task IDs found: {[t.task_id for t in movie_tasks]}")
            if len(book_tasks) != 2:
                print(f"    Book task IDs found: {[t.task_id for t in book_tasks]}")
        
        # Generate all balanced orders for this interface's task set
        balanced_orders = _generate_balanced_task_orders(movie_tasks, book_tasks)
        
        # Select order based on counterbalancing condition or random
        if counterbalancing_condition is not None and balanced_orders:
            # Use systematic assignment: cycle through orders based on condition
            order_index = counterbalancing_condition % len(balanced_orders)
            selected_order = balanced_orders[order_index]
        elif balanced_orders:
            # Fallback to random selection
            selected_order = random.choice(balanced_orders)
        else:
            # No tasks found - return empty list
            selected_order = []
        
        task_order[interface] = selected_order
    
    return task_order

def get_or_create_participant(participant_id):
    """
    Get existing participant or create new one with HCI-compliant counterbalancing.
    
    Uses systematic assignment based on participant ID to ensure:
    - Equal distribution of interface orders (Latin Square)
    - Consistent assignment (same participant always gets same order)
    """
    try:
        participant = Participant.query.filter_by(participant_id=participant_id).first()
        
        if not participant:
            # Systematic assignment: use participant ID to determine interface order
            # This ensures equal distribution across all 6 orders
            participant_num = _assign_counterbalancing_condition(participant_id)
            interface_order_index = participant_num % len(INTERFACE_ORDERS)
            interface_order = INTERFACE_ORDERS[interface_order_index]
            
            # Store counterbalancing condition for analysis
            counterbalancing_condition = participant_num % 8  # 8 balanced task orders
            
            participant = Participant(
                participant_id=participant_id,
                interface_order=json.dumps(interface_order),
                counterbalancing_condition=counterbalancing_condition
            )
            db.session.add(participant)
            db.session.commit()
        
        return participant
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Database error: {str(e)}")

def _create_randomized_task_order(interface_order):
    """
    Create randomized task order for each interface, mixing movies and books.
    Uses balanced randomization: ensures both datasets are represented, but order is fully randomized.
    Returns dict: {"faceted": [task_ids...], "llm_assist": [...], ...}
    """
    task_order = {}
    
    for interface in interface_order:
        # Get tasks from both datasets for this interface
        movie_tasks = Task.query.filter_by(interface_type=interface, dataset_type='movies').all()
        book_tasks = Task.query.filter_by(interface_type=interface, dataset_type='books').all()
        
        # Convert to list of task IDs
        all_task_ids = [task.task_id for task in movie_tasks] + [task.task_id for task in book_tasks]
        
        # Shuffle to randomize order completely
        # This ensures no predictable pattern while maintaining balanced representation
        # (since we have equal numbers from each dataset)
        random.shuffle(all_task_ids)
        
        # Store randomized task IDs for this interface
        task_order[interface] = all_task_ids
    
    return task_order

def get_experiment_plan(participant_id, use_mixed_datasets=True):
    """
    Returns the full experiment plan for a participant.
    Now supports mixed datasets: each interface gets tasks from both movies and books.
    
    Args:
        participant_id: Unique participant identifier
        use_mixed_datasets: If True, mix movies and books tasks (default: True)
    """
    participant = get_or_create_participant(participant_id)
    
    # Ensure interface order exists
    if not participant.interface_order:
        interface_order = random.choice(INTERFACE_ORDERS)
        participant.interface_order = json.dumps(interface_order)
        db.session.commit()
    else:
        interface_order = json.loads(participant.interface_order)
    
    # Get or create HCI-compliant balanced task order
    if use_mixed_datasets:
        if not participant.task_order:
            # Create new HCI-compliant balanced task order
            # Use counterbalancing condition for systematic assignment
            counterbalancing_condition = participant.counterbalancing_condition if participant.counterbalancing_condition is not None else None
            
            # Get participant number for task set assignment
            participant_num = _assign_counterbalancing_condition(participant_id)
            if participant.counterbalancing_condition is None:
                participant.counterbalancing_condition = participant_num % 8
            
            # Create task order with unique task sets per interface
            task_order_ids = _create_hci_balanced_task_order(
                interface_order, 
                counterbalancing_condition,
                participant_num
            )
            participant.task_order = json.dumps(task_order_ids)
            db.session.commit()
        else:
            task_order_ids = json.loads(participant.task_order)
        
        # Build plan using stored task order
        plan = {}
        for interface in interface_order:
            task_ids = task_order_ids.get(interface, [])
            # Fetch tasks in the stored order
            tasks = []
            for task_id in task_ids:
                task = Task.query.filter_by(task_id=task_id).first()
                if task:
                    tasks.append(task.to_dict())
            plan[interface] = tasks
    else:
        # Legacy mode: single dataset (defaults to movies for backward compatibility)
        plan = {}
        for interface in interface_order:
            tasks = Task.query.filter_by(interface_type=interface, dataset_type='movies').all()
            plan[interface] = [task.to_dict() for task in tasks]
    
    return {
        'participant_id': participant_id,
        'interface_order': interface_order,
        'tasks': plan,
        'dataset_type': 'mixed' if use_mixed_datasets else 'movies',
        'consent_given': participant.consent_given
    }

def record_consent(participant_id):
    """Record that participant has given consent"""
    participant = get_or_create_participant(participant_id)
    from datetime import datetime
    participant.consent_given = True
    participant.consent_timestamp = datetime.utcnow()
    db.session.commit()
    return participant  # Return the Participant object, not dict

