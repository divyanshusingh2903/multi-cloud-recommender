from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType

def create_all_indexes(collection_name, qdrant_url, qdrant_api_key):
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    indexes = [
        ("provider", PayloadSchemaType.KEYWORD),
        ("category", PayloadSchemaType.KEYWORD),
        ("service_type", PayloadSchemaType.KEYWORD),
        ("service_name", PayloadSchemaType.KEYWORD),
        ("region", PayloadSchemaType.KEYWORD),
        ("supports_auto_scaling", PayloadSchemaType.BOOL),
        ("supports_multi_az", PayloadSchemaType.BOOL),
        ("supports_encryption", PayloadSchemaType.BOOL),
    ]

    for field_name, field_type in indexes:
        try:
            client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=field_type
            )
            print(f"✓ Created index for {field_name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"⚠️  Index for {field_name} already exists")
            else:
                print(f"❌ Error creating index for {field_name}: {str(e)}")

if __name__ == "__main__":
    collection_name = "cloud_services"

    import argparse

    parser = argparse.ArgumentParser(description="Retriever Stage")
    parser.add_argument("--qdrant-url", type=str, default="cloud-services",
                        help="Qdrant URL for Database deployment")
    parser.add_argument("--qdrant-api-key", type=str, default=None,
                        help="Qdrant API key for authentication")

    args = parser.parse_args()

    create_all_indexes(collection_name, args.qdrant_url, args.qdrant_api_key)