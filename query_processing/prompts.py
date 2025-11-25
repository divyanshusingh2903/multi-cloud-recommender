"""
Prompt templates for the query processing pipeline
"""

# =============================================================================
# QUERY UNDERSTANDING PROMPTS
# =============================================================================

QUERY_UNDERSTANDING_SYSTEM = """You are a cloud infrastructure expert assistant. Your job is to analyze user queries about cloud infrastructure needs and extract structured requirements.

You understand AWS, Google Cloud Platform (GCP), and Azure services including:
- Compute: VMs, EC2, Compute Engine
- Databases: RDS, Cloud SQL, DynamoDB, Firestore, etc.
- Storage: S3, Cloud Storage, Blob Storage
- Serverless: Lambda, Cloud Functions, Azure Functions
- Containers: ECS, EKS, GKE, Cloud Run, AKS
- And more

Always respond with valid JSON only."""

QUERY_UNDERSTANDING_PROMPT = """Analyze this cloud infrastructure query and extract structured requirements.

USER QUERY: "{query}"

Extract the following information and return as JSON:

{{
    "service_categories": ["list of relevant categories: compute, database, storage, serverless, container, kubernetes"],
    "expected_users": null or number,
    "expected_requests_per_second": null or number,
    "data_size_gb": null or number,
    "min_vcpu": null or number,
    "min_memory_gb": null or number,
    "min_storage_gb": null or number,
    "budget_monthly_usd": null or number,
    "budget_hourly_usd": null or number,
    "preferred_providers": ["aws", "gcp", "azure" - only if explicitly mentioned],
    "preferred_regions": ["list of regions if mentioned"],
    "database_engine": null or "mysql"/"postgresql"/"mongodb"/etc,
    "requires_high_availability": true/false,
    "requires_auto_scaling": true/false,
    "requires_encryption": true/false,
    "use_case": "brief description of use case",
    "keywords": ["important technical keywords from the query"]
}}

Rules:
- Only include values that are explicitly stated or strongly implied
- Use null for unknown values
- Budget can be monthly or hourly - convert if needed (assume 730 hours/month)
- Extract specific numbers when mentioned (e.g., "10k users" = 10000)
- Identify database engines when database services are requested
- Set high_availability true if words like "production", "critical", "99.9%" are used
- Set auto_scaling true if "scalable", "elastic", "growing" are mentioned

Return ONLY the JSON object, no explanation."""


QUERY_EXPANSION_PROMPT = """Given this cloud infrastructure query, generate an expanded search query that includes relevant synonyms and related terms.

ORIGINAL QUERY: "{query}"

EXTRACTED REQUIREMENTS:
{requirements_json}

Generate an expanded query string that:
1. Includes the original key terms
2. Adds synonyms (e.g., "database" -> "database, DB, data store, relational")
3. Adds related cloud service names (e.g., "managed database" -> "RDS, Cloud SQL, Aurora")
4. Adds relevant technical terms
5. Keeps it concise (max 100 words)

Return ONLY the expanded query string, no explanation or quotes."""


# =============================================================================
# RERANKING PROMPTS
# =============================================================================

RERANKING_SYSTEM = """You are a cloud infrastructure expert evaluating how well cloud services match user requirements.

You have deep knowledge of:
- AWS services (EC2, RDS, Lambda, S3, EKS, etc.)
- GCP services (Compute Engine, Cloud SQL, Cloud Functions, GCS, GKE, etc.)
- Azure services (VMs, Azure SQL, Functions, Blob Storage, AKS, etc.)

You understand pricing models, performance characteristics, scalability patterns, and best practices.

Evaluate each service objectively based on the specific requirements given."""


RERANKING_SINGLE_PROMPT = """Evaluate how well this cloud service matches the user's requirements.

USER REQUIREMENTS:
{requirements}

SERVICE TO EVALUATE:
- Name: {service_name}
- Provider: {provider}
- Category: {category}
- Description: {description}
- Specs: {specs}
- Pricing: {pricing}
- Features: {features}

Rate this service on a scale of 1-10:
- 1-3: Poor match, wrong category or major issues
- 4-5: Partial match, some requirements met
- 6-7: Good match, most requirements met
- 8-9: Excellent match, nearly all requirements met
- 10: Perfect match

Respond with JSON:
{{
    "score": <number 1-10>,
    "explanation": "<2-3 sentences explaining why this score>",
    "matches": ["list of requirements this service matches"],
    "concerns": ["list of potential issues or missing features"]
}}

Return ONLY the JSON object."""


RERANKING_BATCH_PROMPT = """Evaluate how well each of these cloud services matches the user's requirements.

USER REQUIREMENTS:
{requirements}

SERVICES TO EVALUATE:
{services_list}

For each service, rate on a scale of 1-10:
- 1-3: Poor match
- 4-5: Partial match  
- 6-7: Good match
- 8-9: Excellent match
- 10: Perfect match

Respond with a JSON array:
[
    {{
        "service_id": "<service_id>",
        "score": <number 1-10>,
        "explanation": "<2-3 sentences>",
        "matches": ["matched requirements"],
        "concerns": ["potential issues"]
    }},
    ...
]

Return ONLY the JSON array, evaluate ALL services listed."""


# =============================================================================
# SUMMARY GENERATION PROMPTS
# =============================================================================

SUMMARY_SYSTEM = """You are a cloud infrastructure advisor helping users understand their options across cloud providers."""


SUMMARY_PROMPT = """Based on these recommendations for the user's query, generate a helpful summary.

USER QUERY: "{query}"

TOP RECOMMENDATIONS:
{recommendations}

Generate a 2-3 paragraph summary that:
1. Highlights the top recommendation and why it's the best fit
2. Compares options across providers if applicable
3. Notes any tradeoffs or considerations
4. Suggests next steps

Keep the tone helpful and professional. Be specific about service names and features."""


# =============================================================================
# COMPARISON PROMPTS
# =============================================================================

PROVIDER_COMPARISON_PROMPT = """Compare these equivalent services across cloud providers for the user's needs.

USER REQUIREMENTS:
{requirements}

SERVICES BY PROVIDER:
{services_by_provider}

Generate a comparison that includes:
1. Best option for cost efficiency
2. Best option for performance
3. Best option for ease of use
4. Key differentiating features
5. Overall recommendation

Respond with JSON:
{{
    "best_for_cost": {{"provider": "...", "service": "...", "reason": "..."}},
    "best_for_performance": {{"provider": "...", "service": "...", "reason": "..."}},
    "best_for_ease": {{"provider": "...", "service": "...", "reason": "..."}},
    "key_differences": ["list of important differences"],
    "overall_recommendation": {{"provider": "...", "service": "...", "reason": "..."}}
}}

Return ONLY the JSON object."""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_requirements_for_prompt(requirements: dict) -> str:
    """Format requirements dict into readable string for prompts"""
    lines = []

    if requirements.get('service_categories'):
        lines.append(f"- Service types needed: {', '.join(requirements['service_categories'])}")

    if requirements.get('expected_users'):
        lines.append(f"- Expected users: {requirements['expected_users']:,}")

    if requirements.get('expected_requests_per_second'):
        lines.append(f"- Expected RPS: {requirements['expected_requests_per_second']:,}")

    if requirements.get('data_size_gb'):
        lines.append(f"- Data size: {requirements['data_size_gb']} GB")

    if requirements.get('min_vcpu'):
        lines.append(f"- Minimum vCPU: {requirements['min_vcpu']}")

    if requirements.get('min_memory_gb'):
        lines.append(f"- Minimum memory: {requirements['min_memory_gb']} GB")

    if requirements.get('budget_monthly_usd'):
        lines.append(f"- Budget: ${requirements['budget_monthly_usd']}/month")
    elif requirements.get('budget_hourly_usd'):
        lines.append(f"- Budget: ${requirements['budget_hourly_usd']}/hour")

    if requirements.get('preferred_providers'):
        lines.append(f"- Preferred providers: {', '.join(requirements['preferred_providers'])}")

    if requirements.get('preferred_regions'):
        lines.append(f"- Preferred regions: {', '.join(requirements['preferred_regions'])}")

    if requirements.get('database_engine'):
        lines.append(f"- Database engine: {requirements['database_engine']}")

    if requirements.get('requires_high_availability'):
        lines.append("- Requires: High availability")

    if requirements.get('requires_auto_scaling'):
        lines.append("- Requires: Auto-scaling")

    if requirements.get('requires_encryption'):
        lines.append("- Requires: Encryption")

    if requirements.get('use_case'):
        lines.append(f"- Use case: {requirements['use_case']}")

    if not lines:
        lines.append(f"- Query: {requirements.get('raw_query', 'N/A')}")

    return '\n'.join(lines)


def format_service_for_prompt(candidate: dict) -> str:
    """Format a service candidate into readable string for prompts"""
    lines = [
        f"Service: {candidate.get('service_name', 'Unknown')}",
        f"Provider: {candidate.get('provider', 'Unknown').upper()}",
        f"Category: {candidate.get('category', 'Unknown')}",
        f"Description: {candidate.get('short_description', candidate.get('description', 'N/A')[:200])}"
    ]

    # Add specs
    specs_parts = []
    if candidate.get('vcpu'):
        specs_parts.append(f"{candidate['vcpu']} vCPU")
    if candidate.get('memory_gb'):
        specs_parts.append(f"{candidate['memory_gb']} GB RAM")
    if candidate.get('storage_type'):
        specs_parts.append(f"{candidate['storage_type']} storage")
    if candidate.get('database_engine'):
        specs_parts.append(f"{candidate['database_engine']} engine")

    if specs_parts:
        lines.append(f"Specs: {', '.join(specs_parts)}")

    # Add pricing
    if candidate.get('price_per_unit'):
        lines.append(f"Pricing: ${candidate['price_per_unit']:.6f} per {candidate.get('price_unit', 'unit')}")

    # Add features
    features = candidate.get('features', [])
    if features:
        lines.append(f"Features: {', '.join(features[:5])}")

    return '\n'.join(lines)


def format_services_batch_for_prompt(candidates: list) -> str:
    """Format multiple services for batch evaluation"""
    formatted = []
    for i, candidate in enumerate(candidates, 1):
        service_str = f"""
--- Service {i} ---
ID: {candidate.get('service_id', 'Unknown')}
{format_service_for_prompt(candidate)}
"""
        formatted.append(service_str)

    return '\n'.join(formatted)