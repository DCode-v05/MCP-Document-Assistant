# MCP Document Assistant

**A command-line chat app that gives Anthropic's Claude direct, structured access to your local documents over the Model Context Protocol.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white) ![Anthropic Claude](https://img.shields.io/badge/Anthropic_Claude-D97757?style=flat&logo=anthropic&logoColor=white) ![MCP](https://img.shields.io/badge/Model_Context_Protocol-1.8+-000000?style=flat&logo=modelcontextprotocol&logoColor=white) ![FastMCP](https://img.shields.io/badge/FastMCP-server-4B8BBE?style=flat) ![prompt_toolkit](https://img.shields.io/badge/prompt__toolkit-CLI-2C3E50?style=flat) ![uv](https://img.shields.io/badge/uv-packaging-DE5FE9?style=flat&logo=astral&logoColor=white)

## Overview

This is a terminal chat client that lets Claude work against a set of local documents instead of an isolated chat box. Rather than pasting file contents into a prompt every time, you mention a document with `@` and the assistant pulls in its contents, or you run a `/command` that triggers a predefined workflow on the server side. Under the hood it talks to a local MCP server that owns the documents and exposes them through the three Model Context Protocol primitives: Resources, Tools and Prompts.

It's a focused, single-purpose app. The document store is a small in-memory set of sample files (a deposition, a report, financials, a spec and so on), so the project is really a compact working reference for how an LLM CLI wires up to an MCP server: the client/server split, the tool-use loop, context injection, and a prompt-toolkit UI with live autocompletion. It's module 5 ("Claude MCP") of a longer MCP learning series, and it's where I worked out the client-side agent loop and the `@`/`/` patterns that later carried over into bigger MCP projects.

## Key Features

- **Interactive Claude chat in the terminal.** A REPL-style loop (`> `) backed by `prompt-toolkit`, with in-memory history, live completion menus and inline auto-suggestions.
- **`@`-mention context injection.** Type `@` to open an autocomplete menu of available documents. Mentioned docs are read from the MCP server and injected into the prompt inside `<document>` tags before Claude sees the query.
- **`/`-command prompt workflows.** Type `/` to list server-defined prompts (`format_doc`, `summarize_doc`), pass a document id, and the server returns a ready-made instruction sequence that's appended to the conversation.
- **Tool-use loop.** Claude can call MCP tools on its own. The client runs each requested tool, feeds the result back, and repeats until Claude produces a final text answer.
- **Document tools.** `read_doc` (read a document's contents) and `edit_doc` (search-and-replace edit on a document).
- **Document resources.** A `docs://documents` list resource and a per-document `docs://document/{doc_id}` content resource, returned as JSON or plain text.
- **Server-side prompts.** `summarize_doc` (concise summary) and `format_doc` (rewrite a document as Markdown using the edit tool).
- **Extra servers from the command line.** The entry point can attach more MCP servers passed as arguments, and the tool manager aggregates tools across every connected client and routes each call to the client that owns the tool.
- **Cross-platform stdio transport.** Client and server talk over stdio JSON-RPC, with a Windows-specific asyncio event-loop policy so it runs on Windows as well as Unix.

## How It Works

The app is split into a client process (the CLI you talk to) and a server process (which owns the documents). They run separately and speak MCP over stdio.

### MCP Server (`mcp_server.py`)

A `FastMCP` server named `DocumentMCP`. It holds an in-memory `docs` dictionary of sample documents keyed by id (`deposition.md`, `report.pdf`, `financials.docx`, `outlook.pdf`, `plan.md`, `spec.txt`). It registers:

- **Tools:** `read_doc(doc_id)` returns a document's text; `edit_doc(doc_id, old_str, new_str)` does an in-place string replacement. Both raise a clear error if the id doesn't exist. Arguments are described with Pydantic `Field` metadata so the schema reaches the model.
- **Resources:** `docs://documents` returns the list of ids as JSON; `docs://document/{doc_id}` returns a single document's contents as plain text.
- **Prompts:** `summarize_doc(doc_id)` and `format_doc(doc_id)` return templated `UserMessage` instruction sequences. `format_doc` tells Claude to add headers, bullets and tables and to apply the changes via the edit tool without changing the meaning.

It runs with `mcp.run(transport="stdio")`.

### MCP Client (`mcp_client.py`)

A thin async wrapper around the MCP SDK's `ClientSession` and `stdio_client`. It starts the server as a subprocess (`python mcp_server.py`, or `uv run mcp_server.py` when `USE_UV=1`), initializes the session, and offers `list_tools`, `call_tool`, `list_prompts`, `get_prompt` and `read_resource`. `read_resource` decodes the first content block and parses JSON when the mime type is `application/json`. The client is an async context manager, so connect and cleanup are handled by an `AsyncExitStack`.

### Chat orchestration (`core/chat.py`, `core/cli_chat.py`)

`Chat` runs the core agent loop:

1. Add the user's processed query to the message list.
2. Call Claude with the full message history plus the tools gathered from every connected client.
3. If Claude's `stop_reason` is `tool_use`, run the requested tools, append the results as a user message, and loop again.
4. Otherwise, extract the final text and return it.

`CliChat` extends this with the document-specific behaviour. `_process_query` first checks whether the input is a `/command`. If so, it fetches the matching server prompt with the given `doc_id` and converts the prompt messages into Anthropic message params. For a normal query, `_extract_resources` scans for `@`-mentions, reads each mentioned document from the server, and wraps the query and the document contents into one structured prompt that tells Claude to answer directly and not to mention the injected context.

### Tool execution (`core/tools.py`)

`ToolManager` aggregates tools across all clients into Anthropic's tool schema, finds the client that owns a requested tool, calls it, and packages the output (or any error) into `tool_result` blocks the model can use. Tool failures are caught and returned as error results instead of crashing the loop.

### Claude wrapper (`core/claude.py`)

A small wrapper over the `anthropic` SDK. It builds the `messages.create` call with `max_tokens` of 8000, an optional system prompt, tools, temperature and an optional extended-thinking budget, and has helpers to append user/assistant messages and pull text out of a response.

### CLI front end (`core/cli.py`, `main.py`)

`main.py` loads config from `.env` (it requires `CLAUDE_MODEL` and `ANTHROPIC_API_KEY` and asserts on missing values), starts the document client plus any extra servers passed as arguments, and runs the app. `CliApp` builds the `prompt-toolkit` session: a `UnifiedCompleter` that suggests document ids after `@` and command names after `/`, a `CommandAutoSuggest` that hints a prompt's argument, and custom key bindings on `/`, `@` and space that open the completion menu at the right moments. On startup it refreshes the document and prompt lists from the server so completions match what the server actually exposes.

## Tech Stack

- **Language:** Python 3.10+ (`requires-python` in `pyproject.toml`)
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

# Option A: uv (recommended)
pip install uv
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install -e .

# Option B: pip
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install anthropic python-dotenv prompt-toolkit "mcp[cli]>=1.8.0"
```

### Configuration

Create a `.env` file in the project root:

```bash
ANTHROPIC_API_KEY="your_api_key_here"
CLAUDE_MODEL="your_claude_model_id"       # any Claude model id you have access to
# USE_UV=1                                # set to launch the server via "uv run"
```

Both `ANTHROPIC_API_KEY` and `CLAUDE_MODEL` are required. The app asserts on startup if either is missing.

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

- **Ask a question.** Just type. Example: `What does the report say about the condenser tower?`
- **Reference a document.** Type `@` and pick from the menu; the contents are injected for you.
  > `Tell me about the budget in @financials.docx`
- **Run a server prompt.** Type `/` to list commands, then pass a document id.
  > `/summarize_doc deposition.md`
  > `/format_doc plan.md`
- **Exit.** `Ctrl-C` ends the session.

The built-in sample documents are `deposition.md`, `report.pdf`, `financials.docx`, `outlook.pdf`, `plan.md` and `spec.txt`. To use your own, edit the `docs` dictionary in `mcp_server.py`.

## Project Structure

```
MCP-Document-Assistant/
├── main.py              # Entry point: loads .env, starts clients, runs the CLI loop
├── mcp_server.py        # FastMCP "DocumentMCP" server: docs + tools/resources/prompts
├── mcp_client.py        # Async MCP client wrapper over the stdio ClientSession
├── core/
│   ├── __init__.py
│   ├── chat.py          # Base agent loop (Claude call -> tool-use loop -> final text)
│   ├── cli_chat.py      # Document chat: @-mention injection, /command handling
│   ├── cli.py           # prompt-toolkit app: completer, key bindings, REPL
│   ├── claude.py        # Thin wrapper over the anthropic SDK
│   └── tools.py         # ToolManager: aggregate, route, and execute tool calls
├── pyproject.toml       # Project metadata and dependencies
├── uv.lock              # Locked dependency versions
├── .gitignore
└── README.md
```

---

## Contact

<table>
  <tr><td><b>Portfolio:</b> <a href="https://www.denistan.me">Denistan</a></td><td><b>LinkedIn:</b> <a href="https://www.linkedin.com/in/denistanb">denistanb</a></td></tr>
  <tr><td><b>GitHub:</b> <a href="https://github.com/DCode-v05">DCode-v05</a></td><td><b>LeetCode:</b> <a href="https://leetcode.com/u/Denistan_B">Denistan_B</a></td></tr>
  <tr><td colspan="2" align="center"><b>Email:</b> <a href="mailto:denistanb05@gmail.com">denistanb05@gmail.com</a></td></tr>
</table>

Made with ❤️ by **Denistan B**
