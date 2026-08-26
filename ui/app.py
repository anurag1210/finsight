import streamlit as st
import os
import tempfile
from src.generation.generator import generate_response, generate_response_stream
from src.ingestion.loader import load_pdf
from src.ingestion.chunker import chunk_documents
from src.ingestion.embedder import embed_and_store_chunks
from src.retrieval.vector_store import get_vector_store
from src.security.document_guard import is_financial_document

# Page Configuration
st.set_page_config(page_title='FinSight', layout="centered")
st.title("FinSight — SEC Filing Analysis")

# Sidebar — File Upload
with st.sidebar:
    st.header("Upload Filing")
    uploaded_file = st.file_uploader("Upload SEC Filing (PDF)", type=["pdf"])
    
    if uploaded_file:
        # Size check — 50MB max
        if uploaded_file.size > 50 * 1024 * 1024:
            st.error("File too large. Maximum 50MB.")
        else:
            if st.button("Process Filing"):
                with st.spinner("Validating document..."):
                    # Save to temp file for pdfplumber
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.getbuffer())
                        tmp_path = tmp.name
                    
                    # Load first page for classification
                    pages = load_pdf(tmp_path)
                    if not pages:
                        st.error("Could not read PDF.")
                        os.unlink(tmp_path)
                        st.stop()
                    
                    # Financial document check
                    is_financial, message = is_financial_document(pages[0].page_content)
                    if not is_financial:
                        st.error(message)
                        os.unlink(tmp_path)
                        st.stop()
                
                with st.spinner("Chunking and labelling..."):
                    chunks = chunk_documents(pages)
                
                with st.spinner("Embedding and storing..."):
                    # Clear existing ChromaDB
                    vector_store = get_vector_store()
                    existing = vector_store.get()
                    if existing["ids"]:
                        vector_store.delete(ids=existing["ids"])
                    
                    embed_and_store_chunks(chunks)
                
                # Cleanup temp file
                os.unlink(tmp_path)
                
                # Clear chat history for new document
                st.session_state.messages = []
                st.success(f"✅ {uploaded_file.name} processed — {len(chunks)} chunks indexed. Start asking questions!")
    
    # Show current filing
    try:
        vs = get_vector_store()
        all_docs = vs.get()
        sources = set(m.get("source_file", m.get("source", "Unknown")) for m in all_docs["metadatas"])
        if sources:
            st.caption(f"Current filing: {', '.join(sources)}")
    except:
        pass


# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle User Input
if query := st.chat_input("Please ask a financial question..."):
    with st.chat_message("user"):
        st.markdown(query)
    
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("assistant"):
        response = st.write_stream(
            generate_response_stream(query, st.session_state.messages)
        )
    
    st.session_state.messages.append({"role": "assistant", "content": response})