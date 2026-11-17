import os
from huggingface_hub import InferenceClient
from langchain_core.documents import Document

from app.config.settings import settings
from app.utils.logger import logger

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class CrossEncoderReranker:

    def __init__(self):
        hf_token = getattr(settings, "hf_token", None) or os.getenv("HF_TOKEN")
        self.client = InferenceClient(
            provider="hf-inference",
            api_key=hf_token,
        )

    def rerank(
        self,
        query: str,
        documents: list[Document],
        top_k: int = 5,
    ) -> list[Document]:
        if not documents:
            return []

        try:
            scores = []
            for doc in documents:
                result = self.client.text_classification(
                    {"text": query, "text_pair": doc.page_content},
                    model=MODEL_NAME,
                )
                # Cross-encoder returns a single relevance score entry
                score = float(result[0]["score"]) if result else 0.0
                scores.append(score)

            ranked_documents = sorted(
                zip(documents, scores),
                key=lambda item: item[1],
                reverse=True,
            )

            reranked_documents = []
            for document, score in ranked_documents[:top_k]:
                document.metadata["reranker_score"] = score
                reranked_documents.append(document)

            return reranked_documents

        except Exception as exc:
            logger.warning(
                f"HF Inference reranker failed ({exc}); falling back to initial retrieval order."
            )
            return documents[:top_k]