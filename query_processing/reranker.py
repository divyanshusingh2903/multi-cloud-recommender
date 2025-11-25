"""
Reranker - Stage 3
Pairwise LLM Reranker with Sliding Window

Based on CSCE 670 Lecture 23: Large Language Models for Ranking
Implements PRP-Sliding approach (Qin et al., NAACL 2024)
"""

from typing import List
from config import PipelineConfig, DEFAULT_CONFIG
from models import UserRequirements, RetrievedCandidate, ScoredCandidate
from llm_client import LLMClient


class LLMReranker:
    """
    Pairwise LLM Reranker using sliding window approach.

    From Lecture 23:
    - Given query q and two documents d1, d2, predict which is more relevant
    - Uses sliding window (back-to-first bubblesort) for O(N) API calls
    - k passes guarantee top-k accuracy
    """

    def __init__(self, config: PipelineConfig = DEFAULT_CONFIG):
        """
        Initialize the LLM reranker

        Args:
            config: Pipeline configuration
        """
        self.config = config

        # Initialize LLM client
        self.llm = LLMClient(
            host=config.ollama.host,
            model=config.ollama.chat_model,
            temperature=config.ollama.temperature,
            timeout=config.ollama.timeout
        )

        # Number of bubblesort passes (k passes guarantees top-k accuracy)
        self.num_passes = min(config.top_k_results, 3)

        print("✅ LLMReranker initialized (Pairwise + Sliding Window)")

    def _format_candidate(self, candidate: RetrievedCandidate) -> str:
        """Format a candidate for the comparison prompt"""
        parts = [
            f"Service: {candidate.service_name}",
            f"Provider: {candidate.provider.upper()}",
            f"Category: {candidate.category}",
            f"Description: {candidate.short_description or candidate.description[:200]}"
        ]

        if candidate.vcpu:
            parts.append(f"vCPU: {candidate.vcpu}")
        if candidate.memory_gb:
            parts.append(f"Memory: {candidate.memory_gb} GB")
        if candidate.database_engine:
            parts.append(f"Database: {candidate.database_engine}")
        if candidate.price_per_unit:
            parts.append(f"Price: ${candidate.price_per_unit:.6f} per {candidate.price_unit or 'unit'}")
        if candidate.features:
            parts.append(f"Features: {', '.join(candidate.features[:3])}")

        return "\n".join(parts)

    def _compare_pair(self, query: str, candidate_a: RetrievedCandidate, candidate_b: RetrievedCandidate) -> str:
        """
        Compare two candidates and return which is more relevant.

        Prompt based on Lecture 23, Slide 26:
        "Given a query {query}, which of the following two passages is more
         relevant to the query? Output Passage A or Passage B"

        Returns: "A" or "B"
        """
        prompt = f"""Given a query, which of the following two cloud services is more relevant?

Query: {query}

Service A:
{self._format_candidate(candidate_a)}

Service B:
{self._format_candidate(candidate_b)}

Which service better matches the query requirements? Output only "A" or "B"."""

        try:
            response = self.llm.generate(prompt, max_tokens=10)
            result = response.strip().upper()

            # Extract A or B from response
            if "A" in result and "B" not in result:
                return "A"
            elif "B" in result and "A" not in result:
                return "B"
            elif result.startswith("A"):
                return "A"
            elif result.startswith("B"):
                return "B"
            else:
                # Default: keep original order
                return "A"

        except Exception as e:
            print(f"    Warning: Comparison failed ({str(e)}), keeping original order")
            return "A"

    def rerank(self, requirements: UserRequirements, candidates: List[RetrievedCandidate]) -> List[ScoredCandidate]:
        """
        Rerank candidates using pairwise comparisons with sliding window.

        Implements PRP-Sliding from Lecture 23 (Slides 27-28):
        - Back-to-first bubblesort
        - k passes guarantee top-k documents are correct
        - O(k*N) API calls total

        Args:
            requirements: User requirements (uses raw_query)
            candidates: List of retrieved candidates to rerank

        Returns:
            List of ScoredCandidate objects (ranked by position)
        """
        if len(candidates) <= 1:
            return [ScoredCandidate(candidate=c, llm_relevance_score=10.0 - i)
                    for i, c in enumerate(candidates)]

        # Limit candidates
        candidates_to_rank = candidates[:self.config.reranking.max_candidates]
        query = requirements.raw_query

        print(f"\n🔄 Reranking {len(candidates_to_rank)} candidates (pairwise sliding window)")
        print(f"   Passes: {self.num_passes}, API calls: ~{self.num_passes * (len(candidates_to_rank) - 1)}")

        # Create working copy
        ranked = list(candidates_to_rank)

        # Perform k passes of bubblesort (back-to-first)
        for pass_num in range(self.num_passes):
            swaps = 0

            # Back-to-first: start from the end, bubble up the best
            for i in range(len(ranked) - 1, 0, -1):
                winner = self._compare_pair(query, ranked[i - 1], ranked[i])

                if winner == "B":
                    # Swap: B (position i) is better than A (position i-1)
                    ranked[i - 1], ranked[i] = ranked[i], ranked[i - 1]
                    swaps += 1

            print(f"   Pass {pass_num + 1}/{self.num_passes}: {swaps} swaps")

        # Convert to ScoredCandidate with position-based scores
        # Higher score = better rank (top position gets highest score)
        scored_candidates = []
        for i, candidate in enumerate(ranked):
            # Score from 10 (best) down to 1 (worst)
            score = 10.0 - (i * 9.0 / max(len(ranked) - 1, 1))
            scored_candidates.append(ScoredCandidate(
                candidate=candidate,
                llm_relevance_score=score,
                llm_explanation=f"Ranked #{i + 1} by pairwise comparison"
            ))

        print(f"✅ Reranking complete")
        return scored_candidates


if __name__ == "__main__":
    # Test the reranker
    print("\n" + "=" * 60)
    print("Testing Pairwise LLM Reranker")
    print("=" * 60)

    reranker = LLMReranker()

    # Create mock data for testing
    test_requirements = UserRequirements(
        raw_query="I need a managed PostgreSQL database for a web app with 10000 users, budget $100/month",
        service_categories=["database"],
        expected_users=10000,
        budget_monthly_usd=100,
        database_engine="PostgreSQL",
        use_case="web application"
    )

    # Mock candidates
    mock_candidates = [
        RetrievedCandidate(
            service_id="aws_ec2_t3_micro",
            provider="aws",
            service_name="EC2 t3.micro",
            service_type="ec2",
            category="compute",
            description="General purpose compute instance",
            short_description="2 vCPU, 1 GB RAM",
            vcpu=2,
            memory_gb=1,
            price_per_unit=0.0104,
            price_unit="hour",
            features=["Burstable", "EBS optimized"]
        ),
        RetrievedCandidate(
            service_id="aws_rds_postgresql",
            provider="aws",
            service_name="RDS PostgreSQL db.t3.micro",
            service_type="rds",
            category="database",
            description="Amazon RDS PostgreSQL managed database instance",
            short_description="RDS PostgreSQL: 2 vCPU, 1 GB RAM",
            vcpu=2,
            memory_gb=1,
            database_engine="PostgreSQL",
            price_per_unit=0.017,
            price_unit="hour",
            features=["Automated backups", "Multi-AZ available", "Point-in-time recovery"]
        ),
        RetrievedCandidate(
            service_id="gcp_cloudsql_postgresql",
            provider="gcp",
            service_name="Cloud SQL PostgreSQL",
            service_type="cloud_sql",
            category="database",
            description="Google Cloud SQL PostgreSQL managed database",
            short_description="Cloud SQL PostgreSQL: 1 vCPU, 3.75 GB RAM",
            vcpu=1,
            memory_gb=3.75,
            database_engine="PostgreSQL",
            price_per_unit=0.025,
            price_unit="hour",
            features=["Automatic backups", "High availability", "Encryption"]
        ),
        RetrievedCandidate(
            service_id="aws_lambda",
            provider="aws",
            service_name="AWS Lambda",
            service_type="lambda",
            category="serverless",
            description="Serverless compute service",
            short_description="Event-driven serverless functions",
            price_per_unit=0.0000002,
            price_unit="request",
            features=["Auto-scaling", "Pay per use", "Event-driven"]
        ),
    ]

    print(f"\nQuery: {test_requirements.raw_query}")
    print(f"\nOriginal order:")
    for i, c in enumerate(mock_candidates, 1):
        print(f"  {i}. {c.service_name} ({c.provider}) - {c.category}")

    # Rerank
    scored = reranker.rerank(test_requirements, mock_candidates)

    print(f"\n📋 Reranked Results:")
    for i, s in enumerate(scored, 1):
        print(f"  {i}. {s.candidate.service_name} ({s.candidate.provider})")
        print(f"     Score: {s.llm_relevance_score:.1f}/10 - {s.llm_explanation}")