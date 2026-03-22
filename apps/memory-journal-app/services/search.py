"""
Semantic Search Service — Vector similarity search for journal entries.
Uses TF-IDF vectorization as a lightweight alternative to sentence-transformers.
"""
import re
import math
from typing import List, Dict, Tuple
from collections import Counter


class SemanticSearchEngine:
    """Lightweight vector search using TF-IDF cosine similarity."""

    def __init__(self):
        self._documents: List[Dict] = []
        self._tfidf_cache: Dict[str, List[float]] = {}
        self._vocabulary: List[str] = []
        self._idf: Dict[str, float] = {}

    def _tokenize(self, text: str) -> List[str]:
        """Simple whitespace + punctuation tokenizer with stopword removal."""
        stopwords = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'shall', 'can',
            'of', 'in', 'to', 'for', 'with', 'on', 'at', 'from', 'by',
            'and', 'or', 'but', 'not', 'this', 'that', 'it', 'its',
        }
        tokens = re.findall(r'[a-z0-9]+', text.lower())
        return [t for t in tokens if t not in stopwords and len(t) > 1]

    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        counts = Counter(tokens)
        total = len(tokens) if tokens else 1
        return {t: c / total for t, c in counts.items()}

    def index_documents(self, documents: List[Dict]):
        """Build the TF-IDF index from journal entries."""
        self._documents = documents

        # Build vocabulary
        all_tokens = []
        doc_tokens = []
        for doc in documents:
            text = f"{doc.get('caption', '')} {' '.join(doc.get('tags', []))} {doc.get('filename', '')}"
            tokens = self._tokenize(text)
            doc_tokens.append(tokens)
            all_tokens.extend(tokens)

        self._vocabulary = sorted(set(all_tokens))

        # Compute IDF
        n_docs = len(documents) if documents else 1
        for term in self._vocabulary:
            doc_freq = sum(1 for dt in doc_tokens if term in dt)
            self._idf[term] = math.log((n_docs + 1) / (doc_freq + 1)) + 1

        # Compute TF-IDF vectors
        self._tfidf_cache = {}
        for i, tokens in enumerate(doc_tokens):
            tf = self._compute_tf(tokens)
            vector = [tf.get(term, 0) * self._idf.get(term, 0) for term in self._vocabulary]
            self._tfidf_cache[str(i)] = vector

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        mag_a = math.sqrt(sum(a * a for a in vec_a)) or 1
        mag_b = math.sqrt(sum(b * b for b in vec_b)) or 1
        return dot / (mag_a * mag_b)

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Dict, float]]:
        """Search for journal entries semantically similar to the query."""
        if not self._documents:
            return []

        query_tokens = self._tokenize(query)
        query_tf = self._compute_tf(query_tokens)
        query_vector = [query_tf.get(term, 0) * self._idf.get(term, 0) for term in self._vocabulary]

        scored = []
        for i, doc in enumerate(self._documents):
            doc_vec = self._tfidf_cache.get(str(i), [0] * len(self._vocabulary))
            sim = self._cosine_similarity(query_vector, doc_vec)
            if sim > 0.01:
                scored.append((doc, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


search_engine = SemanticSearchEngine()
