#!/usr/bin/env python3
"""Create and manage .mutation-context.json files"""

import json
from datetime import datetime


class MutationContext:
    """Manages mutation context data"""

    def __init__(self, seed=None, config=None):
        """Initialize new context with timestamp and ID"""
        now = datetime.utcnow()
        self.timestamp = now.isoformat() + "Z"
        self.mutation_id = f"mut-{now.strftime('%Y%m%d-%H%M%S')}"
        self.seed = seed
        self.config = config or {}
        self.mutations = []

    def add_mutation(self, file_path, start_line, end_line, deleted_line_count,
                     context_before, context_after):
        """Add a mutation to the context"""
        mutation_id = f"mut-{len(self.mutations) + 1}"

        mutation = {
            "id": mutation_id,
            "file": file_path,
            "location": {"start_line": start_line, "end_line": end_line},
            "deleted_line_count": deleted_line_count,
            "context_before": context_before,
            "context_after": context_after
        }

        self.mutations.append(mutation)
        return mutation_id

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

    ctx.add_mutation(
        file_path="src/app.py",
        start_line=42,
        end_line=42,
        deleted_line_count=1,
        context_before=["def main():", "    setup()"],
        context_after=["    return 0"]
    )

    print(f"Created context: {ctx.mutation_id}")
    print(f"Mutations: {len(ctx.mutations)}")

    # Save and load
    ctx.save()
    loaded = MutationContext.load()
    print(f"Loaded: {loaded.mutation_id}")
