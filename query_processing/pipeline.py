"""
Recommendation Pipeline
Orchestrates the full query processing flow: understand → retrieve → rerank → score
"""

import time
import json
from typing import List, Dict, Any, Optional

from config import PipelineConfig, DEFAULT_CONFIG
from models import UserRequirements, PipelineResult, Recommendation
from query_processor import QueryProcessor
from retriever import HybridRetriever
from reranker import LLMReranker
from scorer import MultiDimensionalScorer
from llm_client import LLMClient
from prompts import SUMMARY_SYSTEM, SUMMARY_PROMPT


class RecommendationPipeline:
    """Main pipeline orchestrating all stages of recommendation"""

    def __init__(self, config: PipelineConfig = DEFAULT_CONFIG):
        """
        Initialize the recommendation pipeline

        Args:
            config: Pipeline configuration
        """
        print("="*80)
        print("INITIALIZING RECOMMENDATION PIPELINE")
        print("="*80)

        self.config = config

        # Initialize all components
        print("\n Initializing components...")

        self.query_processor = QueryProcessor(config)
        self.retriever = HybridRetriever(config)
        self.reranker = LLMReranker(config)
        self.scorer = MultiDimensionalScorer(config)

        # LLM for summary generation
        self.llm = LLMClient(host=config.ollama.host,model=config.ollama.chat_model,temperature=config.ollama.temperature)

        print("\n" + "="*80)
        print(" PIPELINE READY")
        print("="*80)

    def recommend(self, query: str, top_k: Optional[int] = None) -> PipelineResult:
        """
        Generate recommendations for a user query

        Args:
            query: Natural language query describing infrastructure needs
            top_k: Number of recommendations (overrides config)

        Returns:
            PipelineResult with recommendations and metadata
        """
        start_time = time.time()

        print("\n" + "="*80)
        print(" STARTING RECOMMENDATION PIPELINE")
        print("="*80)
        print(f"\n Query: \"{query}\"")

        # Override top_k if specified
        if top_k:
            self.config.top_k_results = top_k

        # Stage 1: Query Understanding
        print("\n" + "-"*40)
        print("STAGE 1: Query Understanding")
        print("-"*40)
        requirements = self.query_processor.process(query)

        # Stage 2: Hybrid Retrieval
        print("\n" + "-"*40)
        print("STAGE 2: Hybrid Retrieval")
        print("-"*40)
        candidates = self.retriever.retrieve(requirements)

        if not candidates:
            print("     No candidates found!")
            return self._empty_result(query, requirements, time.time() - start_time)

        # Stage 3: LLM Reranking
        print("\n" + "-"*40)
        print("STAGE 3: LLM Reranking")
        print("-"*40)
        scored_candidates = self.reranker.rerank(requirements, candidates)

        if not scored_candidates:
            print("     No candidates passed reranking!")
            return self._empty_result(query, requirements, time.time() - start_time)

        # Stage 4: Multi-dimensional Scoring
        print("\n" + "-"*40)
        print("STAGE 4: Multi-dimensional Scoring")
        print("-"*40)
        recommendations = self.scorer.score_and_rank(requirements, scored_candidates)

        # Generate summary
        print("\n" + "-"*40)
        print("Generating Summary")
        print("-"*40)
        summary = self._generate_summary(query, recommendations)

        # Generate provider comparison if multiple providers
        provider_comparison = self._generate_provider_comparison(requirements, recommendations)

        # Create result
        processing_time = time.time() - start_time

        result = PipelineResult(
            query=query,
            requirements=requirements,
            recommendations=recommendations,
            summary=summary,
            provider_comparison=provider_comparison,
            total_candidates_retrieved=len(candidates),
            total_candidates_reranked=len(scored_candidates),
            processing_time_seconds=processing_time
        )

        # Print results
        self._print_results(result)

        return result

    def _generate_summary(self, query: str, recommendations: List[Recommendation]) -> str:
        """Generate natural language summary of recommendations"""
        if not recommendations:
            return "No matching services found for your requirements."

        # Format recommendations for prompt
        rec_summary = []
        for rec in recommendations[:5]:
            rec_summary.append(
                f"#{rec.rank}: {rec.service_name} ({rec.provider.upper()}) - "
                f"Score: {rec.relevance_score}/10 - {rec.pricing_summary}"
            )

        prompt = SUMMARY_PROMPT.format(
            query=query,
            recommendations='\n'.join(rec_summary)
        )

        summary = self.llm.generate(prompt, system_prompt=SUMMARY_SYSTEM, max_tokens=500)

        if not summary:
            # Fallback summary
            top = recommendations[0]
            summary = (
                f"Based on your requirements, the top recommendation is {top.service_name} "
                f"from {top.provider.upper()}. {top.explanation}"
            )

        return summary

    def _generate_provider_comparison(self, requirements: UserRequirements, recommendations: List[Recommendation]) -> Dict[str, Any]:
        """Generate comparison across providers"""
        # Group recommendations by provider
        by_provider = {}
        for rec in recommendations:
            provider = rec.provider
            if provider not in by_provider:
                by_provider[provider] = rec

        if len(by_provider) < 2:
            return {}

        comparison = {
            'providers_found': list(by_provider.keys()),
            'best_per_provider': {}
        }

        for provider, rec in by_provider.items():
            comparison['best_per_provider'][provider] = {
                'service_name': rec.service_name,
                'score': rec.relevance_score,
                'pricing': rec.pricing_summary,
                'key_features': rec.key_features[:3]
            }

        return comparison

    def _empty_result(self, query: str, requirements: UserRequirements, processing_time: float) -> PipelineResult:
        """Create empty result when no recommendations found"""
        return PipelineResult(
            query=query,
            requirements=requirements,
            recommendations=[],
            summary="No matching cloud services found for your requirements. Try broadening your search criteria.",
            provider_comparison={},
            total_candidates_retrieved=0,
            total_candidates_reranked=0,
            processing_time_seconds=processing_time
        )

    def _print_results(self, result: PipelineResult):
        """Print formatted results"""
        print("\n" + "="*80)
        print(" RECOMMENDATION RESULTS")
        print("="*80)

        print(f"\n️  Processing time: {result.processing_time_seconds:.2f}s")
        print(f" Retrieved: {result.total_candidates_retrieved} → Reranked: {result.total_candidates_reranked} → Final: {len(result.recommendations)}")

        print("\n" + "-"*40)
        print("TOP RECOMMENDATIONS")
        print("-"*40)

        for rec in result.recommendations:
            print(f"\n #{rec.rank}: {rec.service_name}")
            print(f"   Provider: {rec.provider.upper()}")
            print(f"   Category: {rec.category}")
            print(f"   Score: {rec.relevance_score}/10 (Final: {rec.final_score:.3f})")
            print(f"   Specs: {rec.specs_summary}")
            print(f"   Pricing: {rec.pricing_summary}")
            print(f"   Explanation: {rec.explanation[:200]}...")

            if rec.matches:
                print(f"    Matches: {', '.join(rec.matches[:3])}")
            if rec.concerns:
                print(f"     Concerns: {', '.join(rec.concerns[:2])}")

        print("\n" + "-"*40)
        print("SUMMARY")
        print("-"*40)
        print(f"\n{result.summary}")

        if result.provider_comparison:
            print("\n" + "-"*40)
            print("MULTI-CLOUD COMPARISON")
            print("-"*40)
            for provider, info in result.provider_comparison.get('best_per_provider', {}).items():
                print(f"\n   {provider.upper()}: {info['service_name']}")
                print(f"      Score: {info['score']}/10")
                print(f"      Pricing: {info['pricing']}")

    def recommend_simple(self, query: str) -> List[Dict[str, Any]]:
        """
        Simple interface returning just the recommendations as dicts

        Args:
            query: Natural language query

        Returns:
            List of recommendation dictionaries
        """
        result = self.recommend(query)
        return [rec.to_dict() for rec in result.recommendations]


def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Cloud Service Recommendation Pipeline")
    parser.add_argument("query", nargs='?', type=str,
                        help="Natural language query for recommendations")
    parser.add_argument("--top-k", type=int, default=5,
                        help="Number of recommendations to return")
    parser.add_argument("--qdrant-host", type=str, default="localhost",
                        help="Qdrant host")
    parser.add_argument("--qdrant-port", type=int, default=6333,
                        help="Qdrant port")
    parser.add_argument("--qdrant-url", type=str, default="cloud-services",
                        help="Qdrant URL for Database deployment")
    parser.add_argument("--qdrant-api-key", type=str, default=None,
                        help="Qdrant API key for authentication")
    parser.add_argument("--ollama-host", type=str, default="http://localhost:11434",
                        help="Ollama API endpoint")
    parser.add_argument("--chat-model", type=str, default="gemma3:4b",
                        help="LLM model for chat/reasoning")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file for JSON results")
    parser.add_argument("--interactive", action="store_true",
                        help="Run in interactive mode")

    args = parser.parse_args()

    # Configure pipeline
    config = PipelineConfig()
    config.qdrant.host = args.qdrant_host
    config.qdrant.port = args.qdrant_port
    config.qdrant.url = args.qdrant_url
    config.qdrant.api_key = args.qdrant_api_key
    config.ollama.host = args.ollama_host
    config.ollama.chat_model = args.chat_model
    config.top_k_results = args.top_k

    # Initialize pipeline
    pipeline = RecommendationPipeline(config)

    if args.interactive:
        # Interactive mode
        print("\n" + "="*80)
        print(" INTERACTIVE RECOMMENDATION MODE")
        print("="*80)
        print("Enter your infrastructure requirements (or 'quit' to exit)")

        while True:
            print("\n" + "-"*40)
            query = input("Your query: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            if not query:
                continue

            result = pipeline.recommend(query)

            # Optionally save to file
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result.to_dict(), f, indent=2)
                print(f"\n Results saved to {args.output}")

    elif args.query:
        # Single query mode
        result = pipeline.recommend(args.query)

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
            print(f"\n Results saved to {args.output}")

    else:
        # Demo mode with sample queries
        print("\n" + "="*80)
        print(" DEMO MODE - Running sample queries")
        print("="*80)

        demo_queries = [
            "I need a managed PostgreSQL database for a web application with 10,000 daily users and budget under $100/month",
            "Looking for serverless compute for image processing, expecting 1000 requests per second",
            "Need a Kubernetes cluster for microservices deployment with auto-scaling"
        ]

        for i, query in enumerate(demo_queries, 1):
            print(f"\n\n{'#'*80}")
            print(f"# DEMO QUERY {i}/{len(demo_queries)}")
            print(f"{'#'*80}")

            result = pipeline.recommend(query)

            print("\n" + "="*40)
            input("Press Enter to continue to next demo query...")


if __name__ == "__main__":
    main()