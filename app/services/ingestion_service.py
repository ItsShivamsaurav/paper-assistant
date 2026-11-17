from pathlib import Path
from uuid import uuid4

from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct

from app.chunking.chunker import split_documents
from app.config.settings import settings
from app.embeddings.embedding_model import get_embedding_model
from app.loaders.pdf_loader import load_pdf
from app.privacy.classifier import DataClassification
from app.utils.file_hash import calculate_file_hash
from app.utils.logger import logger
from app.vectorstore.client import get_qdrant_client

EMBEDDING_BATCH_SIZE = 50


def ingest_pdf(
    pdf_path: str,
    owner_id: int,
) -> None:
    """
    Load a PDF, split it into chunks, generate batched embeddings,
    and store them in Qdrant with document ownership
    and data classification metadata.
    """
    file_hash = calculate_file_hash(pdf_path)
    filename = Path(pdf_path).name
    classification = DataClassification.INTERNAL.value

    client = get_qdrant_client()

    existing_points, _ = client.scroll(
        collection_name=settings.collection_name,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="file_hash",
                    match=MatchValue(value=file_hash),
                ),
                FieldCondition(
                    key="owner_id",
                    match=MatchValue(value=owner_id),
                ),
            ]
        ),
        limit=1,
    )

    if existing_points:
        logger.warning("PDF already indexed. Skipping.....")
        return

    logger.info("Loading PDF.....")
    documents = load_pdf(pdf_path)

    logger.info("Chunking.....")
    chunks = split_documents(documents)

    if not chunks:
        logger.warning(
            "No extractable text found in PDF %s for owner %s. Skipping indexing.",
            filename,
            owner_id,
        )
        return

    embedding_model = get_embedding_model()
    logger.info("Generating embeddings for %s chunks...", len(chunks))

    total_stored = 0

    for i in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch_chunks = chunks[i : i + EMBEDDING_BATCH_SIZE]
        texts = [chunk.page_content for chunk in batch_chunks]

        # Single batched API call instead of 1 request per chunk
        vectors = embedding_model.embed_documents(texts)

        points = [
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "text": chunk.page_content,
                    "source": filename,
                    "page": chunk.metadata.get("page", 0),
                    "file_hash": file_hash,
                    "owner_id": owner_id,
                    "classification": classification,
                },
            )
            for chunk, vector in zip(batch_chunks, vectors)
        ]

        client.upsert(
            collection_name=settings.collection_name,
            points=points,
        )
        total_stored += len(points)

    logger.info(
        "Successfully stored %s chunks for user %s.",
        total_stored,
        owner_id,
    )