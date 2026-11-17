from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PayloadSchemaType, VectorParams

from app.config.settings import settings


@lru_cache
def get_qdrant_client():
    if settings.qdrant_url:
        print(f"Connecting to Qdrant at {settings.qdrant_url} with API key.")
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            check_compatibility=False,
            port=None,
            timeout=60,
        )
    else:
        client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            check_compatibility=False,
            timeout=30,
        )

    try:
        if not client.collection_exists(settings.collection_name):
            client.create_collection(
                collection_name=settings.collection_name,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                ),
            )

        # Ensure payload indexes exist for Qdrant Cloud Strict Mode filters
        payload_indexes = {
            "file_hash": PayloadSchemaType.KEYWORD,
            "source": PayloadSchemaType.KEYWORD,
            "owner_id": PayloadSchemaType.INTEGER,
        }

        for field_name, field_schema in payload_indexes.items():
            client.create_payload_index(
                collection_name=settings.collection_name,
                field_name=field_name,
                field_schema=field_schema,
            )
    except Exception as e:
        print(f"Qdrant connection error: {e}")
        raise

    return client