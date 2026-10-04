# agent-harness-from-scratch

## Project goal

Learning how agent harnesses work by building one from scratch, step by step, with Claude as a guide.

## Git workflow

- Never commit or push directly to `main`.
- Start each feature on a new branch off `dev`: `git switch dev && git pull && git switch -c feature/<name>`.
- Open PRs `feature/<name>` → `dev`. The user merges `dev` → `main` manually via PR.

## Python

- Python 3.12, managed by uv. Use `uv add <pkg>` and `uv run <cmd>`; never `pip install`.
- Package code lives in `src/agent_harness_from_scratch/`; tests in `tests/`.
- Lint/format with ruff (`uv run ruff check .`, `uv run ruff format .`); test with `uv run pytest`.
- Type hints on all function signatures. Load secrets from `.env`, never hard-code them.

## Tasks

- Plans and progress go in `tasks/todo.md`; lessons from corrections go in `tasks/lessons.md`.
