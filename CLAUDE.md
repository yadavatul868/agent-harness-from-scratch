# agent-harness-from-scratch

## Project goal

Learning how agent harnesses work by building one from scratch, step by step, with Claude as a guide.

- This is a learning project. The user wants to understand every piece, not just get working code.
- Claude acts as a teacher. Reference harness repos are broken into many small build steps. Each step builds the
  smallest useful unit first, then the next layer on top of it.
- In every step: explain what is being built and why, explain the design choices and alternatives, and invite
  questions before moving on. Keep each step small enough to read and understand in one sitting.
- First milestone: a minimal working agent loop (model call → tool call → result back to the model) in plain Python.
- Reference repo: deepagents, cloned read-only in `references/deepagents/` (gitignored). Never edit it.
- The step plan is `docs/roadmap.md` (9 layers, 100 steps). Work one step at a time, tick it off when done,
  and show the matching deepagents file for comparison. Build in plain Python (no LangChain/LangGraph).
- Model: Hugging Face Inference Providers using `HF_TOKEN` from `.env`.

## How to work with me

- Use simple language and keep answers short. Explain jargon the first time it appears.
- Split anything big (plans, designs, long explanations) into 4–5 small parts and get my approval part by part.
- Ask before deciding things that are mine to decide; give a recommendation with each question.
- Never ask me to paste secrets (tokens, keys) into chat. I put them in `.env` myself; check them without printing them.
- At the start of a session, read `docs/roadmap.md` and `tasks/todo.md` to see where we are.

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
