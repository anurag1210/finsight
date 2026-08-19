"""FinSight MCP Server — exposes SEC filing analysis as tools for AI agents."""
import os
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

from mcp.server import MCPServer
from src.retrieval.retriever import retrieve_hybrid
from src.generation.generator import generate_response

# Create the MCP server
mcp = MCPServer(
    name="FinSight",
    description="SEC filing analysis tools — query financial data from 10-K filings"
)

@mcp.tool()
def query_filing(question: str) -> str:
    """Ask a question about SEC 10-K filings and get a grounded answer.
    
    Uses hybrid retrieval (BM25 + vector + RRF) with cross-encoder reranking
    to find relevant chunks, then generates an answer using GPT-4o-mini.
    
    Args:
        question: Natural language question about the filing 
                  (e.g. "What was Apple's total revenue in 2025?")
    """
    return generate_response(question)

@mcp.tool()
def get_filing_context(question: str) -> str:
    """Retrieve relevant chunks from SEC filings without generating an answer.
    
    Returns the raw retrieved context so the calling agent can do its own 
    reasoning. Uses hybrid search + cross-encoder reranking, returns top 5 chunks.
    
    Args:
        question: Natural language query to search the filing
    """
    docs = retrieve_hybrid(question)
    
    chunks = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "N/A")
        chunks.append(f"[Chunk {i}] Source: {source}, Page: {page}\n{doc.page_content}")
    
    return "\n\n---\n\n".join(chunks)


@mcp.resource("filings://available")
def list_filings() -> str:
    """List all SEC filings currently available in the system."""
    from src.retrieval.vector_store import get_vector_store
    
    vector_store = get_vector_store()
    all_docs = vector_store.get()
    
    sources = set()
    for meta in all_docs["metadatas"]:
        if "source" in meta:
            sources.add(meta["source"])
    
    if not sources:
        return "No filings currently loaded."
    
    return "Available filings:\n" + "\n".join(f"- {s}" for s in sorted(sources))


if __name__ == "__main__":
    mcp.run()