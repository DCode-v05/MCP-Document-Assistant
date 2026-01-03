from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")
docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# Tool to read a document
@mcp.tool(name="read_doc", description="Reads the contents of a document and return it as a string.")
def read_doc(doc_id: str=Field(description="Id of the document to read")) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    return docs[doc_id]

# Tool to edit a document
@mcp.tool(name="edit_doc", description="Edits the contents of a document.")
def edit_doc(doc_id: str=Field(description="Id of the document to edit"), old_str: str=Field(description="String to be replaced"), new_str: str=Field(description="String to replace with")):
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)

# Resource to list all document ids
@mcp.resource("docs://documents", mime_type="application/json", description="Returns a list of all document ids.")
def list_docs() -> list[str]:
    return list(docs.keys())

# Resource to get a particular document's contents
@mcp.resource("docs://document/{doc_id}", mime_type="text/plain", description="Returns the contents of a particular document.")
def get_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    return docs[doc_id]

# Prompt to rewrite a document in markdown format
@mcp.prompt(name="format_doc", description="Rewrite a document in markdown format.")
def format_doc(doc_id: str=Field(description="Id of the document to rewrite")) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables, etc as necessary. Feel free to add in extra text, but don't change the meaning of the report.
    Use the 'edit_document' tool to edit the document. After the document has been edited, respond with the final version of the doc. Don't explain your changes.
    """
    return [base.UserMessage(prompt)]

# Prompt to summarize a document
@mcp.prompt(name="summarize_doc", description="Summarize the contents of a document.")
def summarize_doc(doc_id: str=Field(description="Id of the document to summarize")) -> list[base.Message]:
    prompt = f"""
    Your goal is to summarize the contents of a document.

    The id of the document you need to summarize is:
    <document_id>
    {doc_id}
    </document_id>

    Provide a concise summary of the document's key points.
    """
    return [base.UserMessage(prompt)]

if __name__ == "__main__":
    mcp.run(transport="stdio")