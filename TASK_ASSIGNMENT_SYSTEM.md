# Task Assignment System - Preventing Repetition Bias

## Overview

This system ensures that participants see **different, unique tasks** for each interface, preventing repetition bias where participants might remember and be influenced by seeing the same task description across different interfaces.

## Key Features

### 1. Multiple Task Sets (A, B, C)

Each interface has **3 unique task sets**:
- **Set A**: Original tasks
- **Set B**: Different scenarios, same complexity balance
- **Set C**: Different scenarios, same complexity balance

Each set contains:
- 2 movie tasks (1 simple, 1 complex)
- 2 book tasks (1 simple, 1 complex)
- **Total: 4 tasks per set**

### 2. Latin Square Design for Task Set Assignment

Task sets are assigned to interfaces using a **Latin Square design** to ensure:
- Each interface gets a different task set
- Each task set appears equally often in each interface position
- No systematic bias from task set assignment

**Latin Square Pattern:**
```
Participant Group 1: Faceted=A, LLM-Assist=B, LLM-Only=C
Participant Group 2: Faceted=B, LLM-Assist=C, LLM-Only=A
Participant Group 3: Faceted=C, LLM-Assist=A, LLM-Only=B
```

### 3. HCI-Compliant Shuffling Within Task Sets

Within each task set, tasks are shuffled using the existing HCI counterbalancing system:
- 8 balanced orders per interface
- Balances dataset order (movies vs books)
- Balances complexity order (simple vs complex)
- Balances position effects

## How It Works

### Step 1: Task Set Assignment

When a participant starts:
1. System extracts participant number from ID
2. Uses Latin Square to assign task sets:
   - Interface 1 → Task Set A, B, or C
   - Interface 2 → Different task set
   - Interface 3 → Different task set

### Step 2: Task Selection Within Set

For each interface:
1. Get tasks from assigned task set (A, B, or C)
2. Apply HCI counterbalancing to shuffle:
   - 2 movie tasks (1 simple, 1 complex)
   - 2 book tasks (1 simple, 1 complex)
3. Result: 4 tasks in balanced, randomized order

### Step 3: Participant Experience

**Example Participant P01:**
- Interface Order: `[faceted, llm_assist, llm_only]`
- Task Set Assignment: `{faceted: 'A', llm_assist: 'B', llm_only: 'C'}`
- Faceted Interface: Tasks from Set A (shuffled)
- LLM-Assist Interface: Tasks from Set B (shuffled) - **Different tasks!**
- LLM-Only Interface: Tasks from Set C (shuffled) - **Different tasks!**

## Benefits

### 1. **Eliminates Repetition Bias**
- Participants never see the same task description twice
- Each interface feels fresh and different
- Reduces memory effects and learning bias

### 2. **Maintains Experimental Validity**
- Tasks are equivalent in complexity and structure
- Balanced across datasets and complexity levels
- Comparable across interfaces

### 3. **HCI-Compliant Design**
- Latin Square ensures equal representation
- Systematic assignment prevents bias
- Counterbalanced within each task set

### 4. **Scalable System**
- Easy to add more task sets (D, E, F...)
- Can accommodate more interfaces
- Maintains balance and randomization

## Task Structure

### Movies Dataset
- **Set A**: T01A-T06A (6 tasks, 2 per interface)
- **Set B**: T01B-T06B (6 tasks, 2 per interface)
- **Set C**: T01C-T06C (6 tasks, 2 per interface)

### Books Dataset
- **Set A**: B01A-B06A (6 tasks, 2 per interface)
- **Set B**: B01B-B06B (6 tasks, 2 per interface)
- **Set C**: B01C-B06C (6 tasks, 2 per interface)

**Total: 36 tasks** (18 movies + 18 books)

## Implementation Details

### Database Schema
- `Task.task_set`: Stores task set identifier ('A', 'B', or 'C')
- `Participant.task_order`: Stores final task order per interface
- `Participant.counterbalancing_condition`: Used for systematic assignment

### Assignment Logic
```python
# Latin Square assignment
latin_square = [
    {'faceted': 'A', 'llm_assist': 'B', 'llm_only': 'C'},
    {'faceted': 'B', 'llm_assist': 'C', 'llm_only': 'A'},
    {'faceted': 'C', 'llm_assist': 'A', 'llm_only': 'B'},
]

# Participant assignment
square_index = participant_num % 3
task_set_assignment = latin_square[square_index]
```

## Example Scenarios

### Scenario 1: Participant P01
- **Interface Order**: `[faceted, llm_assist, llm_only]`
- **Task Sets**: `{faceted: 'A', llm_assist: 'B', llm_only: 'C'}`
- **Tasks Seen**:
  - Faceted: "Find all movies released after 2015..." (Set A)
  - LLM-Assist: "Locate action or adventure movies..." (Set B) ✨ Different!
  - LLM-Only: "Find science fiction movies..." (Set C) ✨ Different!

### Scenario 2: Participant P02
- **Interface Order**: `[llm_assist, faceted, llm_only]`
- **Task Sets**: `{llm_assist: 'B', faceted: 'C', llm_only: 'A'}`
- **Tasks Seen**:
  - LLM-Assist: "Locate action or adventure movies..." (Set B)
  - Faceted: "Find science fiction movies..." (Set C) ✨ Different!
  - LLM-Only: "Find all movies released after 2015..." (Set A) ✨ Different!

## Analysis Benefits

With this system, you can:
1. **Compare interfaces fairly** - No repetition bias
2. **Analyze task set effects** - Each set appears equally often
3. **Control for order effects** - Latin Square ensures balance
4. **Maintain statistical power** - Balanced design across all conditions

## References

- Latin Square Design: Ensures each condition appears equally often in each position
- Counterbalancing: Controls for order effects within task sets
- HCI Best Practices: Prevents repetition bias and learning effects

