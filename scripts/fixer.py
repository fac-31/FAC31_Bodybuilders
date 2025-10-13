#!/usr/bin/env python3
"""
Fixer Script
Reads .mutation-context.json
Calls LLM to generate fixes
Applies fixes to mutated files
"""

import sys

from utils.context_utils import MutationContext

MARKER = "#mutator_was_here"


def _read_file_lines(path):
    """Best-effort load of a mutated file, tolerating deletions."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()
    except FileNotFoundError:
        print(f"  ! mutated file missing: {path}", file=sys.stderr)
        return None


def _find_marker_lines(lines):
    """Return 1-based indices where the mutator placeholder remains."""
    return [idx for idx, line in enumerate(lines, start=1) if line.strip() == MARKER]


def main():
    try:
        ctx = MutationContext.load()
    except FileNotFoundError:
        print("No mutation context found. Did the mutator run?", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded mutation context {ctx.mutation_id}")
    for mutation in ctx.mutations:
        file_path = mutation["file"]
        start_line = mutation["start_line"]
        deleted = mutation["deleted_line_count"]
        print(f"- {file_path}: start_line={start_line}, deleted_lines={deleted}")

        lines = _read_file_lines(file_path)
        if lines is None:
            continue

        marker_lines = _find_marker_lines(lines)
        if marker_lines:
            print(f"  marker found at lines: {marker_lines}")
        else:
            print("  ! marker not found in file")


if __name__ == "__main__":
    main()
