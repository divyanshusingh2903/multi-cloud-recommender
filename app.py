"""
Multi-Cloud Infrastructure Recommender System
Interactive Streamlit Application

This application provides a chat-based interface for querying cloud service recommendations
across AWS, GCP, and Azure using LLM-enhanced retrieval and ranking.

Redesigned: Configuration on welcome screen, then transitions to chatbot after initialization.
"""

import streamlit as st
import time
from typing import Dict, Any, Optional

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "query_processing"))

# These imports will work once the path is set correctly
try:
    from query_processing.config import PipelineConfig
    from query_processing.models import Recommendation
    from query_processing.query_processor import QueryProcessor
    from query_processing.retriever import HybridRetriever
    from query_processing.reranker import LLMReranker
    from query_processing.scorer import MultiDimensionalScorer
    from query_processing.llm_client import LLMClient, EmbeddingClient
    from query_processing.prompts import SUMMARY_SYSTEM, SUMMARY_PROMPT
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Page configuration
st.set_page_config(
    page_title="Cloud Service Recommender",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Hide sidebar by default */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Welcome screen styling */
    .welcome-header {
        text-align: center;
        padding: 2rem 0;
    }
    
    .config-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .stExpander {
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    
    /* Center the initialize button */
    .init-button {
        display: flex;
        justify-content: center;
        margin-top: 2rem;
    }
    
    /* Status messages */
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# Helper Functions
# ==============================================================================

def get_provider_icon(provider: str) -> str:
    """Get icon for provider"""
    icons = {'aws': '🔶', 'gcp': '🔵', 'azure': '🔷'}
    return icons.get(provider.lower(), '☁️')


def render_recommendation_card(rec: Recommendation):
    """Render a recommendation as a styled card"""
    provider_icon = get_provider_icon(rec.provider)

    with st.container():
        col1, col2, col3 = st.columns([0.5, 3, 1])

        with col1:
            st.markdown(f"### #{rec.rank}")

        with col2:
            st.markdown(f"**{provider_icon} {rec.service_name}**")
            st.caption(f"{rec.provider.upper()} | {rec.category} | {rec.region}")

        with col3:
            st.metric("Score", f"{rec.relevance_score:.1f}/10")

        st.markdown(f"**Specs:** {rec.specs_summary}")
        st.markdown(f"**Pricing:** {rec.pricing_summary}")

        if rec.key_features:
            st.markdown(f"**Features:** {', '.join(rec.key_features[:4])}")

        if rec.matches:
            st.success(f"✓ {' | '.join(rec.matches[:3])}")

        if rec.concerns:
            st.warning(f"⚠ {' | '.join(rec.concerns[:2])}")

        with st.expander("View Details"):
            st.markdown(f"**Description:** {rec.description[:500]}...")
            st.markdown(f"**Service ID:** `{rec.service_id}`")
            st.markdown(f"**Final Score:** {rec.final_score:.4f}")

        st.divider()


def render_additional_recommendations_table(recommendations: list):
    """Render additional recommendations (beyond top 5) in an expandable table"""
    if len(recommendations) <= 5:
        return

    additional_recs = recommendations[5:]

    with st.expander(f"📊 View {len(additional_recs)} More Recommendations", expanded=False):
        # Prepare data for the table
        table_data = []
        for rec in additional_recs:
            provider_icon = get_provider_icon(rec.provider)
            table_data.append({
                "Rank": f"#{rec.rank}",
                "Provider": f"{provider_icon} {rec.provider.upper()}",
                "Service": rec.service_name,
                "Category": rec.category,
                "Score": f"{rec.relevance_score:.1f}/10",
                "Specs": rec.specs_summary[:50] + "..." if len(rec.specs_summary) > 50 else rec.specs_summary,
                "Pricing": rec.pricing_summary,
                "Region": rec.region
            })

        # Display as dataframe
        import pandas as pd
        df = pd.DataFrame(table_data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.TextColumn("Rank", width="small"),
                "Provider": st.column_config.TextColumn("Provider", width="small"),
                "Service": st.column_config.TextColumn("Service", width="medium"),
                "Category": st.column_config.TextColumn("Category", width="small"),
                "Score": st.column_config.TextColumn("Score", width="small"),
                "Specs": st.column_config.TextColumn("Specs", width="medium"),
                "Pricing": st.column_config.TextColumn("Pricing", width="medium"),
                "Region": st.column_config.TextColumn("Region", width="small"),
            }
        )

        # Option to view details of any additional recommendation
        st.markdown("---")
        st.markdown("**View detailed information:**")

        selected_rank = st.selectbox(
            "Select a recommendation to view details",
            options=[f"#{rec.rank} - {rec.service_name} ({rec.provider.upper()})" for rec in additional_recs],
            key="additional_rec_selector"
        )

        if selected_rank:
            # Find the selected recommendation
            selected_idx = int(selected_rank.split("#")[1].split(" -")[0]) - 1
            selected_rec = recommendations[selected_idx]

            st.markdown(f"### {get_provider_icon(selected_rec.provider)} {selected_rec.service_name}")

            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:
                st.markdown(f"**Provider:** {selected_rec.provider.upper()}")
                st.markdown(f"**Category:** {selected_rec.category}")
                st.markdown(f"**Region:** {selected_rec.region}")
                st.markdown(f"**Relevance Score:** {selected_rec.relevance_score:.1f}/10")
                st.markdown(f"**Final Score:** {selected_rec.final_score:.4f}")

            with detail_col2:
                st.markdown(f"**Specs:** {selected_rec.specs_summary}")
                st.markdown(f"**Pricing:** {selected_rec.pricing_summary}")

            st.markdown(f"**Description:** {selected_rec.description}")

            if selected_rec.key_features:
                st.markdown(f"**Features:** {', '.join(selected_rec.key_features)}")

            if selected_rec.matches:
                st.success(f"✓ Matches: {' | '.join(selected_rec.matches)}")

            if selected_rec.concerns:
                st.warning(f"⚠ Concerns: {' | '.join(selected_rec.concerns)}")

            st.code(f"Service ID: {selected_rec.service_id}")


def render_additional_recommendations_table_history(recommendations: list, msg_idx: int):
    """Render additional recommendations table for chat history with unique keys"""
    if len(recommendations) <= 5:
        return

    additional_recs = recommendations[5:]

    with st.expander(f"📊 View {len(additional_recs)} More Recommendations", expanded=False):
        # Prepare data for the table
        table_data = []
        for rec in additional_recs:
            provider_icon = get_provider_icon(rec.provider)
            table_data.append({
                "Rank": f"#{rec.rank}",
                "Provider": f"{provider_icon} {rec.provider.upper()}",
                "Service": rec.service_name,
                "Category": rec.category,
                "Score": f"{rec.relevance_score:.1f}/10",
                "Specs": rec.specs_summary[:50] + "..." if len(rec.specs_summary) > 50 else rec.specs_summary,
                "Pricing": rec.pricing_summary,
                "Region": rec.region
            })

        # Display as dataframe
        import pandas as pd
        df = pd.DataFrame(table_data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.TextColumn("Rank", width="small"),
                "Provider": st.column_config.TextColumn("Provider", width="small"),
                "Service": st.column_config.TextColumn("Service", width="medium"),
                "Category": st.column_config.TextColumn("Category", width="small"),
                "Score": st.column_config.TextColumn("Score", width="small"),
                "Specs": st.column_config.TextColumn("Specs", width="medium"),
                "Pricing": st.column_config.TextColumn("Pricing", width="medium"),
                "Region": st.column_config.TextColumn("Region", width="small"),
            }
        )

        # Option to view details of any additional recommendation
        st.markdown("---")
        st.markdown("**View detailed information:**")

        selected_rank = st.selectbox(
            "Select a recommendation to view details",
            options=[f"#{rec.rank} - {rec.service_name} ({rec.provider.upper()})" for rec in additional_recs],
            key=f"additional_rec_selector_history_{msg_idx}"
        )

        if selected_rank:
            # Find the selected recommendation
            selected_idx = int(selected_rank.split("#")[1].split(" -")[0]) - 1
            selected_rec = recommendations[selected_idx]

            st.markdown(f"### {get_provider_icon(selected_rec.provider)} {selected_rec.service_name}")

            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:
                st.markdown(f"**Provider:** {selected_rec.provider.upper()}")
                st.markdown(f"**Category:** {selected_rec.category}")
                st.markdown(f"**Region:** {selected_rec.region}")
                st.markdown(f"**Relevance Score:** {selected_rec.relevance_score:.1f}/10")
                st.markdown(f"**Final Score:** {selected_rec.final_score:.4f}")

            with detail_col2:
                st.markdown(f"**Specs:** {selected_rec.specs_summary}")
                st.markdown(f"**Pricing:** {selected_rec.pricing_summary}")

            st.markdown(f"**Description:** {selected_rec.description}")

            if selected_rec.key_features:
                st.markdown(f"**Features:** {', '.join(selected_rec.key_features)}")

            if selected_rec.matches:
                st.success(f"✓ Matches: {' | '.join(selected_rec.matches)}")

            if selected_rec.concerns:
                st.warning(f"⚠ Concerns: {' | '.join(selected_rec.concerns)}")

            st.code(f"Service ID: {selected_rec.service_id}")


def create_config_from_session() -> PipelineConfig:
    """Create PipelineConfig from session state"""
    config = PipelineConfig()

    # Ollama settings
    config.ollama.host = st.session_state.get('ollama_host', 'http://localhost:11434')
    config.ollama.chat_model = st.session_state.get('chat_model', 'gemma3:4b')
    config.ollama.embedding_model = st.session_state.get('embedding_model', 'embeddinggemma:300m')

    # Qdrant settings
    if st.session_state.get('use_qdrant_cloud', False):
        config.qdrant.url = st.session_state.get('qdrant_url', '') or None
        config.qdrant.api_key = st.session_state.get('qdrant_api_key', '') or None
        config.qdrant.host = None
        config.qdrant.port = None
    else:
        config.qdrant.url = None
        config.qdrant.api_key = None
        config.qdrant.host = st.session_state.get('qdrant_host', 'localhost')
        config.qdrant.port = st.session_state.get('qdrant_port', 6333)

    config.qdrant.collection_name = st.session_state.get('collection_name', 'cloud_services')

    # Retrieval settings
    config.retrieval.dense_top_k = st.session_state.get('dense_top_k', 30)
    config.retrieval.sparse_top_k = st.session_state.get('sparse_top_k', 30)
    config.retrieval.fusion_top_k = st.session_state.get('fusion_top_k', 25)

    # Reranking settings
    config.reranking.max_candidates = st.session_state.get('max_rerank_candidates', 20)

    # Output settings
    config.top_k_results = st.session_state.get('top_k', 5)

    return config


def initialize_pipeline() -> Optional[dict]:
    """Initialize all pipeline components"""
    config = create_config_from_session()

    progress_container = st.empty()
    status_container = st.empty()

    steps = [
        ("Connecting to LLM (Ollama)...", "llm"),
        ("Connecting to embedding model...", "embedder"),
        ("Initializing query processor...", "query_processor"),
        ("Building retriever and BM25 index...", "retriever"),
        ("Initializing reranker...", "reranker"),
        ("Initializing scorer...", "scorer"),
    ]

    components = {}

    progress_bar = progress_container.progress(0)

    for i, (step_text, step_key) in enumerate(steps):
        status_container.info(f"🔄 {step_text}")
        progress_bar.progress((i) / len(steps))

        try:
            if step_key == "llm":
                components['llm_client'] = LLMClient(
                    host=config.ollama.host,
                    model=config.ollama.chat_model,
                    temperature=config.ollama.temperature
                )

            elif step_key == "embedder":
                components['embedder'] = EmbeddingClient(
                    host=config.ollama.host,
                    model=config.ollama.embedding_model
                )

            elif step_key == "query_processor":
                components['query_processor'] = QueryProcessor(config)

            elif step_key == "retriever":
                components['retriever'] = HybridRetriever(config)

            elif step_key == "reranker":
                components['reranker'] = LLMReranker(config)

            elif step_key == "scorer":
                components['scorer'] = MultiDimensionalScorer(config)

            time.sleep(0.2)  # Brief pause for visual feedback

        except Exception as e:
            progress_container.empty()
            status_container.error(f"❌ Failed at: {step_text}\n\nError: {str(e)}")
            return None

    progress_bar.progress(1.0)
    status_container.success("✅ Pipeline initialized successfully!")
    time.sleep(1)

    progress_container.empty()
    status_container.empty()

    components['config'] = config
    return components


def process_query(query: str, pipeline: dict, top_k: int = 5) -> Dict[str, Any]:
    """Process a user query through the full pipeline"""
    results = {
        'stages': {},
        'recommendations': [],
        'summary': '',
        'timing': {}
    }

    # Stage 1: Query Understanding
    stage1_start = time.time()
    with st.status("**Stage 1:** Query Understanding", expanded=False) as status:
        st.write("Extracting requirements from query...")

        requirements = pipeline['query_processor'].process(query)

        st.write("**Extracted Requirements:**")
        req_dict = requirements.to_dict()
        relevant_reqs = {k: v for k, v in req_dict.items()
                         if v and k not in ['raw_query', 'expanded_query']}
        st.json(relevant_reqs)

        st.write("**Expanded Query:**")
        expanded = requirements.expanded_query
        st.code(expanded[:300] + "..." if len(expanded) > 300 else expanded)

        status.update(label="✅ Stage 1: Query Understanding Complete", state="complete")

    results['stages']['query_understanding'] = {
        'requirements': requirements.to_dict(),
        'expanded_query': requirements.expanded_query
    }
    results['timing']['stage1'] = time.time() - stage1_start

    # Stage 2: Hybrid Retrieval
    stage2_start = time.time()
    with st.status("**Stage 2:** Hybrid Retrieval", expanded=False) as status:
        st.write("Performing hybrid search (dense + sparse)...")

        candidates = pipeline['retriever'].retrieve(requirements)

        st.write(f"**Retrieved:** {len(candidates)} candidates after fusion")

        if candidates:
            st.write("**Top Retrieved Candidates:**")
            for i, c in enumerate(candidates[:5], 1):
                st.write(f"{i}. {c.service_name} ({c.provider}) - Fusion: {c.fusion_score:.4f}")

        status.update(label=f"✅ Stage 2: Retrieved {len(candidates)} candidates", state="complete")

    results['stages']['retrieval'] = {
        'candidate_count': len(candidates),
        'top_candidates': [{'name': c.service_name, 'provider': c.provider, 'score': c.fusion_score}
                           for c in candidates[:10]]
    }
    results['timing']['stage2'] = time.time() - stage2_start

    if not candidates:
        st.error("No candidates found. Try broadening your search criteria.")
        return results

    # Stage 3: LLM Reranking
    stage3_start = time.time()
    with st.status("**Stage 3:** LLM Reranking", expanded=False) as status:
        st.write(f"Reranking {len(candidates)} candidates with pairwise comparisons...")

        scored_candidates = pipeline['reranker'].rerank(requirements, candidates)

        st.write("**Reranked Order:**")
        for i, s in enumerate(scored_candidates[:5], 1):
            st.write(f"{i}. {s.candidate.service_name} ({s.candidate.provider}) - Score: {s.llm_relevance_score:.1f}/10")

        status.update(label=f"✅ Stage 3: Reranked {len(scored_candidates)} candidates", state="complete")

    results['stages']['reranking'] = {
        'reranked_count': len(scored_candidates),
        'top_reranked': [{'name': s.candidate.service_name, 'provider': s.candidate.provider,
                          'score': s.llm_relevance_score}
                         for s in scored_candidates[:10]]
    }
    results['timing']['stage3'] = time.time() - stage3_start

    if not scored_candidates:
        st.error("No candidates passed reranking.")
        return results

    # Stage 4: Multi-dimensional Scoring
    stage4_start = time.time()
    with st.status("**Stage 4:** Multi-dimensional Scoring", expanded=False) as status:
        st.write("Computing feature-based scores and final ranking...")

        all_recommendations = pipeline['scorer'].score_and_rank(requirements, scored_candidates)
        # Keep all recommendations but note how many are "top" results
        recommendations = all_recommendations

        st.write("**Final Ranking (Top 5):**")
        for rec in recommendations[:5]:
            st.write(f"#{rec.rank}: {rec.service_name} ({rec.provider}) - Final: {rec.final_score:.4f}")

        if len(recommendations) > 5:
            st.write(f"*...and {len(recommendations) - 5} more candidates*")

        status.update(label=f"✅ Stage 4: Generated {len(recommendations)} recommendations", state="complete")

    results['stages']['scoring'] = {
        'recommendations_count': len(recommendations),
        'final_ranking': [{'rank': r.rank, 'name': r.service_name, 'provider': r.provider,
                           'final_score': r.final_score}
                          for r in recommendations]
    }
    results['timing']['stage4'] = time.time() - stage4_start
    results['recommendations'] = recommendations

    # Generate summary
    with st.status("Generating summary...", expanded=False) as status:
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

        summary = pipeline['llm_client'].generate(prompt, system_prompt=SUMMARY_SYSTEM, max_tokens=500)

        if not summary and recommendations:
            top = recommendations[0]
            summary = (
                f"Based on your requirements, the top recommendation is {top.service_name} "
                f"from {top.provider.upper()}. {top.explanation}"
            )

        results['summary'] = summary
        status.update(label="✅ Summary generated", state="complete")

    return results


# ==============================================================================
# Welcome/Configuration Screen
# ==============================================================================

def render_welcome_screen():
    """Render the welcome/configuration screen"""

    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1>☁️ Multi-Cloud Service Recommender</h1>
        <p style="font-size: 1.2rem; color: #666;">
            Intelligent cloud service recommendations across <strong>AWS</strong>, <strong>GCP</strong>, and <strong>Azure</strong><br>
            using LLM-enhanced retrieval and ranking
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Configuration sections in columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🤖 Ollama Configuration")

        st.text_input(
            "Ollama Host URL",
            value=st.session_state.get('ollama_host', 'http://localhost:11434'),
            key='ollama_host',
            help="The URL where Ollama is running"
        )

        st.text_input(
            "Chat Model",
            value=st.session_state.get('chat_model', 'gemma3:4b'),
            key='chat_model',
            help="Model for chat/reasoning (e.g., gemma3:4b, llama3:8b)"
        )

        st.text_input(
            "Embedding Model",
            value=st.session_state.get('embedding_model', 'embeddinggemma:300m'),
            key='embedding_model',
            help="Model for generating embeddings"
        )

    with col2:
        st.subheader("🗄️ Qdrant Configuration")

        use_cloud = st.checkbox(
            "Use Qdrant Cloud",
            value=st.session_state.get('use_qdrant_cloud', False),
            key='use_qdrant_cloud',
            help="Check this if using Qdrant Cloud instead of local instance"
        )

        if use_cloud:
            st.text_input(
                "Qdrant Cloud URL",
                value=st.session_state.get('qdrant_url', ''),
                key='qdrant_url',
                placeholder="https://your-cluster.qdrant.io",
                help="Your Qdrant Cloud cluster URL"
            )

            st.text_input(
                "Qdrant API Key",
                value=st.session_state.get('qdrant_api_key', ''),
                key='qdrant_api_key',
                type='password',
                help="API key for Qdrant Cloud authentication"
            )
        else:
            st.text_input(
                "Qdrant Host",
                value=st.session_state.get('qdrant_host', 'localhost'),
                key='qdrant_host',
                help="Host where Qdrant is running"
            )

            st.number_input(
                "Qdrant Port",
                value=st.session_state.get('qdrant_port', 6333),
                min_value=1,
                max_value=65535,
                key='qdrant_port',
                help="Port where Qdrant is listening"
            )

        st.text_input(
            "Collection Name",
            value=st.session_state.get('collection_name', 'cloud_services'),
            key='collection_name',
            help="Name of the Qdrant collection containing cloud services"
        )

    st.divider()

    # Advanced settings in expander
    with st.expander("⚙️ Advanced Pipeline Settings"):
        adv_col1, adv_col2, adv_col3 = st.columns(3)

        with adv_col1:
            st.slider(
                "Top-K Results",
                min_value=1,
                max_value=20,
                value=st.session_state.get('top_k', 25),
                key='top_k',
                help="Number of final recommendations to show"
            )

            st.slider(
                "Dense Search Top-K",
                min_value=10,
                max_value=100,
                value=st.session_state.get('dense_top_k', 30),
                key='dense_top_k',
                help="Number of candidates from dense retrieval"
            )

        with adv_col2:
            st.slider(
                "Sparse Search Top-K",
                min_value=10,
                max_value=100,
                value=st.session_state.get('sparse_top_k', 30),
                key='sparse_top_k',
                help="Number of candidates from BM25 retrieval"
            )

            st.slider(
                "Fusion Top-K",
                min_value=10,
                max_value=50,
                value=st.session_state.get('fusion_top_k', 25),
                key='fusion_top_k',
                help="Number of candidates after rank fusion"
            )

        with adv_col3:
            st.slider(
                "Max Rerank Candidates",
                min_value=5,
                max_value=50,
                value=st.session_state.get('max_rerank_candidates', 20),
                key='max_rerank_candidates',
                help="Maximum candidates for LLM reranking"
            )

    st.divider()

    # Initialize button
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        if st.button("🚀 Initialize Pipeline & Start", type="primary", use_container_width=True):
            # Validate inputs
            valid = True

            if st.session_state.get('use_qdrant_cloud', False):
                if not st.session_state.get('qdrant_url'):
                    st.error("Please enter the Qdrant Cloud URL")
                    valid = False
                if not st.session_state.get('qdrant_api_key'):
                    st.error("Please enter the Qdrant API Key")
                    valid = False

            if not st.session_state.get('ollama_host'):
                st.error("Please enter the Ollama host URL")
                valid = False

            if valid:
                st.session_state['initializing'] = True
                st.rerun()

    # Show initialization progress if triggered
    if st.session_state.get('initializing', False):
        st.divider()
        st.subheader("🔄 Initializing Pipeline...")

        pipeline = initialize_pipeline()

        if pipeline:
            st.session_state['pipeline'] = pipeline
            st.session_state['initialized'] = True
            st.session_state['initializing'] = False
            st.rerun()
        else:
            st.session_state['initializing'] = False
            st.error("Pipeline initialization failed. Please check your configuration and try again.")


# ==============================================================================
# Chatbot Screen
# ==============================================================================

def render_chatbot_screen():
    """Render the chatbot interface"""

    # Compact header with reset button
    header_col1, header_col2 = st.columns([4, 1])

    with header_col1:
        st.title("☁️ Cloud Service Recommender")

    with header_col2:
        if st.button("🔄 Reset", help="Go back to configuration"):
            # Clear pipeline and reset state
            if 'pipeline' in st.session_state:
                del st.session_state['pipeline']
            st.session_state['initialized'] = False
            st.session_state['messages'] = []
            st.rerun()

    st.caption("Ask me about your cloud infrastructure needs across AWS, GCP, and Azure")

    st.divider()

    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    # Display chat history
    for msg_idx, message in enumerate(st.session_state['messages']):
        with st.chat_message(message['role']):
            if message['role'] == 'user':
                st.markdown(message['content'])
            else:
                if 'summary' in message:
                    st.markdown(message['summary'])

                if 'recommendations' in message and message['recommendations']:
                    st.subheader("📋 Top 5 Recommendations")
                    # Show top 5 as cards
                    for rec in message['recommendations'][:5]:
                        render_recommendation_card(rec)

                    # Show additional recommendations in expandable table
                    if len(message['recommendations']) > 5:
                        render_additional_recommendations_table_history(
                            message['recommendations'],
                            msg_idx
                        )

                if 'stages' in message:
                    with st.expander("🔍 View Pipeline Details"):
                        st.json(message['stages'])

    # Example queries for new users
    if not st.session_state['messages']:
        st.markdown("### 💡 Try an example query:")

        examples = {
            "🗄️ Database": "I need a managed PostgreSQL database for a web application with 10,000 daily users and budget under $100/month",
            "⚡ Serverless": "Looking for serverless compute for image processing, expecting 1000 requests per second",
            "🐳 Kubernetes": "Need a Kubernetes cluster for microservices deployment with auto-scaling",
            "💾 Storage": "I need object storage for a data lake, around 10TB of data, infrequent access"
        }

        cols = st.columns(4)
        for i, (label, query) in enumerate(examples.items()):
            with cols[i]:
                if st.button(label, use_container_width=True, key=f"example_{i}"):
                    st.session_state['pending_query'] = query
                    st.rerun()

    # Handle pending query from example buttons
    if 'pending_query' in st.session_state:
        query = st.session_state['pending_query']
        del st.session_state['pending_query']

        st.session_state['messages'].append({'role': 'user', 'content': query})

        with st.chat_message('user'):
            st.markdown(query)

        with st.chat_message('assistant'):
            results = process_query(
                query,
                st.session_state['pipeline'],
                top_k=st.session_state.get('top_k', 5)
            )

            if results['recommendations']:
                st.markdown(results['summary'])
                st.subheader("📋 Top 5 Recommendations")

                # Show top 5 as cards
                for rec in results['recommendations'][:5]:
                    render_recommendation_card(rec)

                # Show additional recommendations in expandable table
                render_additional_recommendations_table(results['recommendations'])

                total_time = sum(results['timing'].values())
                st.caption(f"⏱️ Total processing time: {total_time:.2f}s | Total candidates: {len(results['recommendations'])}")

            st.session_state['messages'].append({
                'role': 'assistant',
                'summary': results['summary'],
                'recommendations': results['recommendations'],
                'stages': results['stages']
            })

    # Chat input
    if query := st.chat_input("Describe your cloud infrastructure needs..."):
        st.session_state['messages'].append({'role': 'user', 'content': query})

        with st.chat_message('user'):
            st.markdown(query)

        with st.chat_message('assistant'):
            results = process_query(
                query,
                st.session_state['pipeline'],
                top_k=st.session_state.get('top_k', 5)
            )

            if results['recommendations']:
                st.markdown(results['summary'])
                st.subheader("📋 Top 5 Recommendations")

                # Show top 5 as cards
                for rec in results['recommendations'][:5]:
                    render_recommendation_card(rec)

                # Show additional recommendations in expandable table
                render_additional_recommendations_table(results['recommendations'])

                total_time = sum(results['timing'].values())
                st.caption(f"⏱️ Total processing time: {total_time:.2f}s | Total candidates: {len(results['recommendations'])}")

            st.session_state['messages'].append({
                'role': 'assistant',
                'summary': results['summary'],
                'recommendations': results['recommendations'],
                'stages': results['stages']
            })

    # Clear chat button at bottom
    if st.session_state['messages']:
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state['messages'] = []
                st.rerun()


# ==============================================================================
# Main Application
# ==============================================================================

def main():
    """Main Streamlit application"""

    # Check if imports are available
    if not IMPORTS_AVAILABLE:
        st.error(f"""
        ❌ **Import Error**
        
        Could not import required modules. Please ensure the `query_processing` directory 
        is in the correct location relative to this script.
        
        Error: `{IMPORT_ERROR}`
        
        **Expected structure:**
        ```
        your_project/
        ├── streamlit_app.py  (this file)
        └── query_processing/
            ├── __init__.py
            ├── config.py
            ├── models.py
            ├── query_processor.py
            ├── retriever.py
            ├── reranker.py
            ├── scorer.py
            ├── llm_client.py
            └── prompts.py
        ```
        """)
        return

    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state['initialized'] = False

    if 'initializing' not in st.session_state:
        st.session_state['initializing'] = False

    # Route to appropriate screen
    if st.session_state.get('initialized', False) and 'pipeline' in st.session_state:
        render_chatbot_screen()
    else:
        render_welcome_screen()


if __name__ == "__main__":
    main()