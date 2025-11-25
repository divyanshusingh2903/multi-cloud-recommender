"""
Scorer - Stage 4
Handles multi-dimensional scoring and final ranking fusion
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict

from config import PipelineConfig, DEFAULT_CONFIG
from models import UserRequirements, ScoredCandidate, Recommendation


class MultiDimensionalScorer:
    """Computes feature-based scores and fuses with LLM scores"""

    def __init__(self, config: PipelineConfig = DEFAULT_CONFIG):
        """
        Initialize the scorer

        Args:
            config: Pipeline configuration
        """
        self.config = config
        print("✅ MultiDimensionalScorer initialized")

    def score_and_rank(self, requirements: UserRequirements, scored_candidates: List[ScoredCandidate]) -> List[Recommendation]:
        """
        Apply multi-dimensional scoring and produce final recommendations

        Args:
            requirements: User requirements
            scored_candidates: Candidates with LLM scores

        Returns:
            List of final Recommendation objects
        """
        print(f"\n📊 Applying multi-dimensional scoring to {len(scored_candidates)} candidates...")

        # Compute feature-based scores for each candidate
        for candidate in scored_candidates:
            self._compute_feature_scores(requirements, candidate)

        # Compute final fused scores
        self._compute_final_scores(scored_candidates)

        # Sort by final score
        scored_candidates.sort(key=lambda x: x.final_score, reverse=True)

        # Apply provider diversity boost if configured
        if self.config.scoring.provider_diversity_weight > 0:
            scored_candidates = self._apply_diversity_boost(scored_candidates)

        # Convert to Recommendation objects
        recommendations = self._create_recommendations(requirements, scored_candidates)

        # Limit to top-k
        recommendations = recommendations[:self.config.top_k_results]

        print(f"   ✅ Generated {len(recommendations)} final recommendations")

        return recommendations

    def _compute_feature_scores(self, requirements: UserRequirements,
                                scored: ScoredCandidate):
        """
        Compute feature-based scores for a candidate

        Args:
            requirements: User requirements
            scored: ScoredCandidate to score
        """
        candidate = scored.candidate

        # Cost efficiency score (0-1)
        scored.cost_efficiency_score = self._compute_cost_score(requirements, candidate)

        # Capacity match score (0-1)
        scored.capacity_match_score = self._compute_capacity_score(requirements, candidate)

        # Feature match score (0-1)
        scored.feature_match_score = self._compute_feature_match_score(requirements, candidate)

    def _compute_cost_score(self, requirements: UserRequirements,
                            candidate) -> float:
        """
        Compute cost efficiency score

        Args:
            requirements: User requirements with budget
            candidate: Candidate to score

        Returns:
            Score between 0 and 1
        """
        # If no budget specified, give neutral score
        budget = requirements.budget_monthly_usd or requirements.budget_hourly_usd
        if not budget:
            return 0.5

        # If no price available, give lower score
        if not candidate.price_per_unit:
            return 0.3

        # Estimate monthly cost
        price = candidate.price_per_unit
        unit = candidate.price_unit or ''

        # Convert to monthly estimate
        if 'hour' in unit.lower():
            monthly_cost = price * 730  # Average hours per month
        elif 'month' in unit.lower():
            monthly_cost = price
        elif 'day' in unit.lower():
            monthly_cost = price * 30
        else:
            # Assume hourly if unclear
            monthly_cost = price * 730

        # Handle hourly budget
        if requirements.budget_hourly_usd and not requirements.budget_monthly_usd:
            budget = requirements.budget_hourly_usd * 730

        # Score based on budget fit
        tolerance = self.config.scoring.budget_tolerance

        if monthly_cost <= budget:
            # Under budget - score based on how much value for money
            # Closer to budget = potentially more capable service
            ratio = monthly_cost / budget
            return 0.7 + (ratio * 0.3)  # 0.7 to 1.0
        elif monthly_cost <= budget * tolerance:
            # Slightly over budget - acceptable
            overage = (monthly_cost - budget) / (budget * (tolerance - 1))
            return 0.5 - (overage * 0.2)  # 0.3 to 0.5
        else:
            # Over budget
            overage_ratio = monthly_cost / budget
            return max(0.1, 0.3 - (overage_ratio - tolerance) * 0.1)

    def _compute_capacity_score(self, requirements: UserRequirements,
                                candidate) -> float:
        """
        Compute capacity match score

        Args:
            requirements: User requirements
            candidate: Candidate to score

        Returns:
            Score between 0 and 1
        """
        scores = []

        # vCPU match
        if requirements.min_vcpu and candidate.vcpu:
            if candidate.vcpu >= requirements.min_vcpu:
                # Meets or exceeds - score based on how close
                ratio = requirements.min_vcpu / candidate.vcpu
                scores.append(0.7 + (ratio * 0.3))
            else:
                # Below requirement
                ratio = candidate.vcpu / requirements.min_vcpu
                scores.append(ratio * 0.6)

        # Memory match
        if requirements.min_memory_gb and candidate.memory_gb:
            if candidate.memory_gb >= requirements.min_memory_gb:
                ratio = requirements.min_memory_gb / candidate.memory_gb
                scores.append(0.7 + (ratio * 0.3))
            else:
                ratio = candidate.memory_gb / requirements.min_memory_gb
                scores.append(ratio * 0.6)

        # If no capacity requirements specified, use neutral score
        if not scores:
            return 0.5

        return sum(scores) / len(scores)

    def _compute_feature_match_score(self, requirements: UserRequirements,
                                     candidate) -> float:
        """
        Compute feature match score

        Args:
            requirements: User requirements
            candidate: Candidate to score

        Returns:
            Score between 0 and 1
        """
        score = 0.5  # Base score
        matches = 0
        requirements_count = 0

        # Database engine match
        if requirements.database_engine:
            requirements_count += 1
            if candidate.database_engine:
                if requirements.database_engine.lower() in candidate.database_engine.lower():
                    matches += 1

        # High availability
        if requirements.requires_high_availability:
            requirements_count += 1
            if candidate.supports_multi_az:
                matches += 1

        # Auto-scaling
        if requirements.requires_auto_scaling:
            requirements_count += 1
            if candidate.supports_auto_scaling:
                matches += 1

        # Encryption
        if requirements.requires_encryption:
            requirements_count += 1
            if candidate.supports_encryption:
                matches += 1

        # Calculate score
        if requirements_count > 0:
            score = matches / requirements_count

        return score

    def _compute_final_scores(self, scored_candidates: List[ScoredCandidate]):
        """
        Compute final fused scores for all candidates

        Args:
            scored_candidates: Candidates with feature scores
        """
        weights = self.config.scoring

        for scored in scored_candidates:
            # Normalize LLM score to 0-1 scale
            llm_normalized = scored.llm_relevance_score / 10.0

            # Weighted combination
            final = (
                    llm_normalized * weights.llm_relevance_weight +
                    scored.cost_efficiency_score * weights.cost_efficiency_weight +
                    scored.capacity_match_score * weights.capacity_match_weight +
                    scored.feature_match_score * weights.provider_diversity_weight  # Reusing weight
            )

            scored.final_score = final

    def _apply_diversity_boost(self, scored_candidates: List[ScoredCandidate]) -> List[ScoredCandidate]:
        """
        Apply diversity boost to ensure multi-provider representation

        Args:
            scored_candidates: Sorted candidates

        Returns:
            Re-ordered candidates with diversity
        """
        if len(scored_candidates) <= 2:
            return scored_candidates

        # Track seen providers
        seen_providers = set()
        diverse_results = []
        remaining = []

        # First pass: take best from each provider
        for candidate in scored_candidates:
            provider = candidate.candidate.provider
            if provider not in seen_providers:
                diverse_results.append(candidate)
                seen_providers.add(provider)
            else:
                remaining.append(candidate)

        # Second pass: add remaining in order
        diverse_results.extend(remaining)

        # Re-assign final scores with small diversity bonus for variety
        # Top result from each provider gets slight boost
        provider_top = set()
        for i, candidate in enumerate(diverse_results):
            provider = candidate.candidate.provider
            if provider not in provider_top:
                candidate.final_score *= 1.05  # 5% boost
                provider_top.add(provider)

        # Re-sort by adjusted scores
        diverse_results.sort(key=lambda x: x.final_score, reverse=True)

        return diverse_results

    def _create_recommendations(self, requirements: UserRequirements,
                                scored_candidates: List[ScoredCandidate]) -> List[Recommendation]:
        """
        Convert scored candidates to Recommendation objects

        Args:
            requirements: User requirements
            scored_candidates: Scored and ranked candidates

        Returns:
            List of Recommendation objects
        """
        recommendations = []

        for rank, scored in enumerate(scored_candidates, 1):
            candidate = scored.candidate

            # Build specs summary
            specs_parts = []
            if candidate.vcpu:
                specs_parts.append(f"{candidate.vcpu} vCPU")
            if candidate.memory_gb:
                specs_parts.append(f"{candidate.memory_gb} GB RAM")
            if candidate.storage_type:
                specs_parts.append(candidate.storage_type)
            if candidate.database_engine:
                specs_parts.append(f"{candidate.database_engine}")
            specs_summary = ', '.join(specs_parts) if specs_parts else 'Specs vary by configuration'

            # Build pricing summary
            if candidate.price_per_unit:
                unit = candidate.price_unit or 'unit'
                pricing_summary = f"${candidate.price_per_unit:.4f} per {unit}"

                # Add monthly estimate if hourly
                if 'hour' in unit.lower():
                    monthly = candidate.price_per_unit * 730
                    pricing_summary += f" (~${monthly:.2f}/month)"
            else:
                pricing_summary = "Pricing varies by configuration"

            # Build matches and concerns from LLM evaluation
            matches = self._identify_matches(requirements, candidate, scored)
            concerns = self._identify_concerns(requirements, candidate, scored)

            recommendation = Recommendation(
                rank=rank,
                service_id=candidate.service_id,
                provider=candidate.provider,
                service_name=candidate.service_name,
                service_type=candidate.service_type,
                category=candidate.category,
                description=candidate.description,
                short_description=candidate.short_description,
                specs_summary=specs_summary,
                pricing_summary=pricing_summary,
                explanation=scored.llm_explanation,
                relevance_score=scored.llm_relevance_score,
                final_score=scored.final_score,
                key_features=candidate.features[:5] if candidate.features else [],
                matches=matches,
                concerns=concerns,
                region=candidate.region,
                full_payload=candidate.raw_payload
            )

            recommendations.append(recommendation)

        return recommendations

    def _identify_matches(self, requirements: UserRequirements,
                          candidate, scored: ScoredCandidate) -> List[str]:
        """Identify what requirements the candidate matches"""
        matches = []

        # Category match
        if candidate.category in requirements.service_categories:
            matches.append(f"Matches required category: {candidate.category}")

        # Database engine
        if requirements.database_engine and candidate.database_engine:
            if requirements.database_engine.lower() in candidate.database_engine.lower():
                matches.append(f"Supports {requirements.database_engine}")

        # Budget
        if scored.cost_efficiency_score >= 0.7:
            matches.append("Within budget")

        # Features
        if requirements.requires_high_availability and candidate.supports_multi_az:
            matches.append("High availability supported")

        if requirements.requires_auto_scaling and candidate.supports_auto_scaling:
            matches.append("Auto-scaling supported")

        if requirements.requires_encryption and candidate.supports_encryption:
            matches.append("Encryption supported")

        return matches

    def _identify_concerns(self, requirements: UserRequirements,
                           candidate, scored: ScoredCandidate) -> List[str]:
        """Identify potential concerns or mismatches"""
        concerns = []

        # Budget concern
        if scored.cost_efficiency_score < 0.5:
            concerns.append("May exceed budget")

        # Capacity concern
        if scored.capacity_match_score < 0.5:
            concerns.append("Capacity may be insufficient")

        # Missing features
        if requirements.requires_high_availability and not candidate.supports_multi_az:
            concerns.append("High availability not confirmed")

        if requirements.requires_auto_scaling and not candidate.supports_auto_scaling:
            concerns.append("Auto-scaling not confirmed")

        return concerns


if __name__ == "__main__":
    # Test the scorer
    print("\n" + "="*60)
    print("Testing Multi-Dimensional Scorer")
    print("="*60)

    scorer = MultiDimensionalScorer()

    # Create mock data for testing
    from models import UserRequirements, RetrievedCandidate, ScoredCandidate

    test_requirements = UserRequirements(
        raw_query="I need a managed PostgreSQL database for a web app, budget $100/month",
        service_categories=["database"],
        expected_users=10000,
        budget_monthly_usd=100,
        database_engine="PostgreSQL",
        requires_high_availability=True,
        use_case="web application"
    )

    # Mock scored candidates
    mock_scored = [
        ScoredCandidate(
            candidate=RetrievedCandidate(
                service_id="aws_rds_postgresql_1",
                provider="aws",
                service_name="RDS PostgreSQL db.t3.micro",
                service_type="rds",
                category="database",
                description="Amazon RDS PostgreSQL",
                short_description="RDS PostgreSQL: 2 vCPU, 1 GB RAM",
                vcpu=2,
                memory_gb=1,
                database_engine="PostgreSQL",
                price_per_unit=0.017,
                price_unit="hour",
                features=["Automated backups", "Multi-AZ"],
                supports_auto_scaling=True,
                supports_multi_az=True,
                supports_encryption=True
            ),
            llm_relevance_score=8.5,
            llm_explanation="Excellent match for PostgreSQL needs with managed service benefits."
        ),
        ScoredCandidate(
            candidate=RetrievedCandidate(
                service_id="gcp_cloudsql_postgresql_1",
                provider="gcp",
                service_name="Cloud SQL PostgreSQL",
                service_type="cloud_sql",
                category="database",
                description="Google Cloud SQL PostgreSQL",
                short_description="Cloud SQL PostgreSQL: 1 vCPU, 3.75 GB RAM",
                vcpu=1,
                memory_gb=3.75,
                database_engine="PostgreSQL",
                price_per_unit=0.025,
                price_unit="hour",
                features=["Automatic backups", "High availability"],
                supports_auto_scaling=True,
                supports_multi_az=True,
                supports_encryption=True
            ),
            llm_relevance_score=8.0,
            llm_explanation="Good PostgreSQL option with competitive pricing."
        )
    ]

    print("\nTesting scoring and ranking...")
    recommendations = scorer.score_and_rank(test_requirements, mock_scored)

    print(f"\n📋 Final Recommendations:")
    for rec in recommendations:
        print(f"\n   #{rec.rank}: {rec.service_name} ({rec.provider.upper()})")
        print(f"      Final Score: {rec.final_score:.3f}")
        print(f"      LLM Score: {rec.relevance_score}/10")
        print(f"      Specs: {rec.specs_summary}")
        print(f"      Pricing: {rec.pricing_summary}")
        print(f"      Matches: {', '.join(rec.matches)}")
        if rec.concerns:
            print(f"      Concerns: {', '.join(rec.concerns)}")