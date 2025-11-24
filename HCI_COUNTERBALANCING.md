# HCI Counterbalancing Strategy

This document describes the Human-Computer Interaction (HCI) experimental design principles implemented in the experiment controller.

## Overview

The experiment uses a **within-subjects design** where each participant experiences all three interfaces (faceted, LLM-assist, LLM-only) and all task types (movies and books). To eliminate bias and order effects, we implement systematic counterbalancing following HCI best practices.

## Counterbalancing Levels

### 1. Interface Order Counterbalancing (Latin Square Design)

**6 Balanced Orders:**
- Order 1: `[faceted, llm_assist, llm_only]`
- Order 2: `[faceted, llm_only, llm_assist]`
- Order 3: `[llm_assist, faceted, llm_only]`
- Order 4: `[llm_assist, llm_only, faceted]`
- Order 5: `[llm_only, faceted, llm_assist]`
- Order 6: `[llm_only, llm_assist, faceted]`

**Assignment Strategy:**
- Systematic assignment based on participant ID
- Uses modulo operation: `participant_num % 6`
- Ensures equal distribution across all 6 orders
- Same participant always gets same order (consistency)

### 2. Task Order Counterbalancing (Within Each Interface)

For each interface, participants see 4 tasks:
- 2 movie tasks (1 simple, 1 complex)
- 2 book tasks (1 simple, 1 complex)

**8 Balanced Task Orders:**

Each order balances:
- **Dataset order**: Movies vs Books positioning
- **Complexity order**: Simple vs Complex positioning
- **Position effects**: First half vs Second half representation

**Order Patterns:**

1. **Movies-first, Simple-first**: `[M_simple, M_complex, B_simple, B_complex]`
2. **Movies-first, Complex-first**: `[M_complex, M_simple, B_complex, B_simple]`
3. **Books-first, Simple-first**: `[B_simple, B_complex, M_simple, M_complex]`
4. **Books-first, Complex-first**: `[B_complex, B_simple, M_complex, M_simple]`
5. **Alternating datasets, Simple-first**: `[M_simple, B_simple, M_complex, B_complex]`
6. **Alternating datasets, Complex-first**: `[M_complex, B_complex, M_simple, B_simple]`
7. **Alternating datasets, Alternating complexity**: `[M_simple, B_complex, M_complex, B_simple]`
8. **Alternating datasets, Reverse alternating**: `[M_complex, B_simple, M_simple, B_complex]`

**Assignment Strategy:**
- Systematic assignment: `participant_num % 8`
- Ensures equal distribution across all 8 orders
- Each participant gets consistent order across all interfaces

## HCI Principles Applied

### 1. **Counterbalancing**
- All conditions appear equally often in each position
- Eliminates position effects (primacy, recency)
- Controls for learning effects

### 2. **Systematic Assignment**
- Uses participant ID to determine condition
- Ensures equal distribution (not random)
- Allows for replication and analysis

### 3. **Balanced Representation**
- Equal number of tasks from each dataset
- Equal number of simple and complex tasks
- Balanced across positions

### 4. **Within-Subjects Design**
- Each participant experiences all conditions
- Reduces between-subjects variance
- More statistical power with fewer participants

### 5. **Order Effect Mitigation**
- Multiple balanced orders prevent systematic bias
- No single order dominates
- Can analyze order effects in post-hoc analysis

## Implementation Details

### Participant Assignment

```python
def _assign_counterbalancing_condition(participant_id):
    """Extract numeric value from participant ID for systematic assignment"""
    numeric_part = ''.join(filter(str.isdigit, participant_id))
    participant_num = int(numeric_part) if numeric_part else hash(participant_id) % 1000
    return participant_num
```

### Task Order Generation

```python
def _generate_balanced_task_orders(movie_tasks, book_tasks):
    """Generate 8 balanced counterbalanced orders"""
    # Separates tasks by dataset and complexity
    # Creates balanced orders following HCI principles
    # Returns list of task ID sequences
```

### Storage

- **Interface order**: Stored in `participant.interface_order` (JSON)
- **Task order**: Stored in `participant.task_order` (JSON)
- **Counterbalancing condition**: Stored in `participant.counterbalancing_condition` (Integer)

## Analysis Benefits

With this counterbalancing strategy, you can:

1. **Control for order effects**: Analyze if task position affects performance
2. **Control for dataset effects**: Compare movies vs books performance
3. **Control for complexity effects**: Compare simple vs complex task performance
4. **Analyze interactions**: Dataset × Complexity × Position interactions
5. **Replicate conditions**: Same participant always gets same order

## Example Participant Flow

**Participant P01** (ID = 1):
- Interface Order: `[faceted, llm_assist, llm_only]` (1 % 6 = 1)
- Task Order Condition: 1 (1 % 8 = 1)
  - Faceted: `[M_complex, M_simple, B_complex, B_simple]`
  - LLM-assist: `[M_complex, M_simple, B_complex, B_simple]`
  - LLM-only: `[M_complex, M_simple, B_complex, B_simple]`

**Participant P02** (ID = 2):
- Interface Order: `[faceted, llm_only, llm_assist]` (2 % 6 = 2)
- Task Order Condition: 2 (2 % 8 = 2)
  - Faceted: `[B_simple, B_complex, M_simple, M_complex]`
  - LLM-assist: `[B_simple, B_complex, M_simple, M_complex]`
  - LLM-only: `[B_simple, B_complex, M_simple, M_complex]`

## References

- Lazar, J., Feng, J. H., & Hochheiser, H. (2017). *Research Methods in Human-Computer Interaction*. Morgan Kaufmann.
- Sauro, J., & Lewis, J. R. (2016). *Quantifying the User Experience: Practical Statistics for User Research*. Morgan Kaufmann.
- Counterbalancing in HCI: Ensures all conditions appear equally often in each position to control for order effects.

