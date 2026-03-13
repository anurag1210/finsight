import os
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import pdfplumber



def load_pdf(file_path: str, metadata: dict = None) -> list[Document]:
    """Load a single PDF and return list of documents with metadata."""
    pages = []
    
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                # Remove common browser PDF headers (date/time + filename pattern)
                text = re.sub(r'\d{2}/\d{2}/\d{4},\s*\d{2}:\d{2}\s*\S+', '', text).strip() 

                page_metadata = {
                    "source": file_path,
                    "page": i,
                    "total_pages": len(pdf.pages),
                }
                if metadata:
                    page_metadata.update(metadata)
                
                pages.append(Document(
                    page_content=text,
                    metadata=page_metadata
                ))
    
    return pages


def load_all_documents(data_dir: str = "data/raw")-> list[Document]:
    """Load all PDFs from the data directory."""
    all_documents=[]

    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            file_path=os.path.join(data_dir,filename)

            # Extract company name from filename
            company_name=filename.replace(".pdf", "").replace("_", " ").title()
          
            #Adding the metadata to the document
            metadata = {
                "source_file": filename,
                "company": company_name,
            }

            documents = load_pdf(file_path, metadata)
            all_documents.extend(documents)
            print(f"Loaded {len(documents)} pages from {filename}")
    
    print(f"\nTotal documents loaded: {len(all_documents)}")
    return all_documents



if __name__ == "__main__":
    docs = load_all_documents(data_dir)
    # Print first page as a test
    if docs:
        print(f"\page 10 preview:")
        #print(f"Metadata: {docs[0].metadata}")
        print(f"Content: {docs[1].page_content[:500]}...")


        

