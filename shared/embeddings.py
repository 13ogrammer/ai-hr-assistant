from functools import lru_cache

from fastembed import TextEmbedding


@lru_cache(maxsize=1)
def get_embedding_model() -> TextEmbedding:
    """Load the embedding model once per process and reuse it.

    Loading it from disk isn't free, and retrieval will call this on every
    question, so caching avoids reloading it on every request.
    """
    return TextEmbedding()  # BAAI/bge-small-en-v1.5, 384-dim vectors
