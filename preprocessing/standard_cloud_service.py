"""
Standardized Cloud Service Schema for Vector Database
This schema is cloud-provider agnostic and suitable for retrieval + ranking
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class ServiceCategory(Enum):
    """Main service categories"""
    COMPUTE = "compute"
    DATABASE = "database"
    STORAGE = "storage"
    SERVERLESS = "serverless"
    CONTAINER = "container"
    KUBERNETES = "kubernetes"
    NETWORKING = "networking"
    OTHER = "other"

class PricingModel(Enum):
    """Pricing models"""
    ON_DEMAND = "on_demand"
    RESERVED = "reserved"
    SPOT = "spot"
    COMMITTED = "committed"
    FREE_TIER = "free_tier"

@dataclass
class PricingInfo:
    """Standardized pricing information"""
    price_per_unit: float  # Normalized to USD per hour/month where applicable
    currency: str = "USD"
    unit: str = ""  # e.g., "hour", "GB-month", "request", "GB-second"
    pricing_model: str = "on_demand"
    region: str = ""

    # Additional pricing details
    free_tier_included: bool = False
    minimum_charge: Optional[float] = None
    tiered_pricing: Optional[List[Dict]] = None  # For services with usage tiers

    def to_dict(self):
        return asdict(self)

@dataclass
class TechnicalSpecs:
    """Technical specifications"""
    # Compute specs
    vcpu: Optional[float] = None
    memory_gb: Optional[float] = None
    gpu_count: Optional[int] = None

    # Storage specs
    storage_type: Optional[str] = None  # e.g., "SSD", "HDD", "NVMe"
    storage_size_gb: Optional[float] = None
    iops: Optional[int] = None
    throughput_mbps: Optional[float] = None

    # Network specs
    network_performance: Optional[str] = None
    bandwidth_gbps: Optional[float] = None

    # Database specs
    database_engine: Optional[str] = None  # e.g., "MySQL", "PostgreSQL"
    database_engine_version: Optional[str] = None
    max_connections: Optional[int] = None

    # General
    architecture: Optional[str] = None  # e.g., "x86_64", "ARM64"
    operating_system: Optional[str] = None

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class CloudService:
    """
    Standardized cloud service representation
    This is what gets stored in the vector database
    """
    # Required fields
    service_id: str  # Unique ID: "{provider}_{service_type}_{sku}"
    provider: str  # "aws", "gcp", "azure"
    service_name: str  # Human-readable name
    service_type: str  # e.g., "ec2", "rds", "lambda"
    category: str  # From ServiceCategory enum

    # Descriptive text (for embedding generation)
    description: str  # Rich description combining all relevant text
    short_description: str  # Brief one-liner

    # Technical specifications
    specs: TechnicalSpecs

    # Pricing
    pricing: List[PricingInfo]  # Can have multiple pricing models/regions

    # Metadata
    region: str  # Primary region or "global"
    available_regions: List[str]  # All regions where available

    # Features and capabilities
    features: List[str]  # List of key features
    use_cases: List[str]  # Common use cases
    tags: List[str]  # Searchable tags

    # Compatibility and requirements
    supports_auto_scaling: bool = False
    supports_multi_az: bool = False
    supports_encryption: bool = False
    compliance_certifications: List[str] = None

    # For retrieval
    popularity_score: Optional[float] = None  # Based on usage/community
    maturity_score: Optional[float] = None  # Based on service age/stability

    # Original data reference
    raw_sku: str = ""  # Original SKU from provider
    last_updated: str = ""

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['specs'] = self.specs.to_dict()
        result['pricing'] = [p.to_dict() for p in self.pricing]
        return result

    def generate_embedding_text(self) -> str:
        """
        Generate text for embedding model
        Combines all searchable fields into one coherent text
        """
        parts = [
            f"Service: {self.service_name}",
            f"Provider: {self.provider.upper()}",
            f"Category: {self.category}",
            f"Description: {self.description}",
        ]

        # Add specs
        if self.specs.vcpu:
            parts.append(f"CPU: {self.specs.vcpu} vCPUs")
        if self.specs.memory_gb:
            parts.append(f"Memory: {self.specs.memory_gb} GB")
        if self.specs.storage_type:
            parts.append(f"Storage: {self.specs.storage_type}")
        if self.specs.database_engine:
            parts.append(f"Database: {self.specs.database_engine}")

        # Add features
        if self.features:
            parts.append(f"Features: {', '.join(self.features)}")

        # Add use cases
        if self.use_cases:
            parts.append(f"Use cases: {', '.join(self.use_cases)}")

        # Add pricing context
        if self.pricing:
            min_price = min(p.price_per_unit for p in self.pricing if p.price_per_unit > 0)
            parts.append(f"Starting price: ${min_price:.4f} per {self.pricing[0].unit}")

        # Add capabilities
        capabilities = []
        if self.supports_auto_scaling:
            capabilities.append("auto-scaling")
        if self.supports_multi_az:
            capabilities.append("multi-AZ")
        if self.supports_encryption:
            capabilities.append("encryption")
        if capabilities:
            parts.append(f"Capabilities: {', '.join(capabilities)}")

        return " | ".join(parts)


# Example usage
if __name__ == "__main__":
    # Example: AWS Lambda
    lambda_service = CloudService(
        service_id="aws_lambda_arm_us-east-1",
        provider="aws",
        service_name="AWS Lambda (ARM)",
        service_type="lambda",
        category=ServiceCategory.SERVERLESS.value,
        description="Serverless compute service that runs code in response to events without provisioning servers. ARM architecture for better price-performance.",
        short_description="Event-driven serverless compute",
        specs=TechnicalSpecs(
            memory_gb=10.0,  # Max configurable
            architecture="ARM64"
        ),
        pricing=[
            PricingInfo(
                price_per_unit=0.0000133334,
                currency="USD",
                unit="GB-second",
                pricing_model="on_demand",
                region="us-east-1",
                free_tier_included=True
            ),
            PricingInfo(
                price_per_unit=0.0000002,
                currency="USD",
                unit="request",
                pricing_model="on_demand",
                region="us-east-1",
                free_tier_included=True
            )
        ],
        region="us-east-1",
        available_regions=["us-east-1", "us-west-2", "eu-west-1"],
        features=[
            "Event-driven execution",
            "Auto-scaling",
            "Pay per invocation",
            "Integrated with AWS services",
            "ARM64 Graviton2 processors"
        ],
        use_cases=[
            "API backends",
            "Data processing",
            "Real-time file processing",
            "IoT backends",
            "Microservices"
        ],
        tags=["serverless", "compute", "event-driven", "arm", "lambda"],
        supports_auto_scaling=True,
        supports_encryption=True,
        raw_sku="26ETFYQPHHGGH3VY",
        last_updated="2025-11-12"
    )

    print("Embedding text:")
    print(lambda_service.generate_embedding_text())
    print("\n" + "="*80 + "\n")
    print("JSON representation:")
    import json
    print(json.dumps(lambda_service.to_dict(), indent=2))