#!/usr/bin/env python3
"""
Fixer Script
Reads .mutation-context.json
Calls LLM to generate fixes
Applies fixes to mutated files
"""

# TODO: Implement fixer logic

import sys

from utils.context_utils import MutationContext


def load_context(path=".mutation-context.json"):
    try:
        return MutationContext.load(path)
    except FileNotFoundError:
        print("No mutation context found. Did the mutator run?", file=sys.stderr)
        return None


def main():
    ctx = load_context()
    if ctx is None:
        sys.exit(1)

    print(f"Loaded mutation context {ctx.mutation_id}")
    for mutation in ctx.mutations:
        file_path = mutation["file"]
        start_line = mutation["start_line"]
        deleted = mutation["deleted_line_count"]
        print(f"- {file_path}: start_line={start_line}, deleted_lines={deleted}")


if __name__ == "__main__":
    main()
