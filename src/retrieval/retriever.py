#Code to Retrieve thevector DB embeddings from the user query
from src.retrieval.vector_store import get_vector_store
from src.config import TOP_K, RERANK_TOP_K, RERANK_FINAL_K, RERANK_MODEL
#BM25 retriever logic added
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document

#Imports for ReRankers 
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

_cross_encoder = HuggingFaceCrossEncoder(model_name=RERANK_MODEL)
_compressor = CrossEncoderReranker(model=_cross_encoder, top_n=RERANK_FINAL_K)

#Method to retrieve the embeddings from the vector db
def retrieve_vectordb(user_query,filter=None):
    vector_store=get_vector_store()
    if filter:
        results = vector_store.similarity_search_with_score(user_query, k=TOP_K, filter=filter)
    else:
        results = vector_store.similarity_search_with_score(user_query, k=TOP_K)    
    
    return results

def retrieve_hybrid(user_query, k=RERANK_TOP_K):
    """Hybrid retrieval: BM25 keyword + ChromaDB semantic, merged via RRF."""

    # Step 1 — get vector store
    vector_store = get_vector_store()

    # Step 2 — load all chunks from ChromaDB for BM25 index
    all_docs = vector_store.get()
    documents = all_docs['documents']
    metadatas = all_docs['metadatas']

    docs = [
        Document(page_content=documents[i], metadata=metadatas[i])
        for i in range(len(documents))
    ]

    # Step 3 — build BM25 retriever from all chunks
    bm25_retriever = BM25Retriever.from_documents(docs)
    bm25_retriever.k = k

    # Step 4 — build ChromaDB vector retriever
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": k})

    # Step 5 — combine via EnsembleRetriever (applies RRF automatically)
    ensemble = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=[0.5, 0.5]
    )
    
    # Step 6 — rerank
    reranking_retriever = ContextualCompressionRetriever(
        base_compressor=_compressor,
        base_retriever=ensemble,
    )

    # Step 7 — retrieve with re-ranking
    results = reranking_retriever.invoke(user_query)
    return results


#Main block old logic with only the semantic search
# if __name__ == "__main__":
#         user_query=input('Input the User Query :')
#         results=retrieve_vectordb(user_query)

#         if results:
#             for res, score in results:
#                 print(f"Match: {res.page_content[:200]}... (Score: {score:.3f})")
#         else:
#                 print("No matching documents found.")

#Updated Main Block with the BM25 and and semantic search included

if __name__ == "__main__":
    user_query = input('Input the User Query :')
    results = retrieve_hybrid(user_query)

    if results:
        for doc in results:
            print(f"Match: {doc.page_content[:200]}...")
    else:
        print("No matching documents found.")