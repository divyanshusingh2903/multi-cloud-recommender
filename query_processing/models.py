"""
Data models for the query processing pipeline
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class ServiceCategory(Enum):
    """Service category types"""
    COMPUTE = "compute"
    DATABASE = "database"
    STORAGE = "storage"
    SERVERLESS = "serverless"
    CONTAINER = "container"
    KUBERNETES = "kubernetes"
    NETWORKING = "networking"


@dataclass
class UserRequirements:
    """Structured requirements extracted from user query"""

    # Original query
    raw_query: str

    # Extracted requirements
    service_categories: List[str] = field(default_factory=list)  # compute, database, etc.

    # Scale requirements
    expected_users: Optional[int] = None
    expected_requests_per_second: Optional[int] = None
    data_size_gb: Optional[float] = None

    # Resource requirements
    min_vcpu: Optional[float] = None
    min_memory_gb: Optional[float] = None
    min_storage_gb: Optional[float] = None

    # Budget constraints
    budget_monthly_usd: Optional[float] = None
    budget_hourly_usd: Optional[float] = None

    # Preferences
    preferred_providers: List[str] = field(default_factory=list)  # aws, gcp, azure
    preferred_regions: List[str] = field(default_factory=list)

    # Technical requirements
    database_engine: Optional[str] = None  # mysql, postgresql, etc.
    requires_high_availability: bool = False
    requires_auto_scaling: bool = False
    requires_encryption: bool = False

    # Use case context
    use_case: Optional[str] = None  # web app, batch processing, etc.

    # Expanded query for retrieval
    expanded_query: str = ""

    # Keywords extracted
    keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'raw_query': self.raw_query,
            'service_categories': self.service_categories,
            'expected_users': self.expected_users,
            'expected_requests_per_second': self.expected_requests_per_second,
            'data_size_gb': self.data_size_gb,
            'min_vcpu': self.min_vcpu,
            'min_memory_gb': self.min_memory_gb,
            'min_storage_gb': self.min_storage_gb,
            'budget_monthly_usd': self.budget_monthly_usd,
            'budget_hourly_usd': self.budget_hourly_usd,
            'preferred_providers': self.preferred_providers,
            'preferred_regions': self.preferred_regions,
            'database_engine': self.database_engine,
            'requires_high_availability': self.requires_high_availability,
            'requires_auto_scaling': self.requires_auto_scaling,
            'requires_encryption': self.requires_encryption,
            'use_case': self.use_case,
            'expanded_query': self.expanded_query,
            'keywords': self.keywords
        }


@dataclass
class RetrievedCandidate:
    """A candidate service retrieved from the vector database"""

    # Identification
    service_id: str
    provider: str
    service_name: str
    service_type: str
    category: str

    # Descriptions
    description: str
    short_description: str

    # Technical specs
    vcpu: Optional[float] = None
    memory_gb: Optional[float] = None
    storage_type: Optional[str] = None
    database_engine: Optional[str] = None

    # Pricing (lowest available)
    price_per_unit: Optional[float] = None
    price_unit: Optional[str] = None

    # Features
    features: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)

    # Capabilities
    supports_auto_scaling: bool = False
    supports_multi_az: bool = False
    supports_encryption: bool = False

    # Region
    region: str = ""
    available_regions: List[str] = field(default_factory=list)

    # Retrieval scores
    dense_score: float = 0.0
    sparse_score: float = 0.0
    fusion_score: float = 0.0

    # Full payload reference
    raw_payload: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_qdrant_payload(cls, payload: Dict[str, Any], score: float = 0.0) -> 'RetrievedCandidate':
        """Create from Qdrant search result payload"""
        specs = payload.get('specs', {})
        pricing = payload.get('pricing', [])

        # Get lowest price
        price_per_unit = None
        price_unit = None
        if pricing:
            min_price = min(pricing, key=lambda p: p.get('price_per_unit', float('inf')))
            price_per_unit = min_price.get('price_per_unit')
            price_unit = min_price.get('unit', '')

        return cls(
            service_id=payload.get('service_id', ''),
            provider=payload.get('provider', ''),
            service_name=payload.get('service_name', ''),
            service_type=payload.get('service_type', ''),
            category=payload.get('category', ''),
            description=payload.get('description', ''),
            short_description=payload.get('short_description', ''),
            vcpu=specs.get('vcpu'),
            memory_gb=specs.get('memory_gb'),
            storage_type=specs.get('storage_type'),
            database_engine=specs.get('database_engine'),
            price_per_unit=price_per_unit,
            price_unit=price_unit,
            features=payload.get('features', []),
            use_cases=payload.get('use_cases', []),
            supports_auto_scaling=payload.get('supports_auto_scaling', False),
            supports_multi_az=payload.get('supports_multi_az', False),
            supports_encryption=payload.get('supports_encryption', False),
            region=payload.get('region', ''),
            available_regions=payload.get('available_regions', []),
            dense_score=score,
            raw_payload=payload
        )


@dataclass
class ScoredCandidate:
    """A candidate with LLM relevance score and explanation"""

    # Base candidate
    candidate: RetrievedCandidate

    # LLM evaluation
    llm_relevance_score: float = 0.0  # 1-10 scale
    llm_explanation: str = ""

    # Feature-based scores (0-1 scale)
    cost_efficiency_score: float = 0.0
    capacity_match_score: float = 0.0
    feature_match_score: float = 0.0

    # Final combined score
    final_score: float = 0.0

    # Ranking position
    rank: int = 0


@dataclass
class Recommendation:
    """Final recommendation with all details"""

    # Ranking
    rank: int

    # Service identification
    service_id: str
    provider: str
    service_name: str
    service_type: str
    category: str

    # Descriptions
    description: str
    short_description: str

    # Technical specs summary
    specs_summary: str

    # Pricing summary
    pricing_summary: str

    # Why this recommendation
    explanation: str

    # Scores
    relevance_score: float  # 0-10
    final_score: float  # 0-1 normalized

    # Key features
    key_features: List[str] = field(default_factory=list)

    # Matching criteria
    matches: List[str] = field(default_factory=list)  # What requirements it matches
    concerns: List[str] = field(default_factory=list)  # Potential issues

    # Region
    region: str = ""

    # Full data reference
    full_payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'rank': self.rank,
            'service_id': self.service_id,
            'provider': self.provider,
            'service_name': self.service_name,
            'service_type': self.service_type,
            'category': self.category,
            'description': self.description,
            'short_description': self.short_description,
            'specs_summary': self.specs_summary,
            'pricing_summary': self.pricing_summary,
            'explanation': self.explanation,
            'relevance_score': self.relevance_score,
            'final_score': self.final_score,
            'key_features': self.key_features,
            'matches': self.matches,
            'concerns': self.concerns,
            'region': self.region
        }


@dataclass
class PipelineResult:
    """Complete result from the recommendation pipeline"""

    # Original query
    query: str

    # Extracted requirements
    requirements: UserRequirements

    # Recommendations
    recommendations: List[Recommendation] = field(default_factory=list)

    # Summary
    summary: str = ""

    # Multi-cloud comparison (if applicable)
    provider_comparison: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    total_candidates_retrieved: int = 0
    total_candidates_reranked: int = 0
    processing_time_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'query': self.query,
            'requirements': self.requirements.to_dict(),
            'recommendations': [r.to_dict() for r in self.recommendations],
            'summary': self.summary,
            'provider_comparison': self.provider_comparison,
            'metadata': {
                'total_candidates_retrieved': self.total_candidates_retrieved,
                'total_candidates_reranked': self.total_candidates_reranked,
                'processing_time_seconds': self.processing_time_seconds
            }
        }