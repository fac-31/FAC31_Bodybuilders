#!/usr/bin/env python3
"""Create and manage .mutation-context.json files"""

import json
from datetime import datetime, timezone


class MutationContext:
    """Manages mutation context data"""

    def __init__(self, seed=None, config=None):
        """Initialize new context with timestamp and ID"""
        now = datetime.now(timezone.utc)
        self.timestamp = now.isoformat().replace("+00:00", "Z")
        self.mutation_id = f"mut-{now.strftime('%Y%m%d-%H%M%S')}"
        self.seed = seed
        self.config = config or {}
        self.mutations = []

    def add_mutation(self, file_path, start_line, deleted_line_count):
        """Record that the mutator removed some lines"""
        mutation_id = f"mut-{len(self.mutations) + 1}"

        mutation = {
            "id": mutation_id,
            "file": file_path,
            "start_line": start_line,
            "deleted_line_count": deleted_line_count,
            "added_code": None
        }

        self.mutations.append(mutation)
        return mutation_id

    def record_fix(self, mutation_id, added_code):
        """Attach fixer-generated code to an existing mutation"""
        for mutation in self.mutations:
            if mutation["id"] == mutation_id:
                mutation["added_code"] = added_code
                return

        raise ValueError(f"Unknown mutation_id '{mutation_id}'")

    def save(self, path=".mutation-context.json"):
        """Save context to JSON file"""
        data = {
            "timestamp": self.timestamp,
            "mutation_id": self.mutation_id,
            "seed": self.seed,
            "config": self.config,
            "mutations": self.mutations
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path=".mutation-context.json"):
        """Load context from JSON file"""
        with open(path, 'r') as f:
            data = json.load(f)

        ctx = cls(seed=data.get("seed"), config=data.get("config", {}))
        ctx.timestamp = data["timestamp"]
        ctx.mutation_id = data["mutation_id"]
        ctx.mutations = data["mutations"]
        return ctx


if __name__ == "__main__":
    # Example
    ctx = MutationContext(seed=12345, config={"flavor": "medium"})

    mut_id = ctx.add_mutation(
        file_path="src/app.py",
        start_line=42,
        deleted_line_count=3
    )

    ctx.record_fix(mut_id, added_code=[
        "def main():",
        "    return 0"
    ])

    print(f"Created context: {ctx.mutation_id}")
    print(f"Mutations: {len(ctx.mutations)}")

    # Save and load
    ctx.save()
    loaded = MutationContext.load()
    print(f"Loaded: {loaded.mutation_id}")
