from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.config import CHUNK_SIZE, CHUNK_OVERLAP,OPENAI_API_KEY
from openai import OpenAI



def chunk_documents(documents: list[Document]) -> list[Document]:
    """Split documents into smaller chunks for embedding."""

    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]

    )


    chunks=text_splitter.split_documents(documents)

    #Enumerate to get the index and the element from the loop
    for i ,chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i


    print(f"Split {len(documents)} pages into {len(chunks)} chunks")
    print(f"Chunk size: {CHUNK_SIZE}, Overlap: {CHUNK_OVERLAP}")

    chunks = add_context_labels(chunks)
    return chunks


def add_context_labels(chunks: list[Document]) -> list[Document]:
    """Prepend a context label to each chunk using LLM."""
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    print(f"Adding context labels to {len(chunks)} chunks...")
    
    for i, chunk in enumerate(chunks):
        source = chunk.metadata.get("source", "SEC filing")
        page = chunk.metadata.get("page", "unknown")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=100,
            messages=[
                {
                    "role": "system",
                    "content": "You are a document labeller. Given a chunk from an SEC 10-K filing, write a 1-2 sentence description of what this chunk contains. Be specific — mention the company name, the type of data (revenue, expenses, risk factors, etc.), and the time period if visible. No preamble, just the description."
                },
                {
                    "role": "user",
                    "content": chunk.page_content
                }
            ]
        )
        
        label = response.choices[0].message.content.strip()
        chunk.metadata["original_content"] = chunk.page_content
        chunk.page_content = f"{label}\n\n{chunk.page_content}"
        
        if (i + 1) % 50 == 0:
            print(f"  Labelled {i + 1}/{len(chunks)} chunks...")
    
    print(f"Context labels added to all {len(chunks)} chunks.")
    return chunks



if __name__=="__main__":
    from src.ingestion.loader import load_all_documents

    docs = load_all_documents()
    chunks = chunk_documents(docs) 

    print(f"\nChunk 0 preview:")
    print(f"Metadata: {chunks[0].metadata}")
    print(f"Content: {chunks[0].page_content[:300]}...")
    print(f"\nChunk 1 preview:")
    print(f"Content: {chunks[1].page_content[:300]}...")
