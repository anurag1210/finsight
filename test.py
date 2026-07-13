import os
from langchain_community.document_loaders import PyPDFLoader


data_dir="/Users/anuraggupta/projects/finsight/data/raw"

if __name__ == "__main__":
    from langchain_community.document_loaders import PyPDFLoader
    loader = PyPDFLoader("/Users/anuraggupta/projects/finsight/data/raw/Apple_2025.pdf")
    pages = loader.load()
    print(repr(pages[10].page_content[:300]))