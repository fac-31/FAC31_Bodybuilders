#!/usr/bin/env python3
"""
Fixer Script
Reads .mutation-context.json
Calls LLM to generate fixes
Applies fixes to mutated files
"""

import os
import anthropic
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.context_utils import MutationContext

def _format_prompt(file_path):
    file_content = None
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    return f"""You are a code repair assistant.
    The following Python file has been automatically mutated. Some lines of code were deleted and replaced with the marker `#mutator_was_here`. Your task is to infer and regenerate the missing code for each of those deleted sections.
    
    Instructions:
    - For every '#mutator_was_here' line, generate code that reasonably fits the surrounding context.
    - Insert your regenerated code directly after the '#mutator_was_here' line.
    - Replace each '#mutator_was_here' comment with the comment '#fixer_was_here'.
    - Maintain correct indentation and syntax.
    - Preserve all other code exactly as-is.
    
    File path: `{file_path}`
    Here is the current content of the file:
    ```python{file_content}```
    Please return the entire repaired file with your changes included.
    """

def _run_fix(file_path, anthropic_api_key):
    client = anthropic.Anthropic(api_key=anthropic_api_key)
    prompt = _format_prompt(file_path)

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        temperature=1,
        system="You are a helpful code assistant.",
        messages=[{"role": "user", "content": prompt}]
    )

    return message.completion

def main():
    try:
        ctx = MutationContext.load()
    except FileNotFoundError:
        print("No mutation context found. Did the mutator run?", file=sys.stderr)
        sys.exit(1)

    file_path = ctx.mutations[0]["file"]
    anthropic_api_key = os.getenv("LLM_API_KEY")

    repaired_file_content = _run_fix(file_path, anthropic_api_key)

    with open(file_path, "w") as f:
        f.write(repaired_file_content)

if __name__ == "__main__":
    main()
