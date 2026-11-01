from dataclasses import dataclass


@dataclass
class RetrievedChunk:
    source: str
    chunk_index: int
    content: str
    distance: float  # cosine distance: 0 = identical meaning, 2 = opposite
