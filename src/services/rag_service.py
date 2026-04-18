from pathlib import Path
from typing import Dict, List, Tuple

from src.core.config import settings
from src.services.embeddings import EmbeddingProvider
from src.utils.pdf_processor import (
    block_to_documents,
    extract_images,
    extract_text_blocks,
)
from src.utils.vector_store import VectorStore


class RAGService:
    def __init__(self):
        self.embedding_provider = EmbeddingProvider()
        self.vector_store = VectorStore(settings.vector_store_path, self.embedding_provider.dimension)

    def status(self) -> Dict[str, object]:
        return {
            "vector_count": self.vector_store.count(),
            "embedding_model": settings.openai_embedding_model if settings.openai_api_key else settings.local_embedding_model,
            "openai_enabled": bool(settings.openai_api_key),
            "index_type": type(self.vector_store.index).__name__,
        }

    def ingest_pdf(self, pdf_path: Path) -> Tuple[int, List[Dict[str, str]]]:
        text_blocks = extract_text_blocks(pdf_path)
        documents = block_to_documents(text_blocks, settings.chunk_size, settings.chunk_overlap)

        image_folder = settings.pdf_storage_path / "images"
        image_paths = extract_images(pdf_path, image_folder)

        image_documents: List[Tuple[str, Dict[str, str]]] = []
        for image_path in image_paths:
            image_caption = f"Image extracted from PDF page {image_path.stem.split('-')[1]}"
            image_documents.append(
                (
                    image_caption,
                    {
                        "source": "pdf_image",
                        "image_path": str(image_path),
                        "text": image_caption,
                    },
                )
            )

        all_text = [content for content, _ in documents] + [caption for caption, _ in image_documents]
        all_metadata = [metadata for _, metadata in documents] + [metadata for _, metadata in image_documents]

        if not all_text:
            return 0, []

        embeddings = self.embedding_provider.embed_texts(all_text)
        self.vector_store.add(embeddings, all_metadata)
        return len(all_text), all_metadata

    def query(self, query_text: str, top_k: int | None = None) -> Tuple[str, List[Dict[str, str]]]:
        top_k = top_k or settings.top_k
        query_embedding = self.embedding_provider.embed_query(query_text)
        hits, _ = self.vector_store.search(query_embedding, top_k)

        if not hits:
            return "No relevant documents were found.", []

        answer = self._generate_answer(query_text, hits)
        return answer, hits

    def _generate_answer(self, query_text: str, documents: List[Dict[str, str]]) -> str:
        if settings.openai_api_key:
            return self._openai_generate(query_text, documents)

        text_context = "\n\n".join(item.get("source", "") + ": " + item.get("text", "") for item in documents)
        return (
            f"Query: {query_text}\n\nTop context:\n{text_context}\n\n"
            "This response was generated without an external LLM provider."
        )

    def _openai_generate(self, query_text: str, documents: List[Dict[str, str]]) -> str:
        try:
            import openai

            openai.api_key = settings.openai_api_key
            top_context = "\n\n".join(
                f"Source: {item.get('source')}\n{item.get('text', '')}"
                for item in documents
            )
            prompt = (
                f"Answer the question using the context below. "
                f"If the answer is not contained in the context, say 'I cannot answer that from the provided documents.'\n\n"
                f"Context:\n{top_context}\n\nQuestion: {query_text}\nAnswer:"
            )
            completion = openai.ChatCompletion.create(
                model=settings.openai_completion_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.0,
            )
            return completion.choices[0].message.content.strip()
        except Exception as error:
            return f"Unable to generate answer with OpenAI: {error}"
