"""
Ingestion Pipeline
Orchestrates the full data ingestion process: load JSON â†’ generate embeddings â†’ upload to Qdrant
"""

import json
import os
from typing import List, Dict, Any, Optional
from qdrant_client.models import PointStruct
import uuid

from embedder import EmbeddingGenerator
from qdrant_manager import QdrantManager


class IngestionPipeline:
    """Orchestrates the ingestion of cloud service data into Qdrant"""

    def __init__(self, qdrant_host: str = "localhost", qdrant_port: int = 6333,
                 qdrant_url: Optional[str] = None, qdrant_api_key: Optional[str] = None,
                 collection_name: str = "cloud_services", embedding_batch_size: int = 32,
                 upload_batch_size: int = 100, ollama_host: str = "http://localhost:11434",
                 model_name: str = "embeddinggemma:300m"):
        """
        Initialize the ingestion pipeline

        Args:
            qdrant_host: Qdrant server host (used if qdrant_url is not provided)
            qdrant_port: Qdrant server port (used if qdrant_url is not provided)
            qdrant_url: Full URL to Qdrant instance (e.g., "https://xyz.qdrant.io")
            qdrant_api_key: API key for Qdrant authentication (required for cloud instances)
            collection_name: Name of the Qdrant collection
            embedding_batch_size: Batch size for embedding generation
            upload_batch_size: Batch size for uploading to Qdrant
            ollama_host: Ollama API endpoint
            model_name: Ollama model to use for embeddings
        """
        self.collection_name = collection_name
        self.upload_batch_size = upload_batch_size

        print("="*80)
        print("INITIALIZING INGESTION PIPELINE")
        print("="*80)

        # Initialize embedder
        self.embedder = EmbeddingGenerator(model_name=model_name, ollama_host=ollama_host,
                                           batch_size=embedding_batch_size)

        # Initialize Qdrant manager
        self.qdrant = QdrantManager(host=qdrant_host, port=qdrant_port, url=qdrant_url, api_key=qdrant_api_key)

        # Ensure collection exists
        self._setup_collection()

    def _setup_collection(self):
        """Create collection if it doesn't exist"""
        if not self.qdrant.collection_exists(self.collection_name):
            print(f"\n Collection '{self.collection_name}' does not exist. Creating...")
            dimension = self.embedder.get_dimension()
            if dimension is None:
                raise ValueError("Failed to detect embedding dimension")
            self.qdrant.create_collection(collection_name=self.collection_name,
                                          vector_size=dimension
            )
        else:
            print(f"\n Collection '{self.collection_name}' already exists")

    def load_standardized_json(self, file_path: str) -> Dict[str, Any]:
        """
        Load standardized services JSON file

        Args:
            file_path: Path to the JSON file

        Returns:
            Dictionary with metadata and services
        """
        print(f"\n Loading data from: {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r') as f:
            data = json.load(f)

        provider = data.get('metadata', {}).get('provider', 'unknown')
        services = data.get('services', [])

        print(f"   Provider: {provider}")
        print(f"   Total services: {len(services)}")

        return data

    def prepare_points(self, services: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[PointStruct]:
        """
        Prepare PointStruct objects for Qdrant upload

        Args:
            services: List of service dictionaries with embedding_text and blob
            embeddings: List of embedding vectors

        Returns:
            List of PointStruct objects
        """
        if len(services) != len(embeddings):
            raise ValueError(f"Mismatch: {len(services)} services but {len(embeddings)} embeddings")

        points = []
        for service, embedding in zip(services, embeddings):
            blob = service.get('blob', {})

            # Create payload with all blob data
            payload = blob.copy()

            # Add the embedding text for reference
            payload['embedding_text'] = service.get('embedding_text', '')

            # Let Qdrant auto-generate UUID
            point = PointStruct(id=str(uuid.uuid4()), vector=embedding, payload=payload)
            points.append(point)

        return points

    def ingest_provider(self, provider: str, data_dir: str = "./data"):
        """
        Ingest data for a specific provider

        Args:
            provider: Provider name (aws, gcp, azure)
            data_dir: Base directory containing data folders
        """
        print("\n" + "="*80)
        print(f"INGESTING {provider.upper()} DATA")
        print("="*80)

        # Construct file path
        provider_lower = provider.lower()
        file_path = os.path.join(data_dir, provider.upper(), f"{provider_lower}_standardized_services.json")

        # Load data
        data = self.load_standardized_json(file_path)
        services = data.get('services', [])

        if not services:
            print(f"!!!  No services found in {file_path}")
            return

        # Extract embedding texts
        print("\n Extracting embedding texts...")
        embedding_texts = [service.get('embedding_text', '') for service in services]

        # Filter out empty texts
        valid_indices = [i for i, text in enumerate(embedding_texts) if text.strip()]
        if len(valid_indices) < len(embedding_texts):
            print(f"  Filtering out {len(embedding_texts) - len(valid_indices)} services with empty embedding text")

        valid_services = [services[i] for i in valid_indices]
        valid_texts = [embedding_texts[i] for i in valid_indices]

        # Generate embeddings
        print(f"\n Generating embeddings for {len(valid_texts)} services...")
        embeddings = self.embedder.embed_texts(valid_texts)

        # Prepare points
        print(f"\n Preparing {len(valid_services)} points for upload...")
        points = self.prepare_points(valid_services, embeddings)

        # Upload to Qdrant
        self.qdrant.upload_points(
            collection_name=self.collection_name,
            points=points,
            batch_size=self.upload_batch_size
        )

        # Print summary
        print("\n" + "="*80)
        print(f" {provider.upper()} INGESTION COMPLETE")
        print("="*80)

        # Get collection info
        info = self.qdrant.get_collection_info(self.collection_name)
        print(f"\n Collection Status:")
        print(f"   Total points in collection: {info.get('points_count', 0)}")
        print(f"   Total vectors: {info.get('vectors_count', 0)}")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Ingest cloud service data into Qdrant")
    parser.add_argument("--provider", type=str, required=True, choices=['aws', 'gcp', 'azure'],
                        help="Provider to ingest (aws, gcp, azure, or all)")
    parser.add_argument("--data-dir", type=str, default="./data",
                        help="Base directory containing data folders")
    parser.add_argument("--collection", type=str, default="cloud_services",
                        help="Qdrant collection name")
    parser.add_argument("--qdrant-host", type=str, default="localhost",
                        help="Qdrant host (used if --qdrant-url is not provided)")
    parser.add_argument("--qdrant-port", type=int, default=6333,
                        help="Qdrant port (used if --qdrant-url is not provided)")
    parser.add_argument("--qdrant-url", type=str, default=None,
                        help="Full Qdrant URL for cloud instances (e.g., https://xyz.qdrant.io)")
    parser.add_argument("--qdrant-api-key", type=str, default=None,
                        help="API key for Qdrant cloud authentication")
    parser.add_argument("--ollama-host", type=str, default="http://localhost:11434",
                        help="Ollama API endpoint")
    parser.add_argument("--model", type=str, default="embeddinggemma:300m",
                        help="Ollama model name for embeddings")

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = IngestionPipeline(qdrant_host=args.qdrant_host, qdrant_port=args.qdrant_port,
        qdrant_url=args.qdrant_url, qdrant_api_key=args.qdrant_api_key, collection_name=args.collection,
        ollama_host=args.ollama_host, model_name=args.model)

    # Ingest data
    pipeline.ingest_provider(args.provider, data_dir=args.data_dir)


if __name__ == "__main__":
    main()