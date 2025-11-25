"""
Retriever - Stage 2
Handles hybrid retrieval combining dense (vector) and sparse (BM25) search
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny

from config import PipelineConfig, DEFAULT_CONFIG
from models import UserRequirements, RetrievedCandidate
from llm_client import EmbeddingClient


class BM25Index:
    """Simple in-memory BM25 index for sparse retrieval"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 index

        Args:
            k1: Term frequency saturation parameter
            b: Length normalization parameter
        """
        self.k1 = k1
        self.b = b
        self.documents = {}  # doc_id -> tokens
        self.doc_lengths = {}
        self.avg_doc_length = 0
        self.doc_freqs = defaultdict(int)  # term -> number of docs containing term
        self.inverted_index = defaultdict(set)  # term -> set of doc_ids
        self.N = 0  # total number of documents

    def add_document(self, doc_id: str, text: str):
        """Add a document to the index"""
        tokens = self._tokenize(text)
        self.documents[doc_id] = tokens
        self.doc_lengths[doc_id] = len(tokens)

        # Update inverted index and doc frequencies
        unique_tokens = set(tokens)
        for token in unique_tokens:
            self.doc_freqs[token] += 1
            self.inverted_index[token].add(doc_id)

        self.N += 1
        self.avg_doc_length = sum(self.doc_lengths.values()) / self.N

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        import re
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens

    def _idf(self, term: str) -> float:
        """Calculate IDF for a term"""
        df = self.doc_freqs.get(term, 0)
        if df == 0:
            return 0
        return math.log((self.N - df + 0.5) / (df + 0.5) + 1)

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Search for documents matching query

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of (doc_id, score) tuples
        """
        query_tokens = self._tokenize(query)
        scores = defaultdict(float)

        for token in query_tokens:
            if token not in self.inverted_index:
                continue

            idf = self._idf(token)

            for doc_id in self.inverted_index[token]:
                doc_tokens = self.documents[doc_id]
                tf = doc_tokens.count(token)
                doc_len = self.doc_lengths[doc_id]

                # BM25 scoring formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_length)
                scores[doc_id] += idf * numerator / denominator

        # Sort by score and return top_k
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]


class HybridRetriever:
    """Hybrid retriever combining dense and sparse search"""

    def __init__(self, config: PipelineConfig = DEFAULT_CONFIG):
        """
        Initialize the hybrid retriever

        Args:
            config: Pipeline configuration
        """
        self.config = config

        # Initialize embedding client
        self.embedder = EmbeddingClient(host=config.ollama.host, model=config.ollama.embedding_model)

        # Initialize Qdrant client
        if config.qdrant.url:
            self.qdrant = QdrantClient(url=config.qdrant.url, api_key=config.qdrant.api_key)
        else:
            self.qdrant = QdrantClient(host=config.qdrant.host, port=config.qdrant.port)

        self.collection_name = config.qdrant.collection_name

        # Initialize BM25 index
        self.bm25_index = BM25Index()
        self._build_bm25_index()

        print(" HybridRetriever initialized")

    def _build_bm25_index(self):
        """Build BM25 index from Qdrant collection"""
        print("   Building BM25 index from Qdrant collection...")

        try:
            # Scroll through all documents in collection
            offset = None
            total_indexed = 0

            while True:
                results, offset = self.qdrant.scroll( collection_name=self.collection_name, limit=100, offset=offset,
                    with_payload=True, with_vectors=False)

                if not results:
                    break

                for point in results:
                    # Create searchable text from payload
                    payload = point.payload
                    search_text = self._create_search_text(payload)
                    self.bm25_index.add_document(str(point.id), search_text)
                    total_indexed += 1

                if offset is None:
                    break

            print(f"    BM25 index built with {total_indexed} documents")

        except Exception as e:
            print(f"     Failed to build BM25 index: {str(e)}")

    def _create_search_text(self, payload: Dict[str, Any]) -> str:
        """Create searchable text from payload"""
        parts = [
            payload.get('service_name', ''),
            payload.get('description', ''),
            payload.get('short_description', ''),
            payload.get('provider', ''),
            payload.get('category', ''),
            payload.get('service_type', ''),
        ]

        # Add features
        features = payload.get('features', [])
        if features:
            parts.extend(features)

        # Add use cases
        use_cases = payload.get('use_cases', [])
        if use_cases:
            parts.extend(use_cases)

        # Add tags
        tags = payload.get('tags', [])
        if tags:
            parts.extend(tags)

        # Add specs
        specs = payload.get('specs', {})
        if specs.get('database_engine'):
            parts.append(specs['database_engine'])

        return ' '.join(str(p) for p in parts if p)

    def retrieve(self, requirements: UserRequirements) -> List[RetrievedCandidate]:
        """
        Retrieve candidate services using hybrid search

        Args:
            requirements: User requirements with expanded query

        Returns:
            List of retrieved candidates with fusion scores
        """
        print(f"\n🔍 Retrieving candidates...")

        # Use expanded query if available, otherwise raw query
        query = requirements.expanded_query or requirements.raw_query

        # Build filters based on requirements
        filters = self._build_filters(requirements)

        # Dense retrieval
        dense_results = self._dense_search(query, filters)
        print(f"   Dense search: {len(dense_results)} results")

        # Sparse retrieval (BM25)
        sparse_results = self._sparse_search(query)
        print(f"   Sparse search: {len(sparse_results)} results")

        # Fuse results
        fused_results = self._reciprocal_rank_fusion(dense_results, sparse_results)
        print(f"   Fused results: {len(fused_results)} candidates")

        # Convert to RetrievedCandidate objects
        candidates = self._fetch_candidates(fused_results)

        return candidates

    def _build_filters(self, requirements: UserRequirements) -> Optional[Filter]:
        """Build Qdrant filters based on requirements"""
        conditions = []

        # Filter by provider if specified
        if requirements.preferred_providers:
            conditions.append(
                FieldCondition(
                    key="provider",
                    match=MatchAny(any=requirements.preferred_providers)
                )
            )

        # Filter by category if specified
        if requirements.service_categories:
            conditions.append(
                FieldCondition(
                    key="category",
                    match=MatchAny(any=requirements.service_categories)
                )
            )

        if conditions:
            return Filter(must=conditions)
        return None

    def _dense_search(self, query: str, filters: Optional[Filter]) -> List[Dict[str, Any]]:
        """
        Perform dense (vector) search

        Args:
            query: Search query
            filters: Optional Qdrant filters

        Returns:
            List of {id, score, payload} dicts
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.embed(query)

            # Search Qdrant
            results = self.qdrant.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=self.config.retrieval.dense_top_k,
                query_filter=filters,
                score_threshold=self.config.retrieval.score_threshold
            )

            # print("results from qdrant", results)

            return [
                {
                    'id': str(r.id),
                    'score': r.score,
                    'payload': r.payload
                }
                for r in results.points
            ]

        except Exception as e:
            print(f"   ⚠️  Dense search error: {str(e)}")
            return []

    def _sparse_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform sparse (BM25) search

        Args:
            query: Search query

        Returns:
            List of {id, score} dicts
        """
        try:
            results = self.bm25_index.search(query, top_k=self.config.retrieval.sparse_top_k)
            return [{'id': doc_id, 'score': score} for doc_id, score in results]

        except Exception as e:
            print(f"   ⚠️  Sparse search error: {str(e)}")
            return []

    def _reciprocal_rank_fusion(self, dense_results: List[Dict], sparse_results: List[Dict],
                                k: int = 60) -> List[Tuple[str, float]]:
        """
        Combine dense and sparse results using Reciprocal Rank Fusion

        Args:
            dense_results: Results from dense search
            sparse_results: Results from sparse search
            k: RRF parameter (default 60)

        Returns:
            List of (doc_id, fused_score) tuples sorted by score
        """
        fused_scores = defaultdict(float)

        # Process dense results
        for rank, result in enumerate(dense_results, 1):
            doc_id = result['id']
            fused_scores[doc_id] += 1.0 / (k + rank)

        # Process sparse results
        for rank, result in enumerate(sparse_results, 1):
            doc_id = result['id']
            fused_scores[doc_id] += 1.0 / (k + rank)

        # Sort by fused score
        sorted_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

        # Return top-k
        return sorted_results[:self.config.retrieval.fusion_top_k]

    def _fetch_candidates(self, fused_results: List[Tuple[str, float]]) -> List[RetrievedCandidate]:
        """
        Fetch full candidate data from Qdrant

        Args:
            fused_results: List of (doc_id, fused_score) tuples

        Returns:
            List of RetrievedCandidate objects
        """
        candidates = []

        for doc_id, fusion_score in fused_results:
            try:
                # Fetch point from Qdrant
                points = self.qdrant.retrieve(
                    collection_name=self.collection_name,
                    ids=[doc_id],
                    with_payload=True
                )

                if points:
                    payload = points[0].payload
                    candidate = RetrievedCandidate.from_qdrant_payload(payload, fusion_score)
                    candidate.fusion_score = fusion_score
                    candidates.append(candidate)

            except Exception as e:
                print(f"   ⚠️  Error fetching candidate {doc_id}: {str(e)}")
                continue

        return candidates

    def dense_only_retrieve(self, query: str, top_k: int = 10, filters: Optional[Filter] = None) -> List[RetrievedCandidate]:
        """
        Simple dense-only retrieval for testing

        Args:
            query: Search query
            top_k: Number of results
            filters: Optional filters

        Returns:
            List of RetrievedCandidate objects
        """
        results = self._dense_search(query, filters)[:top_k]

        candidates = []
        for result in results:
            candidate = RetrievedCandidate.from_qdrant_payload(
                result['payload'],
                result['score']
            )
            candidates.append(candidate)

        return candidates


if __name__ == "__main__":
    # Test the retriever
    print("\n" + "="*60)
    print("Testing Hybrid Retriever")
    print("="*60)

    import argparse

    parser = argparse.ArgumentParser(description="Retriever Stage")

    parser.add_argument("--qdrant-host", type=str, default="localhost",
                        help="Qdrant host")
    parser.add_argument("--qdrant-port", type=int, default=6333,
                        help="Qdrant port")
    parser.add_argument("--qdrant-url", type=str, default="cloud-services",
                        help="Qdrant URL for Database deployment")
    parser.add_argument("--qdrant-api-key", type=str, default=None,
                        help="Qdrant API key for authentication")

    args = parser.parse_args()

    config = PipelineConfig()
    config.qdrant.host = args.qdrant_host
    config.qdrant.port = args.qdrant_port
    config.qdrant.url = args.qdrant_url
    config.qdrant.api_key = args.qdrant_api_key

    retriever = HybridRetriever(config)

    # Test with a sample query
    from models import UserRequirements

    test_requirements = UserRequirements(
        raw_query="I need a managed PostgreSQL database with high availability",
        service_categories=["database"],
        database_engine="PostgreSQL",
        requires_high_availability=True,
        expanded_query="managed PostgreSQL database high availability RDS Cloud SQL Aurora Multi-AZ relational DB"
    )

    print("\nTesting retrieval...")
    candidates = retriever.retrieve(test_requirements)

    print(f"\n📋 Retrieved {len(candidates)} candidates:")
    for i, candidate in enumerate(candidates[:25], 1):
        print(f"\n   {i}. {candidate.service_name} ({candidate.provider.upper()})")
        print(f"      Category: {candidate.category}")
        print(f"      Fusion Score: {candidate.fusion_score:.4f}")
        if candidate.price_per_unit:
            print(f"      Price: ${candidate.price_per_unit:.6f}/{candidate.price_unit}")