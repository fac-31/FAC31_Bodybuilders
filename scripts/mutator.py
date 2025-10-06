#!/usr/bin/env python3
"""
Mutator Script
Performs random deletions on the codebase
"""

# TODO: Implement mutation logic
import os
import random
import pathspec

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

def mini_mut(file_path):
    # Deletes random line in given file.
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    if not lines:
        return None

    idx = random.randint(0, len(lines) - 1)
    removed_line = lines.pop(idx)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def run_mutation(directory):
    files = get_all_files(directory)
    if not files:
        print("No files to mutate.")
        return

    target = random.choice(files)
    mini_mut(target)

if __name__ == "__main__":
    run_mutation(".")
