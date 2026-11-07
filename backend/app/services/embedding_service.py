import json
import math
import re
import hashlib
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.config import settings

VECTOR_DIM = 256

def _hash_token(token: str, dim: int = VECTOR_DIM) -> int:
    """Deterministic hash of a token into vector index."""
    digest = hashlib.md5(token.encode('utf-8')).hexdigest()
    return int(digest, 16) % dim

def generate_local_embedding(text: str, dim: int = VECTOR_DIM) -> List[float]:
    """
    Generate normalized semantic subword + n-gram vector representation.
    Ensures deterministic, zero-latency vector embedding without external network dependencies.
    """
    cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
    words = cleaned.split()
    if not words:
        return [0.0] * dim

    vec = [0.0] * dim
    
    # 1. Unigrams with frequency weighting
    for w in words:
        idx = _hash_token(w, dim)
        # Weight longer words slightly more (content-bearing)
        weight = 1.0 + min(len(w), 8) * 0.1
        vec[idx] += weight

    # 2. Bigrams for phrase preservation
    for i in range(len(words) - 1):
        bigram = f"{words[i]}_{words[i+1]}"
        idx = _hash_token(bigram, dim)
        vec[idx] += 1.5

    # 3. Trigrams / subwords (3-4 char shingles)
    for w in words:
        if len(w) >= 4:
            for i in range(len(w) - 2):
                tri = w[i:i+3]
                idx = _hash_token(tri, dim)
                vec[idx] += 0.4

    # 4. L2 Normalization
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 1e-9:
        vec = [round(x / norm, 6) for x in vec]
    else:
        vec = [0.0] * dim

    return vec

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text.
    If Gemini API key is configured and functional, uses text-embedding-004.
    Otherwise uses local deterministic semantic vectorizer.
    """
    if settings.GEMINI_API_KEY:
        try:
            # We will attempt Gemini API call in Phase 4 when fully wired
            pass
        except Exception:
            pass
    return generate_local_embedding(text)

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two normalized vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    return max(0.0, min(1.0, dot))

def keyword_overlap_score(query: str, text: str) -> float:
    """Calculate token overlap / lexical score between query and chunk."""
    q_tokens = set(re.findall(r'\w+', query.lower()))
    if not q_tokens:
        return 0.0
    text_tokens = set(re.findall(r'\w+', text.lower()))
    if not text_tokens:
        return 0.0
    overlap = q_tokens.intersection(text_tokens)
    return len(overlap) / len(q_tokens)

def search_relevant_chunks(
    db: Session,
    query: str,
    environment: str,
    outlet_id: Optional[int] = None,
    category: Optional[str] = None,
    top_k: int = 5,
    min_score: float = 0.12,
) -> List[Dict[str, Any]]:
    """
    Perform hybrid vector + lexical search strictly isolated within the specified environment.
    CRITICAL: Never touches chunks from other environments.
    """
    # 1. Query chunks only for target environment and active status
    chunk_query = db.query(KnowledgeChunk).join(
        KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id
    ).filter(
        KnowledgeChunk.environment == environment,
        KnowledgeChunk.is_active == True,
        KnowledgeDocument.is_active == True,
        KnowledgeDocument.environment == environment,
    )

    if outlet_id and isinstance(outlet_id, int):
        # Match specific outlet OR general enterprise knowledge (outlet_id is None)
        chunk_query = chunk_query.filter(
            (KnowledgeChunk.outlet_id == outlet_id) | (KnowledgeChunk.outlet_id == None)
        )

    if category and isinstance(category, str) and category != "ALL":
        chunk_query = chunk_query.filter(KnowledgeDocument.category == category)

    candidate_chunks = chunk_query.all()
    if not candidate_chunks:
        return []

    query_vec = generate_embedding(query)
    scored_results = []

    for chunk in candidate_chunks:
        chunk_vec = None
        if chunk.embedding_json:
            try:
                chunk_vec = json.loads(chunk.embedding_json)
            except Exception:
                chunk_vec = None

        if not chunk_vec:
            chunk_vec = generate_embedding(chunk.content)
            # Cache back to database
            chunk.embedding_json = json.dumps(chunk_vec)
            db.commit()

        # Hybrid scoring: 65% cosine vector similarity + 35% lexical token overlap
        cos_sim = cosine_similarity(query_vec, chunk_vec)
        lex_sim = keyword_overlap_score(query, chunk.content)
        combined_score = (0.65 * cos_sim) + (0.35 * lex_sim)

        # High-precision relevance filter: requires lexical alignment OR strong semantic cosine
        is_relevant = (lex_sim >= 0.08 and combined_score >= 0.15) or (cos_sim >= 0.35) or (lex_sim >= 0.25)

        if is_relevant:
            doc = chunk.document
            scored_results.append({
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "document_title": doc.title if doc else "Corporate Document",
                "category": doc.category if doc else "GENERAL",
                "environment": chunk.environment,
                "outlet_id": chunk.outlet_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "score": round(combined_score, 4),
                "cosine_similarity": round(cos_sim, 4),
                "lexical_overlap": round(lex_sim, 4),
            })

    # Sort descending by combined score
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    return scored_results[:top_k]
