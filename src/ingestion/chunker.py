from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.config import CHUNK_SIZE, CHUNK_OVERLAP



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
