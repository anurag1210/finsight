import os
from dotenv import load_dotenv

load_dotenv()

#Loading the environment variables from the .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET")

# ChromaDB
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
COLLECTION_NAME = "finsight_documents"


# LLM Settings, defines which language model to use, the temperature for response generation, and the maximum tokens for the response
LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_TEMPERATURE = 0.1 #Why temperature is not set to 0? Because we want some level of creativity in the responses, especially when generating summaries or insights. A temperature of 0.1 allows for a bit of variability while still maintaining a focus on accuracy and relevance
MAX_TOKENS = 1000 #This is the maximum number of tokens that the LLM will generate in its response. Setting this to 1000 allows for detailed summaries and insights without overwhelming the user with too much information. It also helps to manage costs, as generating very long responses can be more expensive when using LLMs.

# Chunking Settings, defines how the documents are split into smaller pieces for embedding and retrieval
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval Settings, picks the top K most relevant chunks to be used as context for the LLM
TOP_K = 5

