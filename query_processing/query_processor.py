"""
Query Processor - Stage 1
Handles query understanding, requirement extraction, and query expansion
"""

import json

from config import PipelineConfig, DEFAULT_CONFIG
from models import UserRequirements
from llm_client import LLMClient
from prompts import (QUERY_UNDERSTANDING_SYSTEM, QUERY_UNDERSTANDING_PROMPT, QUERY_EXPANSION_PROMPT)


class QueryProcessor:
    """Processes user queries to extract requirements and expand for retrieval"""

    def __init__(self, config: PipelineConfig = DEFAULT_CONFIG):
        """
        Initialize the query processor

        Args:
            config: Pipeline configuration
        """
        self.config = config

        # Initialize LLM client
        self.llm = LLMClient(host=config.ollama.host, model=config.ollama.chat_model,
            temperature=config.ollama.temperature, timeout=config.ollama.timeout)

        print(" QueryProcessor initialized")

    def process(self, query: str) -> UserRequirements:
        """
        Process a user query to extract requirements and generate expanded query

        Args:
            query: Raw user query string

        Returns:
            UserRequirements object with extracted information
        """
        print(f"\n Processing query: \"{query[:100]}{'...' if len(query) > 100 else ''}\"")

        # Step 1: Extract structured requirements
        requirements = self._extract_requirements(query)

        # Step 2: Generate expanded query
        expanded_query = self._expand_query(query, requirements)
        requirements.expanded_query = expanded_query

        print(f"    Extracted {len([v for v in requirements.to_dict().values() if v])} requirement fields")
        print(f"    Generated expanded query ({len(expanded_query.split())} words)")

        return requirements

    def _extract_requirements(self, query: str) -> UserRequirements:
        """
        Use LLM to extract structured requirements from query

        Args:
            query: Raw user query

        Returns:
            UserRequirements object
        """
        # Format the prompt
        prompt = QUERY_UNDERSTANDING_PROMPT.format(query=query)

        # Get LLM response
        response = self.llm.generate_json(prompt, system_prompt=QUERY_UNDERSTANDING_SYSTEM)

        if not response:
            print("     LLM extraction failed, using basic parsing")
            return self._basic_parse(query)

        # Convert response to UserRequirements
        return self._response_to_requirements(query, response)

    def _response_to_requirements(self, query: str, response: dict) -> UserRequirements:
        """Convert LLM JSON response to UserRequirements object"""

        # Handle potential type mismatches gracefully
        def safe_list(val):
            if isinstance(val, list):
                return val
            elif val:
                return [val]
            return []

        def safe_float(val):
            if val is None:
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        def safe_int(val):
            if val is None:
                return None
            try:
                return int(val)
            except (ValueError, TypeError):
                return None

        def safe_bool(val):
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.lower() in ('true', 'yes', '1')
            return bool(val) if val else False

        return UserRequirements(
            raw_query=query,
            service_categories=safe_list(response.get('service_categories', [])),
            expected_users=safe_int(response.get('expected_users')),
            expected_requests_per_second=safe_int(response.get('expected_requests_per_second')),
            data_size_gb=safe_float(response.get('data_size_gb')),
            min_vcpu=safe_float(response.get('min_vcpu')),
            min_memory_gb=safe_float(response.get('min_memory_gb')),
            min_storage_gb=safe_float(response.get('min_storage_gb')),
            budget_monthly_usd=safe_float(response.get('budget_monthly_usd')),
            budget_hourly_usd=safe_float(response.get('budget_hourly_usd')),
            preferred_providers=safe_list(response.get('preferred_providers', [])),
            preferred_regions=safe_list(response.get('preferred_regions', [])),
            database_engine=response.get('database_engine'),
            requires_high_availability=safe_bool(response.get('requires_high_availability')),
            requires_auto_scaling=safe_bool(response.get('requires_auto_scaling')),
            requires_encryption=safe_bool(response.get('requires_encryption')),
            use_case=response.get('use_case'),
            keywords=safe_list(response.get('keywords', []))
        )

    def _expand_query(self, query: str, requirements: UserRequirements) -> str:
        """
        Generate expanded query for better retrieval

        Args:
            query: Original query
            requirements: Extracted requirements

        Returns:
            Expanded query string
        """
        # Format requirements for prompt
        requirements_json = json.dumps(requirements.to_dict(), indent=2, default=str)

        # Format the prompt
        prompt = QUERY_EXPANSION_PROMPT.format(
            query=query,
            requirements_json=requirements_json
        )

        # Get LLM response
        expanded = self.llm.generate(prompt, temperature=0.5)

        if not expanded:
            # Fallback: basic expansion
            return self._basic_expand(query, requirements)

        # Clean up the response
        expanded = expanded.strip().strip('"').strip("'")

        return expanded

    def _basic_parse(self, query: str) -> UserRequirements:
        """
        Basic parsing when LLM fails

        Args:
            query: Raw user query

        Returns:
            UserRequirements with basic extraction
        """
        query_lower = query.lower()

        # Detect categories
        categories = []
        category_keywords = {
            'compute': ['vm', 'instance', 'server', 'compute', 'ec2', 'virtual machine'],
            'database': ['database', 'db', 'sql', 'mysql', 'postgres', 'rds', 'dynamo'],
            'storage': ['storage', 's3', 'bucket', 'blob', 'file', 'object storage'],
            'serverless': ['serverless', 'lambda', 'function', 'faas'],
            'container': ['container', 'docker', 'ecs', 'fargate', 'cloud run'],
            'kubernetes': ['kubernetes', 'k8s', 'eks', 'gke', 'aks']
        }

        for category, keywords in category_keywords.items():
            if any(kw in query_lower for kw in keywords):
                categories.append(category)

        # Extract numbers for budget
        import re
        budget = None
        budget_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', query)
        if budget_match:
            budget = float(budget_match.group(1).replace(',', ''))

        # Detect providers
        providers = []
        if 'aws' in query_lower or 'amazon' in query_lower:
            providers.append('aws')
        if 'gcp' in query_lower or 'google' in query_lower:
            providers.append('gcp')
        if 'azure' in query_lower or 'microsoft' in query_lower:
            providers.append('azure')

        return UserRequirements(
            raw_query=query,
            service_categories=categories if categories else ['compute'],
            budget_monthly_usd=budget,
            preferred_providers=providers,
            keywords=query.split()[:10]
        )

    def _basic_expand(self, query: str, requirements: UserRequirements) -> str:
        """
        Basic query expansion when LLM fails

        Args:
            query: Original query
            requirements: Extracted requirements

        Returns:
            Expanded query string
        """
        expansions = [query]

        # Add category-related terms
        category_expansions = {
            'compute': 'virtual machine VM instance server EC2 Compute Engine',
            'database': 'database DB SQL relational RDS Cloud SQL Aurora',
            'storage': 'storage S3 GCS bucket object storage blob',
            'serverless': 'serverless Lambda Functions FaaS event-driven',
            'container': 'container Docker ECS Fargate Cloud Run',
            'kubernetes': 'Kubernetes K8s EKS GKE AKS orchestration'
        }

        for category in requirements.service_categories:
            if category in category_expansions:
                expansions.append(category_expansions[category])

        # Add database engine if specified
        if requirements.database_engine:
            expansions.append(f"{requirements.database_engine} database")

        # Add keywords
        if requirements.keywords:
            expansions.extend(requirements.keywords[:5])

        return ' '.join(expansions)


if __name__ == "__main__":
    # Test the query processor
    print("\n" + "="*60)
    print("Testing Query Processor")
    print("="*60)

    processor = QueryProcessor()

    test_queries = [
        "I need a scalable database for a web application with 10,000 daily users and budget under $100/month",
        "Looking for a managed PostgreSQL database on AWS with high availability",
        "Need serverless compute for processing images, expecting 1000 requests per second",
        "Kubernetes cluster for microservices, multi-region deployment"
    ]

    for query in test_queries:
        print("\n" + "-"*60)
        requirements = processor.process(query)

        print(f"\n   Extracted Requirements:")
        req_dict = requirements.to_dict()
        for key, value in req_dict.items():
            if value and key not in ['raw_query', 'expanded_query']:
                print(f"      {key}: {value}")

        print(f"\n   Expanded Query:")
        print(f"      {requirements.expanded_query[:200]}...")