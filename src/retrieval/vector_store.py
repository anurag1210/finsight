#Importing the necessary packages
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.config import OPENAI_API_KEY, EMBEDDING_MODEL, CHROMA_PERSIST_DIR, COLLECTION_NAME

_vector_store = None

print("Initializing the Vector Store DB")

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        embedding_model = OpenAIEmbeddings(
            api_key=OPENAI_API_KEY,
            model=EMBEDDING_MODEL
        )
        _vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embedding_model,
            persist_directory=CHROMA_PERSIST_DIR
        )
    return _vector_store

