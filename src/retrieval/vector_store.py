import os
import sys

try:
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ModuleNotFoundError:
    pass

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.config import OPENAI_API_KEY, EMBEDDING_MODEL, CHROMA_PERSIST_DIR, COLLECTION_NAME
import chromadb

_vector_store = None

print("Initializing the Vector Store DB", file=sys.stderr)

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        embedding_model = OpenAIEmbeddings(
            api_key=OPENAI_API_KEY,
            model=EMBEDDING_MODEL
        )
        
        chroma_host = os.getenv("CHROMA_HOST")
        
        if chroma_host:
            # Docker mode — connect to ChromaDB server
            chroma_port = int(os.getenv("CHROMA_PORT", "8100"))
            client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
            _vector_store = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=embedding_model,
                client=client,
            )
        else:
            # Local mode — use persist directory
            _vector_store = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=embedding_model,
                persist_directory=CHROMA_PERSIST_DIR,
            )
    return _vector_store