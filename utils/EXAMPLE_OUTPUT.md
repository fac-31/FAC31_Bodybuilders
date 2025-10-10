# roll_mutation() Return Value

`roll_mutation()` now returns only the information needed to carry out deletions:

```python
{
    "num_blocks": 2,
    "blocks": [
        {"start_line": 15, "lines_to_delete": 8},
        {"start_line": 50, "lines_to_delete": 13}
    ]
}
```

Each entry in `blocks` tells you where to begin deleting and how many consecutive lines to remove. All other details (e.g. flavor, totals, percentages) are intentionally omitted to keep the response lightweight.
