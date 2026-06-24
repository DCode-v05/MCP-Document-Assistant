# MCP Document Assistant

**A command-line chat app that gives Anthropic's Claude direct, structured access to your local documents over the Model Context Protocol.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white) ![Anthropic Claude](https://img.shields.io/badge/Anthropic_Claude-D97757?style=flat&logo=anthropic&logoColor=white) ![MCP](https://img.shields.io/badge/Model_Context_Protocol-1.8+-000000?style=flat&logo=modelcontextprotocol&logoColor=white) ![FastMCP](https://img.shields.io/badge/FastMCP-server-4B8BBE?style=flat) ![prompt_toolkit](https://img.shields.io/badge/prompt__toolkit-CLI-2C3E50?style=flat) ![uv](https://img.shields.io/badge/uv-packaging-DE5FE9?style=flat&logo=astral&logoColor=white)

## Overview

This is a terminal chat client that lets Claude work against a set of local documents instead of an isolated chat box. Rather than copy-pasting file contents into a prompt every time, you mention a document with `@` and the assistant pulls in its contents, or you run a `/command` that triggers a predefined workflow on the server side. Under the hood it talks to a local MCP server that owns the documents and exposes them through the three Model Context Protocol primitives: Resources, Tools, and Prompts.

It's a focused, single-purpose app — the document store is a small in-memory set of sample files (a deposition, a report, financials, a spec, etc.), so the project is really a clean, working reference for how an LLM CLI wires up to an MCP server: the client/server split, the tool-use loop, context injection, and a prompt-toolkit UI with live autocompletion. It's module 5 ("Claude MCP") of a longer MCP learning series, and it's the piece where the client-side agent loop and `@`/`/` UX patterns were worked out that later carried over into bigger MCP projects.

## Key Features

- **Interactive Claude chat in the terminal** — a REPL-style loop (`> `) backed by `prompt-toolkit`, with in-memory history, live completion menus, and inline auto-suggestions.
- **`@`-mention context injection** — type `@` to open an autocomplete menu of available documents; mentioned docs are read from the MCP server and injected into the prompt inside `<document>` tags before Claude sees the query.
- **`/`-command prompt workflows** — type `/` to list server-defined prompts (`format_doc`, `summarize_doc`), pass a document id, and have the server return a ready-made instruction sequence that's appended to the conversation.
- **Tool-use loop** — Claude can call MCP tools on its own; the client runs a loop that executes each requested tool, feeds the result back, and repeats until Claude produces a final text answer.
- **Document tools** — `read_doc` (read a document's contents) and `edit_doc` (search-and-replace edit on a document).
- **Document resources** — a `docs://documents` list resource and a per-document `docs://document/{doc_id}` content resource, returned as JSON or plain text.
- **Server-side prompts** — `summarize_doc` (concise summary) and `format_doc` (rewrite a document into Markdown using the edit tool).
- **Multi-server ready** — the entry point can attach additional MCP servers passed as command-line arguments, and the tool manager aggregates tools across every connected client and routes each call to the client that owns the tool.
- **Cross-platform stdio transport** — client and server communicate over stdio JSON-RPC, with a Windows-specific asyncio event-loop policy set so it runs on Windows as well as Unix.

## How It Works

The app is split into a client process (the CLI you talk to) and a server process (which owns the documents). They run as separate processes and speak MCP over stdio.

### MCP Server (`mcp_server.py`)

A `FastMCP` server named `DocumentMCP`. It holds an in-memory `docs` dictionary of sample documents keyed by id (`deposition.md`, `report.pdf`, `financials.docx`, `outlook.pdf`, `plan.md`, `spec.txt`). It registers:

- **Tools** — `read_doc(doc_id)` returns a document's text; `edit_doc(doc_id, old_str, new_str)` does an in-place string replacement. Both raise a clear error if the id doesn't exist. Arguments are described with Pydantic `Field` metadata so the schema reaches the model.
- **Resources** — `docs://documents` returns the list of ids as JSON; `docs://document/{doc_id}` returns a single document's contents as plain text.
- **Prompts** — `summarize_doc(doc_id)` and `format_doc(doc_id)` return templated `UserMessage` instruction sequences. `format_doc` tells Claude to add headers, bullets and tables and to apply the changes via the edit tool without altering meaning.

It runs with `mcp.run(transport="stdio")`.

### MCP Client (`mcp_client.py`)

A thin async wrapper around the MCP SDK's `ClientSession` and `stdio_client`. It spawns the server as a subprocess (`python mcp_server.py`, or `uv run` when `USE_UV=1`), initializes the session, and exposes helpers: `list_tools`, `call_tool`, `list_prompts`, `get_prompt`, and `read_resource`. `read_resource` decodes the first content block and parses JSON when the mime type is `application/json`. The client is an async context manager, so connect/cleanup is handled by an `AsyncExitStack`.

### Chat orchestration (`core/chat.py`, `core/cli_chat.py`)

`Chat` runs the core agent loop:

1. Add the user's processed query to the message list.
2. Call Claude with the full message history plus the list of all tools gathered from every connected client.
3. If Claude's `stop_reason` is `tool_use`, execute the requested tools, append the results as a user message, and loop again.
4. Otherwise, extract the final text and return it.

`CliChat` extends this with the document-specific behavior. `_process_query` first checks whether the input is a `/command`; if so it fetches the matching server prompt with the given `doc_id` and converts the prompt messages into Anthropic message params. If it's a normal query, `_extract_resources` scans for `@`-mentions, reads each mentioned document from the server, and wraps the query and the document contents into a single structured prompt that tells Claude to answer directly and not to reference the injected context.

### Tool execution (`core/tools.py`)

`ToolManager` aggregates tools across all clients into Anthropic's tool schema, finds the client that owns a requested tool, calls it, and packages the output (or any error) into `tool_result` blocks the model can consume. Tool failures are caught and returned as error results rather than crashing the loop.

### Claude wrapper (`core/claude.py`)

A small wrapper over the `anthropic` SDK. It builds the `messages.create` call with a `max_tokens` of 8000, optional system prompt, tools, temperature, and optional extended-thinking budget, and provides helpers to append user/assistant messages and pull text out of a response.

### CLI front end (`core/cli.py`, `main.py`)

`main.py` loads config from `.env` (requires `CLAUDE_MODEL` and `ANTHROPIC_API_KEY`, asserting on missing values), starts the document client plus any extra servers passed as arguments, and runs the app. `CliApp` builds the `prompt-toolkit` session: a `UnifiedCompleter` that suggests document ids after `@` and command names after `/`, a `CommandAutoSuggest` that hints a prompt's argument, and custom key bindings on `/`, `@`, and space that pop the completion menu at the right moments. On startup it refreshes the document and prompt lists from the server so completions reflect what the server actually exposes.

## Tech Stack

- **Language:** Python 3.10+ (`pyproject.toml`; README also notes 3.9+ compatibility)
- **AI / protocol:** Anthropic Claude via the `anthropic` SDK; Model Context Protocol via the `mcp[cli]` SDK and `FastMCP` server
- **CLI / UX:** `prompt-toolkit` (completion, history, key bindings, styling)
- **Supporting libraries:** `pydantic` (tool/argument schemas), `python-dotenv` (config)
- **Transport:** stdio JSON-RPC between client and server; `asyncio` with `AsyncExitStack`
- **Packaging / env:** `uv` (recommended) with `uv.lock`, or plain `pip`

## Getting Started

### Prerequisites

- Python 3.10 or newer
- An Anthropic API key
- `uv` (recommended) or `pip`

### Installation

```bash
git clone https://github.com/DCode-v05/MCP-Document-Assistant.git
cd MCP-Document-Assistant

# Option A — uv (recommended)
pip install uv
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install -e .

# Option B — pip
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install anthropic python-dotenv prompt-toolkit "mcp[cli]>=1.8.0"
```

### Configuration

Create a `.env` file in the project root:

```bash
ANTHROPIC_API_KEY="your_api_key_here"
CLAUDE_MODEL="claude-3-5-sonnet-latest"   # any Claude model id you have access to
# USE_UV=1                                # set to launch the server via "uv run"
```

Both `ANTHROPIC_API_KEY` and `CLAUDE_MODEL` are required — the app asserts on startup if either is missing.

### Running

```bash
# uv
uv run main.py

# plain python
python main.py
```

The client launches the MCP document server as a subprocess automatically. To attach extra MCP servers, pass their scripts as arguments: `uv run main.py path/to/other_server.py`.

## Usage

Once the `> ` prompt appears:

- **Ask a question** — just type. Example: `What does the report say about the condenser tower?`
- **Reference a document** — type `@` and pick from the menu; the contents are injected for you.
  > `Tell me about the budget in @financials.docx`
- **Run a server prompt** — type `/` to list commands, then pass a document id.
  > `/summarize_doc deposition.md`
  > `/format_doc plan.md`
- **Exit** — `Ctrl-C` ends the session.

The built-in sample documents are `deposition.md`, `report.pdf`, `financials.docx`, `outlook.pdf`, `plan.md`, and `spec.txt`. To use your own, edit the `docs` dictionary in `mcp_server.py`.

## Project Structure

```
MCP-Document-Assistant/
├── main.py              # Entry point: loads .env, starts clients, runs the CLI loop
├── mcp_server.py        # FastMCP "DocumentMCP" server: docs + tools/resources/prompts
├── mcp_client.py        # Async MCP client wrapper over the stdio ClientSession
├── core/
│   ├── chat.py          # Base agent loop (Claude call -> tool-use loop -> final text)
│   ├── cli_chat.py      # Document chat: @-mention injection, /command handling
│   ├── cli.py           # prompt-toolkit app: completer, key bindings, REPL
│   ├── claude.py        # Thin wrapper over the anthropic SDK
│   └── tools.py         # ToolManager: aggregate, route, and execute tool calls
├── pyproject.toml       # Project metadata and dependencies
├── uv.lock              # Locked dependency versions
└── README.md
```

---

## Contact

**Portfolio:** [Denistan](https://www.denistan.me)<br>
**LinkedIn:** [Denistan](https://www.linkedin.com/in/denistanb)<br>
**GitHub:** [DCode-v05](https://github.com/DCode-v05)<br>
**LeetCode:** [Denistan_B](https://leetcode.com/u/Denistan_B)<br>
**Email:** [denistanb05@gmail.com](mailto:denistanb05@gmail.com)

Made with ❤️ by **Denistan B**
