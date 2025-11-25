"""
Configuration settings for the query processing pipeline
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class OllamaConfig:
    """Ollama LLM configuration"""
    host: str = "http://localhost:11434"
    embedding_model: str = "embeddinggemma:300m"
    chat_model: str = "gemma3:4b"
    temperature: float = 0.3  # Lower for more consistent outputs
    timeout: int = 300  # seconds


@dataclass
class QdrantConfig:
    """Qdrant vector database configuration"""
    host: str = "localhost"
    port: int = 6333
    url: Optional[str] = None
    api_key: Optional[str] = None
    collection_name: str = "cloud_services"


@dataclass
class RetrievalConfig:
    """Retrieval stage configuration"""
    dense_top_k: int = 30  # Candidates from dense retrieval
    sparse_top_k: int = 30  # Candidates from sparse retrieval
    fusion_top_k: int = 25  # Candidates after fusion for reranking
    score_threshold: float = 0.3  # Minimum similarity score


@dataclass
class RerankingConfig:
    """LLM reranking configuration"""
    batch_size: int = 5  # Services to evaluate per LLM call
    max_candidates: int = 20  # Maximum candidates to rerank
    min_relevance_score: float = 3.0  # Minimum LLM score (1-10) to include


@dataclass
class ScoringConfig:
    """Multi-dimensional scoring weights"""
    llm_relevance_weight: float = 0.5
    cost_efficiency_weight: float = 0.2
    capacity_match_weight: float = 0.2
    provider_diversity_weight: float = 0.1

    # Budget tolerance (how much over budget is acceptable)
    budget_tolerance: float = 1.2  # 20% over budget still considered


@dataclass
class PipelineConfig:
    """Main pipeline configuration"""
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    qdrant: QdrantConfig = field(default_factory=QdrantConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    reranking: RerankingConfig = field(default_factory=RerankingConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)

    # Final output
    top_k_results: int = 5

    # Supported providers
    providers: List[str] = field(default_factory=lambda: ["aws", "gcp", "azure"])

    # Service categories for classification
    service_categories: List[str] = field(default_factory=lambda: [
        "compute", "database", "storage", "serverless",
        "container", "kubernetes", "networking", "analytics"
    ])


# Default configuration instance
DEFAULT_CONFIG = PipelineConfig()