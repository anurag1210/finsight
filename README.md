# finsight
A RAG system that lets business professionals ask natural language questions across SEC financial filings (10-K annual reports). Users upload or query against pre-loaded financial documents and get accurate, cited answers.


finsight/
├── README.md                    # Portfolio-worthy documentation
├── docker-compose.yml           # One-command setup
├── Dockerfile
├── requirements.txt
├── .env.example                 # Template for API keys
├── src/
│   ├── __init__.py
│   ├── config.py                # All configuration
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py            # PDF loading and parsing
│   │   ├── chunker.py           # Chunking strategies
│   │   └── embedder.py          # Embedding generation
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vector_store.py      # ChromaDB operations
│   │   ├── retriever.py         # Search logic (semantic + keyword)
│   │   └── reranker.py          # Optional reranking
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── prompt_templates.py  # All prompts (system, user, few-shot)
│   │   └── generator.py         # LLM response generation
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── eval_dataset.py      # Custom test Q&A pairs
│   │   ├── metrics.py           # Retrieval & generation metrics
│   │   └── run_eval.py          # Evaluation runner
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── routes.py            # API endpoints
│   │   └── models.py            # Pydantic request/response models
│   └── security/
│       ├── __init__.py
│       ├── input_guard.py       # Input validation & prompt injection prevention
│       └── output_guard.py      # Output checking
├── ui/
│   └── app.py                   # Streamlit frontend
├── data/
│   ├── raw/                     # Original SEC filings (PDFs)
│   └── processed/               # Chunked and processed documents
├── tests/
│   ├── test_chunker.py
│   ├── test_retriever.py
│   └── test_generator.py
├── evaluation_results/          # Stored evaluation outputs
├── docs/
│   └── ARCHITECTURE.md          # Architecture Decision Records
└── notebooks/
    └── exploration.ipynb        # Experimentation notebookclear




Files and their meaning:


__init__.py — makes each folder a Python package so you can import between them.

config.py — centralised configuration. API keys, chunk sizes, model names, database paths. Change settings in one place, not scattered across files.
Ingestion (PDF → searchable chunks):

loader.py — reads PDF files, extracts text page by page, attaches metadata (company name, year)

chunker.py — splits extracted text into smaller pieces (chunks) for embedding

embedder.py — converts chunks into vectors using the embedding model

Retrieval (finding relevant chunks):

vector_store.py — ChromaDB operations. Store vectors, delete, update
retriever.py — search logic. Takes a query, finds the most relevant chunks
reranker.py — optional cross-encoder reranking for more precise results

Generation (producing answers):

prompt_templates.py — all your system prompts, user templates, few-shot examples in one place
generator.py — takes retrieved chunks + query, calls the LLM, returns the answer

Evaluation (proving it works):

eval_dataset.py — your custom test questions with expected answers
metrics.py — precision, recall, faithfulness calculations
run_eval.py — runs all test questions through the pipeline and produces a report

API (serving it):

main.py — FastAPI app initialisation
routes.py — your endpoints (query, upload, health check)
models.py — Pydantic models defining request/response shapes

Security:

input_guard.py — checks user input for prompt injection before it reaches the LLM
output_guard.py — checks LLM response before returning to user

The rest:

ui/app.py — Streamlit frontend
tests/ — unit tests for critical components
docs/ARCHITECTURE.md — your architecture decision records
notebooks/exploration.ipynb — for experimenting before writing production code




-----TO BE DONE------

Add SEC EDGAR API integration as a feature — once the core pipeline works, add an endpoint where users can type a company ticker and your system fetches the filing automatically.