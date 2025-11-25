"""
Qdrant Collection Manager
Handles Qdrant collection creation, configuration, and operations
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (Distance, VectorParams, PointStruct, Filter)
from typing import List, Dict, Any, Optional


class QdrantManager:
    """Manages Qdrant collections and operations"""

    def __init__(self, host: str = "localhost", port: int = 6333, url: Optional[str] = None,
                 api_key: Optional[str] = None):
        """
        Initialize Qdrant client

        Args:
            host: Qdrant server host (used if url is not provided)
            port: Qdrant server port (used if url is not provided)
            url: Full URL to Qdrant instance
            api_key: API key for authentication (required for cloud instances)
        """
        if url:
            # Use URL-based connection (for cloud instances)
            self.client = QdrantClient(url=url, api_key=api_key)
            print(f"Connected to Qdrant at {url}")
        else:
            # Use host:port connection (for local instances)
            self.client = QdrantClient(host=host, port=port)
            print(f"Connected to Qdrant at {host}:{port}")

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists

        Args:
            collection_name: Name of the collection

        Returns:
            True if collection exists, False otherwise
        """
        try:
            collections = self.client.get_collections().collections
            return any(col.name == collection_name for col in collections)
        except Exception as e:
            print(f" Error checking collection existence: {str(e)}")
            return False

    def create_collection(self, collection_name: str, vector_size: int, distance: Distance = Distance.COSINE,
                          recreate: bool = False):
        """
        Create a new collection

        Args:
            collection_name: Name of the collection
            vector_size: Dimension of the embedding vectors
            distance: Distance metric (COSINE, EUCLID, DOT)
            recreate: If True, delete existing collection and create new
        """
        if self.collection_exists(collection_name):
            if recreate:
                print(f"  Deleting existing collection: {collection_name}")
                self.client.delete_collection(collection_name)
            else:
                print(f"  Collection '{collection_name}' already exists, skipping creation")
                return

        print(f" Creating collection: {collection_name}")
        print(f"   Vector size: {vector_size}, Distance: {distance}")

        result = self.client.create_collection(collection_name=collection_name,
                                               vectors_config=VectorParams(size=vector_size, distance=distance))

        print(f" Collection '{collection_name}' created successfully")

    def upload_points(self, collection_name: str, points: List[PointStruct], batch_size: int = 100):
        """
        Upload points to a collection in batches

        Args:
            collection_name: Name of the collection
            points: List of PointStruct objects
            batch_size: Number of points to upload per batch
        """
        total_points = len(points)
        total_batches = (total_points + batch_size - 1) // batch_size

        print(f"\n Uploading {total_points} points to '{collection_name}'")

        for i in range(0, total_points, batch_size):
            batch = points[i:i + batch_size]
            batch_num = i // batch_size + 1

            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
                print(f"   Batch {batch_num}/{total_batches}: Uploaded {len(batch)} points")
            except Exception as e:
                print(f"   Batch {batch_num}/{total_batches}: Failed - {str(e)}")
                raise

        print(f" Successfully uploaded all {total_points} points")

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get information about a collection

        Args:
            collection_name: Name of the collection

        Returns:
            Dictionary with collection info
        """
        try:
            info = self.client.get_collection(collection_name)
            return {
                'name': collection_name,
                'vectors_count': info.vectors_count,
                'points_count': info.points_count,
                'status': info.status
            }
        except Exception as e:
            print(f"❌ Error getting collection info: {str(e)}")
            return {}

    def search(self, collection_name: str, query_vector: List[float], limit: int = 10,
               score_threshold: Optional[float] = None, filter_conditions: Optional[Filter] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors

        Args:
            collection_name: Name of the collection
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filter_conditions: Optional filters

        Returns:
            List of search results with scores and payloads
        """
        try:
            results = self.client.query_points(collection_name=collection_name, query=query_vector, limit=limit,
                                               score_threshold=score_threshold, query_filter=filter_conditions)

            return [
                {
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                }
                for result in results
            ]
        except Exception as e:
            print(f" Error during search: {str(e)}")
            return []

    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        try:
            self.client.delete_collection(collection_name)
            print(f"  Deleted collection: {collection_name}")
        except Exception as e:
            print(f" Error deleting collection: {str(e)}")

    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = self.client.get_collections().collections
            return [col.name for col in collections]
        except Exception as e:
            print(f" Error listing collections: {str(e)}")
            return []
