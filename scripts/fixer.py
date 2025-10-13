#!/usr/bin/env python3
"""
Fixer Script
Reads .mutation-context.json
Calls LLM to generate fixes
Applies fixes to mutated files
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.context_utils import MutationContext

MARKER = "#mutator_was_here"
PLACEHOLDER_LINE = "FIXER_PLACEHOLDER\n"


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


def _build_placeholder_lines(count):
    """Create minimal filler lines to stand in for missing code."""
    count = max(1, count)
    return [PLACEHOLDER_LINE for _ in range(count)]


def _replace_marker(lines, replacements):
    """Swap the first marker occurrence with the planned replacement lines."""
    for idx, line in enumerate(lines):
        if line.strip() == MARKER:
            return lines[:idx] + replacements + lines[idx + 1 :]
    return lines


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
            fillers = _build_placeholder_lines(deleted)
            print(f"  planned replacement lines: {len(fillers)} (first line: {fillers[0].rstrip()})")

            updated = _replace_marker(lines, fillers)
            if updated != lines:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(updated)
                ctx.record_fix(mutation["id"], added_code=fillers)
                print(f"  marker replaced and recorded in context")
            else:
                print("  ! expected marker missing during write")
        else:
            print("  ! marker not found in file")

    ctx.save()
    print("Updated mutation context saved.")


if __name__ == "__main__":
    main()
