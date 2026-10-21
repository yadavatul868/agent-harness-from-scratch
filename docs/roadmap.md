# Roadmap: building a deep-agent harness from scratch

Reference: [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents), cloned (shallow) in
`references/deepagents/`. In this file `DA/` means `references/deepagents/libs/deepagents/deepagents/`.
Second reference (Layer 5 sandbox only): [anthropics/sandbox-runtime](https://github.com/anthropics/sandbox-runtime),
the sandbox Claude Code uses, cloned in `references/sandbox-runtime/`. `SRT/` means `references/sandbox-runtime/src/sandbox/`.

**Approach:** plain Python, no LangChain/LangGraph. We copy deepagents' *design* (middleware, backends,
the `task` tool, and so on) and names where it helps, and compare with the real code at each layer.
**Model:** any OpenAI-compatible endpoint via the `openai` SDK, configured in `.env`. We start on local Ollama
(`qwen3.5:9b`); Hugging Face Inference Providers (`router.huggingface.co/v1`) is a `.env` change away.

**How each step works:** Claude explains what and why → we write a small piece of code together → you ask
questions / challenge the design → a test or a demo run proves it works → commit. One step ≈ one sitting.

```
            9. Assembly: create_deep_agent()
      8. Skills + memory     7. Context management
   6. Sub-agents        5. Sandbox provider (sandbox-exec)
            4. Shell + human approval
            3. Filesystem (backends + file tools)
            2. Middleware (hooks + state)
            1. Tools (functions → schemas)
            0. Agent loop
```

---

## Layer 0: The agent loop
Goal: the smallest thing that is an "agent": a model in a loop that can use one tool.

- [x] 0.1 Call the model once from Python (`openai` SDK, endpoint + model from `.env`)
- [ ] 0.2 Messages: system / user / assistant roles; send a short conversation
- [ ] 0.3 What a "tool" is to a model: a JSON schema (name, description, parameters)
- [ ] 0.4 Hand-write one tool schema (`add(a, b)`) and send it with the request
- [ ] 0.5 Read the model's tool-call request (name + JSON arguments)
- [ ] 0.6 Run the Python function and build the tool-result message (`tool_call_id`)
- [ ] 0.7 Send the result back; get the final answer
- [ ] 0.8 Turn it into a `while` loop: stop when the model replies without tool calls
- [ ] 0.9 Add a max-iterations guard (why runaway loops happen)
- [ ] 0.10 Our own `Message` / `ToolCall` dataclasses so the rest of the code isn't tied to one provider

Checkpoint: `run_agent("What is 17*23+4?")` uses tools and answers correctly.
Compare: `DA/graph.py` (`create_deep_agent` → `create_agent`). The loop itself lives in LangChain.

## Layer 1: Tools
Goal: any typed Python function becomes a tool automatically.

- [ ] 1.1 Generate a JSON schema from a function's type hints
- [ ] 1.2 Use the docstring as the tool description (and per-argument descriptions)
- [ ] 1.3 A `@tool` decorator and a `Tool` object
- [ ] 1.4 A tool registry: look tools up by name
- [ ] 1.5 Validate arguments from the model; return clear errors instead of crashing
- [ ] 1.6 When the tool raises: send the error back to the model so it can retry
- [ ] 1.7 Several tool calls in one model turn
- [ ] 1.8 Unknown tool name / malformed JSON handling
- [ ] 1.9 Tools that need context (state, config) without the model seeing it ("injected args")
- [ ] 1.10 Tests for all of the above with a fake model (no network)

Checkpoint: the agent uses 3–4 real tools; the test suite runs offline with a scripted fake model.
Compare: `DA/_tools.py`, the `runtime` injected arg in `DA/middleware/subagents.py` (`_TASK_TOOL_INJECTED_ARGS`).

## Layer 2: Middleware
Goal: the core idea of deepagents. Plug-ins that hook into the loop without editing it.

- [ ] 2.1 Why middleware: what a plain tool *can't* do (change the prompt, change the tool list)
- [ ] 2.2 Agent `state`: a dict that holds `messages` plus extra fields
- [ ] 2.3 Hook 1: `before_agent` (runs once at start)
- [ ] 2.4 Hook 2: `before_model` (runs before every model call; can update state)
- [ ] 2.5 Hook 3: `wrap_model_call` (wraps the call: edit the request, or the response)
- [ ] 2.6 Hook 4: `wrap_tool_call` (wraps each tool run: block, change, or log it)
- [ ] 2.7 The `Middleware` base class; a middleware can also bring its own tools
- [ ] 2.8 Stacking: the order middleware runs in, and why order matters (onion model)
- [ ] 2.9 Middleware that adds its own state fields (`state_schema`)
- [ ] 2.10 Example: a logging middleware
- [ ] 2.11 Example: a system-prompt-injection middleware
- [ ] 2.12 Refactor the Layer 0 loop so *everything* goes through the middleware stack

Checkpoint: logging and prompt-injection middleware work without touching the loop code.
Compare: `DA/middleware/__init__.py` (docstring on tools vs middleware), `DA/middleware/patch_tool_calls.py` (a tiny, real one).

## Layer 3: Filesystem
Goal: the agent can read and write files, and *where* files live can be swapped.

- [ ] 3.1 Why agents need a scratch filesystem (notes, plans, big outputs)
- [ ] 3.2 `BackendProtocol`: the interface (`ls`, `read`, `write`, `edit`, `glob`, `grep`, `delete`)
- [ ] 3.3 Result types (`ReadResult`, `WriteResult`, ...) and why errors are returned, not raised
- [ ] 3.4 `StateBackend`: files kept in agent state (in-memory, per conversation)
- [ ] 3.5 Tool: `ls`
- [ ] 3.6 Tool: `read_file` with line numbers, offset and limit
- [ ] 3.7 Tool: `write_file`
- [ ] 3.8 Tool: `edit_file` (exact string replace; unique-match rule)
- [ ] 3.9 Tool: `glob`
- [ ] 3.10 Tool: `grep`
- [ ] 3.11 Tool: `delete`
- [ ] 3.12 `FilesystemMiddleware`: adds the tools and the filesystem part of the system prompt
- [ ] 3.13 Path rules: normalising paths, blocking `..` escapes
- [ ] 3.14 `FilesystemBackend`: real files on disk under a root folder
- [ ] 3.15 `StoreBackend`: files that survive across conversations (simple key-value store)
- [ ] 3.16 `CompositeBackend`: route `/memories/` to one backend, everything else to another
- [ ] 3.17 Writing good tool descriptions (they're prompts!)
- [ ] 3.18 Demo: agent researches a topic and saves notes to files

Checkpoint: same agent, three storage options, swapped with one argument.
Compare: `DA/backends/protocol.py`, `DA/backends/state.py`, `DA/backends/filesystem.py`, `DA/backends/composite.py`, `DA/middleware/filesystem.py`.

## Layer 4: Shell + human approval
Goal: the agent can run commands, safely.

- [ ] 4.1 `SandboxBackendProtocol`: a backend that can also `execute`
- [ ] 4.2 `LocalShellBackend`: run commands in a folder, with a timeout
- [ ] 4.3 Tool: `execute`; output truncation
- [ ] 4.4 Only show `execute` if the backend supports it (middleware edits the tool list)
- [ ] 4.5 Permissions: allow/deny rules for paths and tools
- [ ] 4.6 Human-in-the-loop: pause before a tool runs; approve / edit / reject
- [ ] 4.7 Resuming after a pause (why state must be saveable)
- [ ] 4.8 Rejected calls: what the model is told
- [ ] 4.9 Safety discussion: what approval can't protect against (sets up Layer 5)
- [ ] 4.10 Demo: agent writes and runs a Python script, asking before each command

Checkpoint: `execute` works, and nothing runs without your OK when approval is on.
Compare: `DA/backends/local_shell.py`, `DA/middleware/permissions.py`, `DA/middleware/_fs_interrupt.py`.

## Layer 5: Sandbox provider
Goal: commands run inside an OS-enforced sandbox, plugged in the way deepagents' partner integrations
(Modal, Daytona, Vercel, ...) are. Decisions D2–D4 in `docs/decisions.md`.

- [ ] 5.1 Local vs container vs cloud sandboxes; how deepagents' partner packages plug in
- [ ] 5.2 `BaseSandbox`: build `ls` / `read` / `write` / `edit` / `glob` / `grep` from `execute()` + `upload_files()` / `download_files()`
- [ ] 5.3 Test `BaseSandbox` with a plain local subclass: same results as the Layer 3 tools
- [ ] 5.4 Partner-style package: `partners/seatbelt/` holding one `SeatbeltSandbox(BaseSandbox)` class
- [ ] 5.5 Seatbelt profile: start from `(deny default)`; allow reads, writes only in the work folder, no network
- [ ] 5.6 Always-blocked paths: shell startup files, `.git/hooks`, `.git/config` (they run later, outside the sandbox)
- [ ] 5.7 `SeatbeltSandbox.execute()`: wrap each command in `sandbox-exec`; timeouts; reading "Operation not permitted"
- [ ] 5.8 `upload_files` / `download_files` for the sandbox's work folder
- [ ] 5.9 Choose a backend by name (`local`, `seatbelt`)
- [ ] 5.10 Escape tests that must fail: write outside, reach the network, touch a blocked path
- [ ] 5.11 Demo: the Layer 4 demo again, sandboxed; the agent code is unchanged, one argument differs
- [ ] 5.12 *(optional, decide later: D5)* Run `SeatbeltSandbox` under the real deepagents library

Checkpoint: switching `backend="local"` to `"seatbelt"` changes no agent code, and every escape test fails as it should.
Compare: `DA/backends/sandbox.py` (`BaseSandbox`), `references/deepagents/libs/partners/modal/langchain_modal/sandbox.py`,
`references/deepagents/libs/code/deepagents_code/integrations/sandbox_factory.py`,
`SRT/macos-sandbox-utils.ts` (`wrapCommandWithSandboxMacOS`, `generateWriteRules`, `macGetMandatoryDenyEntries`),
`SRT/sandbox-utils.ts` (`DANGEROUS_FILES`).

## Layer 6: Sub-agents
Goal: the main agent hands a sub-task to a helper with a clean context.

- [ ] 6.1 Why: context isolation (the helper's messy work doesn't fill the main context)
- [ ] 6.2 A sub-agent is just another agent: reuse our loop
- [ ] 6.3 The `task` tool: `description` plus `subagent_type`
- [ ] 6.4 The tool description lists the available sub-agents
- [ ] 6.5 Return only the final answer to the parent
- [ ] 6.6 The default `general-purpose` sub-agent (same tools as the parent)
- [ ] 6.7 Custom sub-agents: name, description, prompt, tools, model
- [ ] 6.8 What state is shared vs private (files yes, messages no)
- [ ] 6.9 Sub-agents get their own middleware stack
- [ ] 6.10 Running several `task` calls in one turn (parallel)
- [ ] 6.11 Preventing infinite delegation (depth limits)
- [ ] 6.12 Demo: researcher sub-agent + writer main agent

Checkpoint: the main agent delegates two research tasks and combines the results.
Compare: `DA/middleware/subagents.py` (`SubAgent`, `TASK_TOOL_DESCRIPTION`, general-purpose spec).

## Layer 7: Context management
Goal: long tasks don't overflow the model's context window.

- [ ] 7.1 Tokens and context windows; counting tokens (approximate is fine)
- [ ] 7.2 Watching size: trigger when history passes a fraction of the window
- [ ] 7.3 Summarization: replace old messages with a summary; keep the recent ones
- [ ] 7.4 Never split a tool call from its result when cutting history
- [ ] 7.5 Saving the full old history to a file before summarizing
- [ ] 7.6 Offloading huge tool outputs to files; give the model a pointer + preview
- [ ] 7.7 Truncating large old tool-call arguments
- [ ] 7.8 Patching dangling tool calls (a call with no result breaks the next request)
- [ ] 7.9 A `compact_conversation` tool the agent can call itself
- [ ] 7.10 Tests with a tiny fake context window
- [ ] 7.11 Prompt caching: what it is, why middleware order matters for it
- [ ] 7.12 Demo: a long task that summarizes itself and keeps going

Checkpoint: a 50-tool-call task completes in a small context window.
Compare: `DA/middleware/summarization.py` (trigger 0.85 / keep 0.10), `DA/middleware/patch_tool_calls.py`, `DA/middleware/_overflow_clip.py`, `DA/middleware/_blob_offload.py`.

## Layer 8: Skills + memory
Goal: reusable know-how loaded only when needed, and memory that survives sessions.

- [ ] 8.1 Skills: folders with a `SKILL.md` (YAML frontmatter + instructions)
- [ ] 8.2 Find and parse skills from a backend
- [ ] 8.3 Show only skill *names + descriptions* in the prompt ("progressive disclosure")
- [ ] 8.4 Load the full skill when the agent asks for it
- [ ] 8.5 `SkillsMiddleware`
- [ ] 8.6 Memory: `AGENTS.md` files injected into the system prompt
- [ ] 8.7 The agent updates its own memory file (with `edit_file`)
- [ ] 8.8 Memory that persists across threads (`StoreBackend` / composite route)
- [ ] 8.9 `MemoryMiddleware`
- [ ] 8.10 Demo: teach the agent a preference once; it remembers next session

Checkpoint: skills load on demand; memory survives a restart.
Compare: `DA/middleware/skills.py`, `DA/middleware/memory.py`.

## Layer 9: Assembly
Goal: one function that builds a full deep agent, like the real thing.

- [ ] 9.1 Composing the system prompt (base + user instructions + middleware sections)
- [ ] 9.2 Default middleware order, and why it's that order
- [ ] 9.3 `create_deep_agent(model, tools, system_prompt, subagents, backend, skills, memory, ...)`
- [ ] 9.4 Profiles: small per-model tweaks (tool descriptions, excluded tools)
- [ ] 9.5 End-to-end demo: a real multi-step task using every layer
- [ ] 9.6 Retrospective: our version vs deepagents. What LangGraph gives them (checkpoints, streaming) that we skipped

Checkpoint: `create_deep_agent()` runs the end-to-end demo.
Compare: `DA/graph.py` lines ~888–1010 (main middleware stack assembly), `DA/profiles/`.

---

Optional later: port our middleware onto LangChain's `create_agent()` to see how close the real thing is.
