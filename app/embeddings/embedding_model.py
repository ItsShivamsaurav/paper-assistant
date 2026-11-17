import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config.settings import settings

_cached_embedding_model = None


def get_embedding_model() -> GoogleGenerativeAIEmbeddings:
    global _cached_embedding_model

    if _cached_embedding_model is None:
        api_key = getattr(settings, "gemini_api_key", None) or os.getenv("GEMINI_API_KEY")
        _cached_embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key,
            output_dimensionality=384,  # Keeps 384 dimensions to match your Qdrant setup
        )

    return _cached_embedding_model


# import os
# from langchain_huggingface import HuggingFaceEndpointEmbeddings

# from app.config.settings import settings

# _cached_embedding_model = None


# def get_embedding_model() -> HuggingFaceEndpointEmbeddings:
#     global _cached_embedding_model

#     if _cached_embedding_model is None:
#         hf_token = getattr(settings, "hf_token", None) or os.getenv("HF_TOKEN")

#         _cached_embedding_model = HuggingFaceEndpointEmbeddings(
#             model=settings.embedding_model,
#             task="feature-extraction",
#             huggingfacehub_api_token=hf_token,
#         )

#     return _cached_embedding_model