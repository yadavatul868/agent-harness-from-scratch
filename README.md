# agent-harness-from-scratch

Learning how agent harnesses work by building one from scratch, step by step, with Claude as a guide.

## Setup

```bash
uv sync
cp .env.example .env   # then add your keys
```

## Run

```bash
uv run agent-harness-from-scratch
uv run pytest
uv run ruff check .
```

## Layout

```
src/agent_harness_from_scratch/   package code
tests/                 pytest tests
notebooks/             experiments
scripts/               one-off scripts
data/raw, processed    local data (not committed)
docs/                  notes and design docs
tasks/                 todo.md and lessons.md
```

## Branches

- `main`: stable, only changed through PRs from `dev`
- `dev`: integration branch
- `feature/<name>`: one per feature, PR into `dev`
