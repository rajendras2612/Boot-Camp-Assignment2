import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional

import faiss
import numpy as np


class VectorStore:
    def __init__(self, storage_path: Path, dimension: int):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_path = self.storage_path / "vector.index"
        self.meta_path = self.storage_path / "metadata.pkl"
        self.dimension = dimension
        self.index = self._load_index()
        self.metadata: List[Dict[str, Any]] = self._load_metadata()

    def _load_index(self):
        if self.index_path.exists():
            return faiss.read_index(str(self.index_path))
        return faiss.IndexFlatIP(self.dimension)

    def _load_metadata(self):
        if self.meta_path.exists():
            with open(self.meta_path, "rb") as handle:
                return pickle.load(handle)
        return []

    def add(self, embeddings: np.ndarray, metadatas: List[Dict[str, Any]]):
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        self.index.add(embeddings)
        self.metadata.extend(metadatas)
        self._persist()

    def search(self, query_embedding: np.ndarray, top_k: int):
        if query_embedding.dtype != np.float32:
            query_embedding = query_embedding.astype(np.float32)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        if self.index.ntotal == 0:
            return [], []

        distances, indices = self.index.search(query_embedding, top_k)
        hits = [self.metadata[int(i)] for i in indices[0] if i != -1]
        return hits, distances[0].tolist()

    def _persist(self):
        faiss.write_index(self.index, str(self.index_path))
        with open(self.meta_path, "wb") as handle:
            pickle.dump(self.metadata, handle)

    def count(self) -> int:
        return len(self.metadata)

    def reset(self):
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        self._persist()
