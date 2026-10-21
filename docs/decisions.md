# Decision log

One entry per decision: what we chose, why, and what we passed on. Newest last.
Status is `decided`, `deferred` (decide later), or `replaced by Dn`.

---

## D1. Model access: `openai` SDK + local Ollama

- **Date:** 2026-10-21 · **Status:** decided
- **Decision:** Call models through the `openai` SDK against any OpenAI-compatible server, set by
  `MODEL_BASE_URL`, `MODEL_API_KEY` and `MODEL_NAME` in `.env`. Default: local Ollama, `qwen3.5:9b`.
- **Why:** The Hugging Face account has no Inference Provider credits (every hosted model returns 402).
  The OpenAI format is accepted by Ollama, the Hugging Face router and OpenAI alike, so switching is a
  `.env` edit.
- **Passed on:** `huggingface_hub.InferenceClient` (HF-specific); buying HF credits (cost); raw HTTP
  (more code, same result).
- **Trade-off:** local responses take 15–40 s, and a 9B model calls tools less reliably than large hosted ones.

## D2. Build order: a plain shell backend first, the sandbox after

- **Date:** 2026-10-21 · **Status:** decided
- **Decision:** Layer 4 builds `LocalShellBackend`, the `execute` tool and human approval, with no isolation.
  A new Layer 5 adds the sandbox on top. The later layers move from 5–8 to 6–9.
- **Why:** You see what the shell tool does on its own before adding a boundary around it. Layer 5's demo
  reruns Layer 4's demo, so the difference is visible.

## D3. Sandbox engine: our own `sandbox-exec` code, with sandbox-runtime as reference only

- **Date:** 2026-10-21 · **Status:** decided
- **Decision:** Write the macOS Seatbelt profile and the `sandbox-exec` wrapper ourselves in Python,
  following Anthropic's [sandbox-runtime](https://github.com/anthropics/sandbox-runtime) (cloned in
  `references/sandbox-runtime/`): start from `(deny default)`, allow writes only in the work folder,
  no network, and always block the paths it blocks.
- **Why:** The goal is to understand how the sandbox works, not just to have one.
- **Passed on:** calling sandbox-runtime's `srt` command-line tool (less code and works on Linux too, but
  the sandbox becomes a black box); Docker, and cloud sandboxes such as Modal or Daytona (stronger isolation,
  but they need Docker running, or an account, a key and billing).
- **Known limits:** macOS only. Apple marks `sandbox-exec` deprecated, but it still ships, and Claude Code
  uses the same Seatbelt mechanism. Network allowlists (sandbox-runtime's proxy) are out of scope.

## D4. Integration shape: a partner-style provider for our own harness

- **Date:** 2026-10-21 · **Status:** decided
- **Decision:** Build the sandbox the way deepagents' partner integrations are built (for example
  `libs/partners/modal/langchain_modal/sandbox.py`): a `SeatbeltSandbox` class in its own small package
  that extends our `BaseSandbox` and implements only `execute()`, `upload_files()` and `download_files()`.
  It plugs into our harness only. The agent code does not change; you pass a different backend.
- **Why:** This keeps our design faithful to deepagents and keeps the project in plain Python, with no
  LangChain or LangGraph.

## D5. Testing `SeatbeltSandbox` with the real deepagents library

- **Date:** 2026-10-21 · **Status:** deferred (decide when Layer 5 is done)
- **Idea:** Rerun our `SeatbeltSandbox` against the real `deepagents.backends.sandbox.BaseSandbox`, with
  deepagents installed only for that test. Roadmap step 5.12, optional.
- **Why it might be worth it:** it proves our provider fits deepagents as it really is. The interface is
  small, so it should mostly mean changing one import.
- **Cost:** it installs LangChain and LangGraph, so it has to stay outside the main project's dependencies.
