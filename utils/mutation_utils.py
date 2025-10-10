#!/usr/bin/env python3
"""Roll dice to determine which lines to delete"""

import json
import random


def roll_mutation(flavor, file_lines, seed=None):
    """
    Decide how many blocks and lines to delete, and where

    Returns: {
        "num_blocks": 2,
        "blocks": [
            {"start_line": 15, "lines_to_delete": 8},
            {"start_line": 50, "lines_to_delete": 13}
        ]
    }
    """
    if seed:
        random.seed(seed)

    # Load config
    with open("mutation_config.json") as f:
        config = json.load(f)

    if flavor not in config:
        raise ValueError(f"Unknown flavor '{flavor}'")

    flavor_config = config[flavor]

    # Sample number of blocks (1, 2, or 3)
    blocks_prob = flavor_config["blocks_to_mutate"]
    values = [int(k) for k in blocks_prob.keys()]
    weights = list(blocks_prob.values())
    num_blocks = random.choices(values, weights=weights)[0]

    # Sample lines per block using linear distribution
    ms = flavor_config["mutation_size"]
    min_p = ms["min_percent"]
    max_p = ms["max_percent"]
    start_prob = ms["start_probability"]
    end_prob = ms["end_probability"]

    blocks = []
    lines_deleted_so_far = 0
    used_ranges = []  # Track (start, end) to avoid overlaps

    for i in range(num_blocks):
        # Calculate how many lines are still available
        lines_remaining = file_lines - lines_deleted_so_far

        # If we've already deleted everything, stop
        if lines_remaining <= 0:
            break

        # Create 20 sample points between min and max percent
        percentages = []
        probabilities = []

        for j in range(20):
            percent = min_p + (max_p - min_p) * j / 19
            # Linear interpolation for probability
            normalized = (percent - min_p) / (max_p - min_p)
            prob = start_prob + (end_prob - start_prob) * normalized
            percentages.append(percent)
            probabilities.append(prob)

        # Sample a percentage and convert to lines
        sampled_percent = random.choices(percentages, weights=probabilities)[0]
        lines = max(1, int(file_lines * sampled_percent / 100))

        # Cap at remaining lines
        lines = min(lines, lines_remaining)

        # Pick a random start line that doesn't overlap with previous blocks
        max_attempts = 50
        start_line = None

        for _ in range(max_attempts):
            # Random start between 1 and (file_lines - lines + 1)
            candidate_start = random.randint(1, max(1, file_lines - lines + 1))
            candidate_end = candidate_start + lines - 1

            # Check if this overlaps with any existing block
            overlaps = False
            for existing_start, existing_end in used_ranges:
                if not (candidate_end < existing_start or candidate_start > existing_end):
                    overlaps = True
                    break

            if not overlaps:
                start_line = candidate_start
                used_ranges.append((candidate_start, candidate_end))
                break

        # If we couldn't find a non-overlapping spot, skip this block
        if start_line is None:
            continue

        blocks.append({
            "start_line": start_line,
            "lines_to_delete": lines
        })
        lines_deleted_so_far += lines

    return {
        "num_blocks": len(blocks),
        "blocks": blocks
    }


if __name__ == "__main__":
    for flavor in ["conservative", "medium", "crazy"]:
        print(f"\n{flavor.upper()}")
        for _ in range(3):
            result = roll_mutation(flavor, 100)
            blocks_str = ", ".join(f"L{b['start_line']}+{b['lines_to_delete']}" for b in result['blocks'])
            print(f"  {result['num_blocks']} blocks: {blocks_str}")
