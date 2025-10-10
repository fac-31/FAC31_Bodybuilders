# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a developer tool that strengthens codebases through AI-driven adversarial testing. The system works by:

1. **Mutation**: When `main` is updated, a GitHub Action creates a `mutation` branch where code is intentionally broken (deleting lines, blocks, or files based on configurable probabilities)
2. **Fixing**: An AI agent attempts to repair the damage without knowing what was deleted
3. **Review**: A PR is opened from `mutation` back to `main` for developer review

## Key Concepts

- **Mutator**: Performs deletions at different damage levels (1 line, 1 function, 1 use case). Creates a draft PR and context object for the Fixer. Respects `.mutignore` file for protected files.
- **Fixer**: An LLM (ideally not cutting-edge) that receives information about mutation location and codebase context, but NOT what was deleted. Must genuinely repair the code.
- **Mutation Branch**: Temporary branch where damage and repair happen before PR creation.

## Technical Architecture

### GitHub Actions Workflow (Modular)

Four sequential workflows triggered on push to `main`:

1. **Trigger**: Creates/resets `mutation` branch from `main`
2. **Mutate**: Runs procedural deletion script, commits mutated code + `.mutation-context.json`
3. **Fix**: Reads context, calls LLM API, commits fix
4. **Create PR**: Opens PR from `mutation` → `main`

### Context Passing Mechanism

**`.mutation-context.json`** is committed to the mutation branch and contains:
- Mutation metadata (file, type, location, line count, timestamp, seed)
- Does NOT contain deleted content (to prevent cheating)
- Read by Fixer and PR creator
- Protected by `.mutignore` to prevent self-mutation

Example structure:
```json
{
  "timestamp": "2025-10-02T17:45:00Z",
  "mutations": [{
    "file": "src/utils/helper.js",
    "type": "line",
    "location": "line 42",
    "deletedLineCount": 1
  }],
  "damageLevel": "medium",
  "seed": 12345
}
```

### Key Constraints

- Fixer cannot access git history or original deleted code
- Mutator is procedural (deterministic random deletion)
- Fixer uses a non-cutting-edge LLM
- `.mutignore` protects specific files from mutation

## Code Structure

### Mutation Configuration (`mutation_config.json`)

Defines three flavors: `conservative`, `medium`, `crazy`

Each flavor specifies:
- `blocks_to_mutate`: Probability distribution for 1, 2, or 3 blocks
- `mutation_size`: Linear distribution (min/max percent, start/end probability)

### Utils (`utils/`)

**`mutation_utils.py`** - Core mutation utilities:
- `roll_mutation(flavor, file_lines, seed)` - Main function to determine mutation parameters
- Returns: `{"num_blocks": 2, "blocks": [...], "total_lines": 15, "percentage": 15.0}`
- Uses linear interpolation to sample percentage of lines to delete

### Context (`context/`)

**`context_utils.py`** - MutationContext class for creating `.mutation-context.json`:
- `add_mutation()` - Add mutation metadata
- `save()` - Write context to JSON
- `load()` - Read existing context
