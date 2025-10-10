# Utils

Two utilities for the mutation workflow.

---

## mutation_utils.py

**Purpose:** Roll dice to decide which lines to delete.

**How it works:**
1. Reads `mutation_config.json` to get flavor settings
2. Randomly picks number of blocks (1, 2, or 3)
3. For each block, picks how many lines to delete using linear probability
4. Returns the plan

**Usage:**
```python
from utils.mutation_utils import roll_mutation

result = roll_mutation("medium", file_lines=100)
# {
#   "num_blocks": 2,
#   "blocks": [
#     {"start_line": 15, "lines_to_delete": 8},
#     {"start_line": 50, "lines_to_delete": 13}
#   ]
# }
```

**Flavors:** `conservative`, `medium`, `crazy`

---

## context_utils.py

**Purpose:** Create `.mutation-context.json` to record what was mutated (but not what was deleted).

**How it works:**
1. Create a context with timestamp and ID
2. Add mutations (file, location, line count, context before/after)
3. Save to JSON file

**Usage:**
```python
from utils.context_utils import MutationContext

# Create context
ctx = MutationContext(seed=12345, config={"flavor": "medium"})

# Add mutation info (WITHOUT the deleted code)
ctx.add_mutation(
    file_path="src/app.py",
    start_line=10,
    end_line=15,
    deleted_line_count=6,
    context_before=["def main():", "    setup()"],
    context_after=["    return 0"]
)

# Save
ctx.save()  # Creates .mutation-context.json

# Load later
ctx = MutationContext.load()
print(ctx.mutation_id)  # "mut-20251002-143022"
```

---

## Testing

```bash
python3 utils/mutation_utils.py
python3 utils/context_utils.py
```
