from io import BytesIO
from pathlib import Path
from typing import List, Optional

import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer

try:
    import openai
except ImportError:
    openai = None

from src.core.config import settings


class EmbeddingProvider:
    def __init__(self):
        self.use_openai = bool(settings.openai_api_key and openai)
        self.text_model = None
        self.image_model = None

        if self.use_openai:
            openai.api_key = settings.openai_api_key
            self.dimension = 3072
        else:
            self.text_model = SentenceTransformer(settings.local_embedding_model)
            self.image_model = SentenceTransformer("clip-ViT-B-32")
            self.dimension = self.text_model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if self.use_openai:
            response = openai.Embedding.create(
                model=settings.openai_embedding_model,
                input=texts,
            )
            embeddings = [item["embedding"] for item in response["data"]]
            return np.array(embeddings, dtype=np.float32)

        return self.text_model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

    def embed_image(self, image_path: Path) -> np.ndarray:
        if self.use_openai:
            caption = f"Image at {image_path.name}"
            return self.embed_texts([caption])[0]

        pil_image = Image.open(image_path).convert("RGB")
        return self.image_model.encode(pil_image, convert_to_numpy=True)

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed_texts([query])[0]
