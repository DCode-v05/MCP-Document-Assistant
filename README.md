# MCP Document Assistant

## Project Description
This project is a powerful command-line interface (CLI) application that extends the capabilities of Anthropic's Claude AI model by integrating it with your local document environment. Using the **Model Context Protocol (MCP)**, it enables seamless interaction between the AI and your local files, allowing for document-aware code assistance, intelligent retrieval, and automated content manipulation. By bridging the gap between remote AI intelligence and local context, it provides a highly efficient workflow for managing and querying documentation.

---

## Project Details

### Problem Statement
Developers and knowledge workers often need to perform complex tasks on local documents—such as summarization, reformatting, or specific data extraction—while leveraging the reasoning capabilities of Large Language Models (LLMs). Manually copying context into chat windows is inefficient and error-prone. This project solves that by establishing a direct protocol for the AI to "read" and "act" upon local files securely.

### Key Features
- **Interactive Chat Interface**: A robust CLI chat session directly with Claude.
- **Context injection**: Easily fetch and include document contents in your prompt using the `@` symbol (e.g., `@report.pdf`).
- **Command Execution**: Trigger predefined prompt workflows using the `/` prefix (e.g., `/summarize`).
- **Tool Integration**:
  - **Read**: The AI can read file contents on demand.
  - **Edit**: The AI can perform precise search-and-replace edits on documents.
  - **Format**: Automated reformatting of documents into Markdown.

### Architecture
*   **MCP Server (`mcp_server.py`)**: Acts as the custodian of the data, exposing documents as *Resources* and providing *Tools* (read/edit) and *Prompts* (summarize/format) to the client.
*   **MCP Client (`mcp_client.py`)**: Manages the connection to the server and handles the protocol communication (JSON-RPC) to execute tools and retrieve resources.
*   **CLI Interface (`main.py`)**: The user-facing frontend that orchestrates the chat session, parsing user input for special commands and formatting the output.

---

## Tech Stack
- **Languages**: Python 3.9+
- **Core Libraries**:
  - `anthropic`: For communicating with the Claude API.
  - `mcp`: The official Model Context Protocol SDK.
  - `prompt-toolkit`: For the rich CLI user experience (history, auto-completion).
  - `python-dotenv`: For environment configuration.
  - `pydantic`: For data validation and schema definition.
- **Environment Management**: `uv` (recommended) or `pip`.

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/DCode-v05/MCP-Document-Assistant.git
cd MCP-Document-Assistant
```

### 2. Configure Environment
Create a `.env` file in the root directory and add your Anthropic API key:
```bash
ANTHROPIC_API_KEY="your_api_key_here"
```

### 3. Install dependencies
**Option A: Using uv (Recommended)**
```bash
pip install uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

**Option B: Standard pip**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install anthropic python-dotenv prompt-toolkit "mcp[cli]==1.8.0"
```

### 4. Run the Application
```bash
# If using uv
uv run main.py

# If using standard python
python main.py
```

---

## Usage
- **Chat**: Type natural language queries to ask Claude questions.
- **Resources**: Type `@` to trigger the auto-complete menu for available documents.
  > `Tell me about the budget in @financials.docx`
- **Commands**: Type `/` to see available commands (prompts).
  > `/summarize deposition.md`
- **Exiting**: Type `quit` to end the session.

---

## Project Structure
```
MCP-Document-Assistant/
│
├── core/                   # Core application logic (if any)
├── main.py                 # Application entry point and CLI loop
├── mcp_client.py           # Client implementation for MCP connection
├── mcp_server.py           # Server implementation defining tools & resources
├── .env                    # Environment variables (API Key)
├── .gitignore              # Git ignore rules
├── pyproject.toml          # Project configuration and dependencies
├── uv.lock                 # Dependency lock file
└── README.md               # Project documentation
```

---

## Contributing

Contributions are welcome! To contribute:
1.  Fork the repository
2.  Create a new branch:
    ```bash
    git checkout -b feature/your-feature
    ```
3.  Commit your changes:
    ```bash
    git commit -m "Add your feature"
    ```
4.  Push to your branch:
    ```bash
    git push origin feature/your-feature
    ```
5.  Open a pull request describing your changes.

---

## Contact
- **GitHub:** [DCode-v05](https://github.com/DCode-v05)
- **Email:** denistanb05@gmail.com
