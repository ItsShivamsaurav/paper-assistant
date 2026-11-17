import os
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.config.settings import settings

_cached_embedding_model = None


def get_embedding_model() -> HuggingFaceEndpointEmbeddings:
    global _cached_embedding_model

    if _cached_embedding_model is None:
        hf_token = getattr(settings, "hf_token", None) or os.getenv("HF_TOKEN")

        _cached_embedding_model = HuggingFaceEndpointEmbeddings(
            model=settings.embedding_model,
            task="feature-extraction",
            huggingfacehub_api_token=hf_token,
        )

    return _cached_embedding_model