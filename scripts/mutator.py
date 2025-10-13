#!/usr/bin/env python3
"""
Mutator Script
Performs random deletions on the codebase
"""

import os
import random
import pathspec
import sys

from utils.mutation_utils import roll_mutation
from utils.context_utils import MutationContext

MUTIGNORE_PATH = ".mutignore"

def load_mutignore():
    # Loads .mutignore and compiles it into a pathspec object.
    if not os.path.exists(MUTIGNORE_PATH):
        return None
    with open(MUTIGNORE_PATH, 'r') as f:
        patterns = f.read().splitlines()
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

def get_all_files(directory):
    # Recursively gets all files in the directory/repo, excluding those matched by .mutignore.
    ignored = load_mutignore()
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.relpath(os.path.join(root, file), directory)
            if ignored and ignored.match_file(full_path):
                continue
            file_list.append(os.path.join(directory, full_path))
    return file_list

def regular_mutation(file_path, flavor, ctx):
    # Deletes a random number of lines from one file.
    # Severity of line deletion (number of blocks, number of lines within blocks) is determined by flavor (conservative, medium or crazy).
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        file_lines = f.readlines()
    if not file_lines:
        print("No lines to delete.")
        return

    mutation_spec = roll_mutation(flavor, len(file_lines))
    blocks = sorted(mutation_spec['blocks'], key=lambda b: b['start_line'], reverse=True)

    for block in blocks:
        start = block['start_line'] - 1
        count = block['lines_to_delete']
        file_lines[start:start + count] = ['#mutator_was_here\n']
        ctx.add_mutation(
            file_path=file_path,
            start_line=block['start_line'],
            deleted_line_count=count
        )

    with open(file_path, 'w') as f:
        f.writelines(file_lines)

def mega_mutation(file_path, ctx):
    # Deletes all lines from one file.
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        file_lines = f.readlines()
    if not file_lines:
        print("No lines to delete.")
        return

    try:
        with open(file_path, 'w') as f:
            f.writelines([])

        ctx.add_mutation(
            file_path=file_path,
            start_line=1,
            deleted_line_count=len(file_lines)
        )
    except Exception as e:
        print(f"Error during mega mutation: {e}")
        return

def run_mutation(directory, flavor):
    files = get_all_files(directory)
    if not files:
        print("No files to mutate.")
        return

    ctx = None
    if os.path.exists('.mutation-context.json'):
        ctx = MutationContext.load()
    else:
        ctx = MutationContext(config={"flavor": flavor})
    
    target = random.choice(files)
    if flavor != 'pure_and_utter_madness':
        regular_mutation(target, flavor, ctx)
    else:
        mega_mutation(target, ctx)
    
    ctx.save()
    print(f"Mutation context saved as .mutation-context.json")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mutator.py <flavor>")
        sys.exit(1)

    flavor = sys.argv[1]
    run_mutation(".", flavor)
