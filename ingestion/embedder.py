"""
Embedding Generator
Generates embeddings using Gemma through Ollama
"""

import requests
from typing import List


class EmbeddingGenerator:
    """Generate embeddings for cloud service descriptions using Ollama"""

    def __init__(self, model_name: str = "embeddinggemma:300m", ollama_host: str = "http://localhost:11434",
                 batch_size: int = 32):
        """
        Initialize the embedding generator

        Args:
            model_name: Ollama model to use (embeddinggemma:300m or other embedding models)
            ollama_host: Ollama API endpoint
            batch_size: Number of texts to embed in one batch
        """
        self.model_name = model_name
        self.ollama_host = ollama_host
        self.batch_size = batch_size
        self.dimension = None  # Will be set on first embedding

        # Test connection and get dimension
        try:
            response = requests.get(f"{ollama_host}/api/tags")
            response.raise_for_status()
            print(f" Connected to Ollama at {ollama_host}")

            # Generate test embedding to detect dimension
            print(f"   Detecting embedding dimension...")
            test_embedding = self.embed_single("test")
            self.dimension = len(test_embedding)

        except Exception as e:
            raise ConnectionError(f"Failed to connect to Ollama: {str(e)}")

        print(f" Initialized EmbeddingGenerator with model: {model_name}")
        print(f"   Dimension: {self.dimension}, Batch size: {batch_size}")

    def embed_single(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text string to embed

        Returns:
            Embedding vector
        """
        try:
            response = requests.post(f"{self.ollama_host}/api/embed",
                json={
                    "model": self.model_name,
                    "input": text
                }
            )
            response.raise_for_status()
            embedding = response.json()["embeddings"][0]

            # Set dimension on first call
            if self.dimension is None:
                self.dimension = len(embedding)
                print(f"   Detected embedding dimension: {self.dimension}")

            return embedding

        except Exception as e:
            print(f" Error generating embedding: {str(e)}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        embeddings = []
        for text in texts:
            embedding = self.embed_single(text)
            embeddings.append(embedding)

        return embeddings

    def embed_texts(self, texts: List[str], show_progress: bool = True) -> List[List[float]]:
        """
        Generate embeddings for a list of texts with batching

        Args:
            texts: List of text strings to embed
            show_progress: Whether to print progress

        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1

            if show_progress:
                print(f"  Processing batch {batch_num}/{total_batches} ({len(batch)} texts)...")

            embeddings = self.embed_batch(batch)
            all_embeddings.extend(embeddings)

        if show_progress:
            print(f" Generated {len(all_embeddings)} embeddings")

        return all_embeddings

    def get_dimension(self) -> int | None:
        """Get the embedding dimension"""
        return self.dimension


if __name__ == "__main__":
    # Test the embedder
    print("\n" + "="*60)
    print("Testing Ollama Gemma Embedder")
    print("="*60)

    embedder = EmbeddingGenerator()

    test_texts = [
        "AWS EC2 t2.micro instance with 1 vCPU and 1 GB RAM",
        "Google Cloud SQL PostgreSQL database",
        "Azure Kubernetes Service for container orchestration"
    ]

    print("\nTesting embedder with sample texts:")
    embeddings = embedder.embed_texts(test_texts)

    print(f"\n✅ Generated {len(embeddings)} embeddings")
    print(f"   Embedding dimension: {len(embeddings[0])}")
    print(f"   First 5 values of first embedding: {embeddings[0][:5]}")