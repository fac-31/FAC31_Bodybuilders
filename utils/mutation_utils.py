#!/usr/bin/env python3
"""Roll dice to determine which lines to delete"""

import json
import random


def roll_mutation(flavor, file_lines, seed=None):
    """
    Decide how many blocks and lines to delete

    Returns: {"num_blocks": 2, "blocks": [...], "total_lines": 15, "percentage": 15.0}
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
    for i in range(num_blocks):
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

        blocks.append({"block_id": i + 1, "lines_to_delete": lines})

    total_lines = sum(b["lines_to_delete"] for b in blocks)

    return {
        "flavor": flavor,
        "num_blocks": num_blocks,
        "blocks": blocks,
        "total_lines": total_lines,
        "file_lines": file_lines,
        "percentage": round(total_lines / file_lines * 100, 2)
    }


if __name__ == "__main__":
    for flavor in ["conservative", "medium", "crazy"]:
        print(f"\n{flavor.upper()}")
        for _ in range(3):
            result = roll_mutation(flavor, 100)
            blocks_str = ", ".join(f"{b['lines_to_delete']}L" for b in result['blocks'])
            print(f"  {result['num_blocks']} blocks: [{blocks_str}] = {result['total_lines']}L ({result['percentage']}%)")
