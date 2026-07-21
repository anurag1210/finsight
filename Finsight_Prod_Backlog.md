# 🔧 FinSight — Production Improvements Backlog
> Things identified during load testing, security testing, interview prep, and gap analysis
> Last Updated: 21st July 2026

---

## ✅ COMPLETED

### ~~10. Authentication Layer~~ ✅ SHIPPED — 21st July 2026
- API key authentication on `/query` endpoint using FastAPI APIKeyHeader
- Pydantic v2 field_validator — rejects empty, whitespace, short, long queries
- Secure key generation via `secrets.token_urlsafe(32)`
- Key stored in `.env` — never hardcoded
- `.env.example` added to repo
- Full README documentation with screenshots
- Tested: 403 without key, 200 with key, Swagger UI integration

---

## Priority 1 — HIGH (Implement first, most impact)

### 1. Retry Logic with Exponential Backoff
**Why:** Currently any OpenAI API failure bubbles up as a 500 error to the user
**What to implement:**
- Exponential backoff: attempt 1 → wait 1s → attempt 2 → wait 2s → attempt 3 → wait 4s
- Maximum 3-4 retries before failing gracefully
- Retry on: 429 rate limit, 503 service unavailable, timeout errors
- Do NOT retry on: 400 bad request, guardrail rejections, malformed inputs
- User-facing message on final failure: "I'm having trouble reaching the AI service right now, please try again in a moment"

**Library:** tenacity
**Effort:** 2-3 hours

---

### 2. Redis Semantic Caching
**Why:** Load testing showed OpenAI API latency is the bottleneck — repeated/similar queries hit OpenAI every time
**What to implement:**
- Redis cache layer in front of LLM generation step
- cosine similarity > 0.92 threshold → return cached response
- Expected improvement: ~80% latency reduction on cache hits
**Effort:** 4-5 hours

---

### 3. Per-Stage Latency Logging with Correlation IDs
**Why:** Current logs only show HTTP request/response — no visibility into which pipeline stage is slow
**What to implement:**
- Log timestamp before/after: input guardrail, ChromaDB retrieval, grading, OpenAI call, output guardrail
- Structured JSON logging with correlation ID per request
- Log token usage per request
**Effort:** 2-3 hours

---

## Priority 2 — MEDIUM

### 4. Async Task Queue (Celery + Redis)
**Why:** FastAPI handles LLM calls synchronously — connections time out under concurrent load
**Architecture:** User → FastAPI → Redis Queue → Celery Worker → OpenAI. Return 202 immediately, client polls for result.
**Effort:** 6-8 hours

---

### 5. Enable Streaming (stream=True)
**Why:** LangSmith traces revealed streaming=False — entire response generated before anything sent to client
**Fix:** Set stream=True on ChatOpenAI — tokens returned progressively, reduces perceived latency, prevents timeouts
**Effort:** 1-2 hours

---

### 6. Request Timeout Middleware
**Why:** LangSmith showed a ghost request running for 1+ hour — client disconnected but server never cancelled
**Fix:** 30 second timeout middleware, return 504 on timeout, cancel downstream OpenAI calls
**Effort:** 1 hour

---

### 7. OpenAI Chat Completions Logging
**Why:** Individual request logs not available in OpenAI dashboard by default
**Fix:** Add store=True to ChatOpenAI calls
**Effort:** 30 minutes

---

### 8. Prometheus Metrics Endpoint
**Metrics:** Per-node latency, guardrail trigger rate, reformulation frequency, cache hit rate, queue depth
**Effort:** 2-3 hours

---

### 9. Evidently AI — Embedding Drift Detection
**Why:** SEC filings update quarterly — flag when embedding distribution shifts, trigger re-index
**Effort:** 2-3 hours

---

## Priority 3 — LOWER

### 11. Kubernetes Deployment Manifests
**What:** Deployment, Service, ConfigMap, HPA — add k8s/ directory to repo
**Effort:** 3-4 hours

---

### 12. pdfplumber Ingestion Fix
**Why:** Apple_2025.pdf fails — LTRect bug, 65/65 pages skipped
**Fix:** Investigate version compatibility, rebuild ChromaDB after fix (page i+1 already in place)
**Effort:** 2-4 hours

---

### 13. RAGAS Evaluation Pipeline
**What:** 15-20 QA pairs, context_recall/precision/faithfulness/answer_relevancy, integrate into CI/CD as quality gate
**Effort:** 2-3 hours

---

## Post-Generation Feedback Loop

### 14. Thumbs Up/Down Feedback
**What:** Button on every response → stored with LangSmith trace ID → enables debugging any flagged answer
**Effort:** 2 hours

---

### 15. Human-in-the-Loop Review Queue
**What:** Low confidence answers flagged for manual review before shown to user
**Effort:** 4-5 hours

---

### 16. Bad Answers → RAGAS Evaluation Dataset
**What:** Flagged wrong answers → RAGAS → identify retrieval vs generation failure → fix root cause
**Effort:** 2 hours

---

## Technical Gap Closure Items

### 17. Hybrid Search (BM25 + Vector, merged via RRF)
**Why:** Pure semantic search misses exact keyword matches — critical for financial terminology
**What:** BM25 sparse + ChromaDB dense, merge via Reciprocal Rank Fusion, evaluate with RAGAS before/after
**Effort:** 4-5 hours

---

### 18. HNSW Vector Index Internals and Tuning
**Why:** Using ChromaDB default HNSW settings — not tuned for production
**What:** Understand ef_construction, ef_search, M parameters. Tune and document recall vs latency trade-off.
**Effort:** 3-4 hours

---

### 19. LangGraph Persistence/Checkpointing
**Why:** enterprise-doc-agent has no state persistence — agent fails mid-execution, state lost
**What:** SqliteSaver (dev) or RedisSaver (prod) — agent state survives interruptions, enables human-in-the-loop pause/resume
**Effort:** 2-3 hours

---

### 20. Recency-Weighted Retrieval / Time-Decay Scoring
**Why:** Newer SEC filings should rank higher than older ones
**What:** score = similarity_score x e^(-λ x days_since_ingestion). Tune decay factor λ per document type.
**Effort:** 3-4 hours

---

### 21. MCP Hands-On Implementation
**Why:** Currently theory-only — identified gap in Fitch Round 1
**What:** FastMCP server exposing enterprise-doc-agent retrieval as MCP tool. One evening, working prototype.
**Effort:** 2-3 hours

---

## Scale Architecture (Millions of Documents)

### 22. Production Scale RAG Architecture
- S3 hash-based prefix storage (bucket/ea/ff/doc1.pdf) — prevents key hotspotting
- Postgres for chunks — source of truth, re-embed without touching raw documents
- Elasticsearch — BM25 + semantic + native sharding
- Multiple parallel ingestors + SQS coordination (visibility timeout prevents duplicates)
- S3 events → Lambda → SQS → ingestor for incremental updates
- Chunk versioning for audit trail — "what did 2024 filing say vs 2025?"
- Dead letter queue for failed documents
- Cross-encoder re-ranking — top 20 ANN candidates → top 5 to LLM

---

## Content Pipeline

### 23. YouTube Video — "Adding Layer on Layer to a RAG App"
**Arc:** Working app → Locust load test (93% failures, teaching moment) → fix and rerun → diagnose bottleneck → OpenAI dashboard evidence → security testing → fix guardrails → production roadmap
**Why it performs:** Load testing RAG is underserved. Real failures, not happy path. Empty string bug is great hook.

---

## Interview Talking Points Summary

| Enhancement | Current State | Production Fix | Key Interview Line |
|-------------|--------------|----------------|-------------------|
| ✅ Auth | No auth | API key via APIKeyHeader | "Protected at API boundary, not UI layer" |
| Retry logic | 500 on failure | Tenacity exponential backoff | "Distinguish transient vs permanent" |
| Caching | Every query hits OpenAI | Redis semantic cache 0.92 | "80% latency reduction on hits" |
| Logging | HTTP only | Per-stage JSON + correlation ID | "Can't diagnose without per-stage latency" |
| Async | Synchronous blocking | Celery + Redis Queue | "Return 202, poll for result" |
| Streaming | False — blocks connection | stream=True | "Confirmed via LangSmith trace" |
| Timeout | Ghost requests run forever | 30s middleware, 504 | "1hr ghost request in LangSmith" |
| Feedback | None | Thumbs up/down → LangSmith | "Close loop from signal to root cause" |
| Hybrid search | Semantic only | BM25 + vector + RRF | "Pure semantic misses financial terms" |
| MCP | Theory only | FastMCP server | "Exposing retrieval as MCP tool" |
| Scale | One document | S3 + Postgres + ES + SQS | "SQS prevents duplicate processing" |

---

## Weekly Shipping Log

| Week | Feature | Status |
|------|---------|--------|
| 21st July 2026 | API Key Authentication | ✅ Shipped |
| 28th July 2026 | TBD | ⬜ Pending |
| 4th Aug 2026 | TBD | ⬜ Pending |
| 11th Aug 2026 | TBD | ⬜ Pending |

---

## Key Engineering Principles

1. Retry transient, fail fast on permanent
2. Degrade gracefully — helpful message not raw 500
3. Instrument before optimising — confirm bottleneck first
4. Cache at the right layer — before LLM not after retrieval
5. Correlation IDs — trace one request across all stages
6. Evidence-based diagnosis — isolation testing + external dashboard
7. Fail loudly for permanent failures — wrong input, security violations
8. Most powerful hallucination prevention is grounding — not guardrails
9. Query specificity directly impacts latency
10. streaming=False is a hidden bottleneck — check LangSmith attributes

---

*"The difference between a personal project and a production system is not the features — it's the operational maturity around it."*

*Last updated: 21st July 2026*