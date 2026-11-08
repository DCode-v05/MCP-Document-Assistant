# MCP Document Assistant

A terminal chat client where Claude works on a set of documents held by a local MCP server. Mention a document with `@` to inject its contents into your question, or run a `/command` to trigger a prompt defined on the server.

The documents are a small in-memory set of samples (`deposition.md`, `report.pdf`, `financials.docx`, `outlook.pdf`, `plan.md`, `spec.txt`), so this is really a compact reference for wiring an LLM CLI to an MCP server: the client/server split, the tool-use loop, context injection and prompt-toolkit autocompletion. It was part of a series of MCP exercises I did.

## How it works

Two processes talk MCP over stdio.

**Server (`mcp_server.py`)** is a `FastMCP` server named `DocumentMCP` with a `docs` dictionary and all three MCP primitives:

- Tools: `read_doc(doc_id)` and `edit_doc(doc_id, old_str, new_str)`, a plain string replace.
- Resources: `docs://documents` (list of ids as JSON) and `docs://document/{doc_id}` (text).
- Prompts: `summarize_doc` and `format_doc`. The latter asks Claude to rewrite the document as Markdown and apply it with `edit_doc`.

**Client**

- `mcp_client.py` wraps `ClientSession` and `stdio_client`. It starts the server as a subprocess (`python mcp_server.py`, or `uv run mcp_server.py` when `USE_UV=1`) and offers `list_tools`, `call_tool`, `list_prompts`, `get_prompt` and `read_resource`.
- `core/chat.py` is the agent loop. It calls Claude with the history and every connected client's tools, runs the tools when `stop_reason` is `tool_use`, appends the results and repeats until it gets a text answer.
- `core/cli_chat.py` adds the document handling. A `/command` fetches the server prompt for the given document id. Otherwise `@` mentions are read from the server and wrapped into the prompt as `<document>` blocks.
- `core/tools.py` (`ToolManager`) turns MCP tools into Anthropic tool schemas, routes each call to the client that owns the tool, and returns failures as error results instead of crashing.
- `core/claude.py` is a thin wrapper over the `anthropic` SDK (`max_tokens` 8000).
- `core/cli.py` is the prompt-toolkit app: completion for document ids after `@` and command names after `/`, plus key bindings.

`main.py` also accepts extra server scripts as arguments (`uv run main.py other_server.py`) and aggregates their tools.

## Setup

Needs Python 3.10+ and an Anthropic API key.

```bash
uv venv
uv pip install -e .
```

or with pip: `pip install anthropic python-dotenv prompt-toolkit "mcp[cli]>=1.8.0"`.

Create `.env`:

```
ANTHROPIC_API_KEY=your_key
CLAUDE_MODEL=a_claude_model_id
# USE_UV=1
```

`main.py` asserts that both `ANTHROPIC_API_KEY` and `CLAUDE_MODEL` are set. Run it with:

```bash
uv run main.py
```

or `python main.py`.

## Usage

At the `> ` prompt:

```
What does the report say about the condenser tower?
Tell me about the budget in @financials.docx
/summarize_doc deposition.md
/format_doc plan.md
```

`Ctrl-C` exits. To use your own documents, edit the `docs` dictionary in `mcp_server.py`.

## Structure

```
main.py         entry point
mcp_server.py   DocumentMCP server
mcp_client.py   stdio MCP client wrapper
core/           agent loop, CLI chat, CLI app, tool manager, Claude wrapper
pyproject.toml, uv.lock
```
