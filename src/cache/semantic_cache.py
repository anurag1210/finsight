#Importing the necessary packages

import json
import numpy as np
import redis
from openai import OpenAI
from src.config import (
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_TTL,
    CACHE_SIMILARITY_THRESHOLD
)

# Redis connection
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)


# OpenAI client for embeddings
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str) -> list[float]:
    """Convert text to embedding vector using OpenAI."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """Calculate cosine similarity between two vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def get_cached_response(query: str) -> str | None:
    """
    Check Redis for a semantically similar cached query.
    Returns cached answer if similarity > threshold, else None.
    """
    query_embedding = get_embedding(query)

    # Get all cached keys
    cached_keys = redis_client.keys("finsight:cache:*")

    best_similarity = 0.0
    best_answer = None

    for key in cached_keys:
        cached_data = redis_client.get(key)
        if not cached_data:
            continue

        cached = json.loads(cached_data)
        cached_embedding = cached["embedding"]

        similarity = cosine_similarity(query_embedding, cached_embedding)

        if similarity > best_similarity:
            best_similarity = similarity
            best_answer = cached["answer"]

    if best_similarity >= CACHE_SIMILARITY_THRESHOLD:
        print(f"Cache HIT — similarity: {best_similarity:.4f}")
        return best_answer

    print(f"Cache MISS — best similarity: {best_similarity:.4f}")
    return None


def cache_response(query: str, answer: str) -> None:
    """
    Store query embedding and answer in Redis.
    """
    query_embedding = get_embedding(query)

    cache_data = json.dumps({
        "query": query,
        "embedding": query_embedding,
        "answer": answer
    })

    # Use query hash as key
    import hashlib
    key = f"finsight:cache:{hashlib.md5(query.encode()).hexdigest()}"

    redis_client.setex(key, REDIS_TTL, cache_data)
    print(f"Cached response for: '{query[:50]}...'")



def clear_cache() -> int:
    """Clear all cached responses. Returns number of keys deleted."""
    keys = redis_client.keys("finsight:cache:*")
    if keys:
        return redis_client.delete(*keys)
    return 0
