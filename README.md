# ☁️ Multi-Cloud Infrastructure Recommender System

An LLM-enhanced retrieval and recommendation system for multi-cloud infrastructure services. This tool accepts natural language descriptions of infrastructure requirements and outputs ranked recommendations for cloud services across **AWS**, **Google Cloud Platform (GCP)**, and **Microsoft Azure**.

> **Course Project:** CSCE 670 - Information Storage and Retrieval  
> **Author:** Divyanshu Singh  
> **Institution:** Texas A&M University

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Algorithm Pipeline Stages](#algorithm-pipeline-stages)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [Technical Stack](#technical-stack)
- [Screenshots](#screenshots)

---

## Overview

This system implements a **4-stage retrieval-augmented LLM pipeline** that helps users find the best cloud services for their infrastructure needs. Users can describe their requirements in natural language (e.g., *"I need a scalable database for a web application with 10,000 daily users and budget under $100/month"*), and the system returns ranked recommendations with explanations across multiple cloud providers.

### What Makes This Different?

| Feature | Traditional Tools | Our System |
|---------|------------------|------------|
| Multi-cloud comparison | ❌ Single provider | ✅ AWS, GCP, Azure |
| Natural language input | ❌ Manual selection | ✅ Conversational queries |
| Explainable recommendations | ❌ Just prices | ✅ LLM-generated reasoning |
| Grounded in real data | ❌ May hallucinate | ✅ Retrieved from actual pricing APIs |
| Hybrid retrieval | ❌ Basic search | ✅ Dense + Sparse + LLM reranking |

---

## Key Features

- **🗣️ Natural Language Interface**: Describe infrastructure needs conversationally
- **🔄 Multi-Cloud Comparison**: Unified recommendations across AWS, GCP, and Azure
- **🤖 LLM-Enhanced Ranking**: Pairwise comparison using academic PRP-Sliding methodology
- **📊 Hybrid Retrieval**: Combines dense vector search with BM25 sparse retrieval
- **💡 Explainable AI**: Natural language justifications for each recommendation
- **📈 Multi-Dimensional Scoring**: Balances relevance, cost efficiency, and capacity matching
- **🎯 320,000+ Data Points**: Comprehensive coverage of cloud services and pricing

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           User Interface (Streamlit)                        │
│                              Chat-based interaction                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        STAGE 1: Query Understanding                         │
│  • LLM extracts structured requirements from natural language               │
│  • Identifies constraints (budget, scale, features)                         │
│  • Generates expanded query with synonyms                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        STAGE 2: Hybrid Retrieval                            │
│  • Dense Retrieval: Vector similarity using embeddings (768-dim)            │
│  • Sparse Retrieval: BM25 keyword matching                                  │
│  • Reciprocal Rank Fusion: Combines both result sets                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        STAGE 3: LLM Reranking                               │
│  • Pairwise comparison with sliding window (PRP-Sliding)                    │
│  • Back-to-first bubblesort for O(k×N) efficiency                           │
│  • k passes guarantee top-k accuracy                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STAGE 4: Multi-Dimensional Scoring                       │
│  • LLM relevance score (50% weight)                                         │
│  • Cost efficiency score (20% weight)                                       │
│  • Capacity match score (20% weight)                                        │
│  • Provider diversity boost (10% weight)                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Final Recommendations                               │
│  • Ranked list with scores and explanations                                 │
│  • Multi-cloud comparison view                                              │
│  • Natural language summary                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Algorithm Pipeline Stages

### Stage 1: Query Understanding (`query_processor.py`)

The query processor uses an LLM to analyze user queries and extract structured requirements:

```python
# Example input:
"I need a managed PostgreSQL database for a web app with 10,000 daily users, budget $100/month"

# Extracted requirements:
{
    "service_categories": ["database"],
    "expected_users": 10000,
    "budget_monthly_usd": 100,
    "database_engine": "PostgreSQL",
    "requires_high_availability": false,
    "use_case": "web application"
}
```

**Key Operations:**
- Extracts service categories (compute, database, storage, serverless, etc.)
- Identifies numerical constraints (users, RPS, budget, capacity)
- Detects feature requirements (HA, auto-scaling, encryption)
- Generates expanded query with synonyms and related terms

### Stage 2: Hybrid Retrieval (`retriever.py`)

Combines two complementary retrieval methods:

**Dense Retrieval:**
- Embeds queries and services using 768-dimensional vectors
- Computed via Gemma embedding model through Ollama
- Cosine similarity search in Qdrant vector database

**Sparse Retrieval (BM25):**
- Classical keyword-based matching
- Effective for exact term matches
- Built in-memory from indexed documents

**Fusion:**
```python
# Reciprocal Rank Fusion formula
for each document d:
    fused_score[d] = Σ 1/(k + rank_i(d))  # k=60 by default
```

### Stage 3: LLM Reranking (`reranker.py`)

Implements the **PRP-Sliding** approach from academic research (Qin et al., NAACL 2024):

```
Algorithm: Back-to-First Bubblesort
─────────────────────────────────────
For k passes (guarantees top-k accuracy):
    For i from N-1 down to 1:
        Compare service[i-1] vs service[i]
        If service[i] is more relevant:
            Swap positions
```

**Pairwise Comparison Prompt:**
```
Given a query, which of the following two cloud services is more relevant?

Query: {user_query}

Service A: {service_details_a}
Service B: {service_details_b}

Which service better matches the requirements? Output only "A" or "B".
```

**Efficiency:** O(k×N) API calls instead of O(N²) for full pairwise comparison

### Stage 4: Multi-Dimensional Scoring (`scorer.py`)

Combines multiple signals into a final score:

| Component | Weight | Description |
|-----------|--------|-------------|
| LLM Relevance | 50% | Normalized score from reranking (1-10 scale) |
| Cost Efficiency | 20% | Budget fit with 20% tolerance |
| Capacity Match | 20% | vCPU/memory alignment with requirements |
| Feature Match | 10% | HA, auto-scaling, encryption support |

**Provider Diversity Boost:** Top service from each provider gets 5% bonus to ensure multi-cloud representation

---

## Project Structure

```
multi-cloud-recommender/
│
├── app.py                          # 🚀 Main Streamlit application
│
├── collectors/                     # Data collection scripts
│   ├── aws_services_collector.py   # Fetches AWS service catalog
│   ├── aws_services_prices.py      # Extracts EC2, RDS, Lambda, S3 pricing
│   ├── gcp_services_collector.py   # Fetches GCP service catalog
│   ├── gcp_services_prices.py      # Extracts Compute, Cloud SQL, GKE pricing
│   ├── azure_collector.py          # Fetches Azure service catalog
│   └── azure_services_prices.py    # Azure Retail Prices API
│
├── preprocessing/                  # Data transformation
│   ├── standard_cloud_service.py   # Unified CloudService schema
│   ├── AWS_preprocess.py           # Transforms AWS data to standard format
│   ├── GCP_preprocess.py           # Transforms GCP data to standard format
│   └── Azure_preprocess.py         # Transforms Azure data to standard format
│
├── ingestion/                      # Vector database population
│   ├── embedder.py                 # Generates embeddings via Ollama
│   ├── qdrant_manager.py           # Qdrant collection operations
│   └── ingestion_pipeline.py       # Orchestrates JSON → embeddings → Qdrant
│
├── query_processing/               # Main recommendation pipeline
│   ├── __init__.py
│   ├── config.py                   # Pipeline configuration settings
│   ├── models.py                   # Data models (UserRequirements, Recommendation)
│   ├── prompts.py                  # LLM prompt templates
│   ├── llm_client.py               # Ollama API client
│   ├── query_processor.py          # Stage 1: Query understanding
│   ├── retriever.py                # Stage 2: Hybrid retrieval
│   ├── reranker.py                 # Stage 3: LLM pairwise reranking
│   ├── scorer.py                   # Stage 4: Multi-dimensional scoring
│   └── pipeline.py                 # Orchestrates all stages
│
├── data/                           # Cloud service data
│   ├── AWS/
│   │   ├── aws_standardized_services.json
│   │   └── raw/                    # Raw API responses
│   ├── GCP/
│   │   ├── gcp_standardized_services.json
│   │   └── raw/
│   └── Azure/
│       └── azure_standardized_services.json
│
├── scripts/
│   └── create_qdrant_indexes.py    # Database setup utilities
│
└── README.md
```

---

## Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) for local LLM inference
- [Qdrant](https://qdrant.tech/) vector database (local or cloud)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/multi-cloud-recommender.git
cd multi-cloud-recommender
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key dependencies:**
```
streamlit>=1.28.0
qdrant-client>=1.6.0
requests>=2.31.0
boto3>=1.28.0              # AWS API
google-cloud-billing>=1.11  # GCP API
python-dotenv>=1.0.0
```

### Step 3: Set Up Ollama

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull gemma3:4b              # Chat model
ollama pull embeddinggemma:300m    # Embedding model
```

### Step 4: Set Up Qdrant

**Option A: Local Docker**
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

**Option B: Qdrant Cloud**
- Create account at [cloud.qdrant.io](https://cloud.qdrant.io)
- Note your cluster URL and API key

### Step 5: Ingest Data

```bash
# Ingest AWS services
python ingestion/ingestion_pipeline.py --provider aws --data-dir ./data

# Ingest GCP services
python ingestion/ingestion_pipeline.py --provider gcp --data-dir ./data

# Ingest Azure services (if available)
python ingestion/ingestion_pipeline.py --provider azure --data-dir ./data
```

---

## Configuration

The system can be configured through the Streamlit UI or programmatically:

### Ollama Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ollama_host` | `http://localhost:11434` | Ollama API endpoint |
| `chat_model` | `gemma3:4b` | Model for reasoning |
| `embedding_model` | `embeddinggemma:300m` | Model for embeddings |

### Qdrant Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `qdrant_host` | `localhost` | Host for local instance |
| `qdrant_port` | `6333` | Port for local instance |
| `qdrant_url` | `None` | Full URL for cloud instance |
| `qdrant_api_key` | `None` | API key for authentication |
| `collection_name` | `cloud_services` | Vector collection name |

### Pipeline Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `dense_top_k` | `30` | Candidates from dense retrieval |
| `sparse_top_k` | `30` | Candidates from BM25 |
| `fusion_top_k` | `25` | Candidates after fusion |
| `max_rerank_candidates` | `20` | Max candidates for LLM reranking |
| `top_k_results` | `5` | Final recommendations to show |

---

## Usage

### Running the Streamlit App

```bash
streamlit run app.py
```

This launches the interactive web interface where you can:

1. **Configure** connection settings on the welcome screen
2. **Initialize** the pipeline with a single click
3. **Chat** with the recommender using natural language

### Example Queries

```
🗄️ "I need a managed PostgreSQL database for a web application 
    with 10,000 daily users and budget under $100/month"

⚡ "Looking for serverless compute for image processing, 
    expecting 1000 requests per second"

🐳 "Need a Kubernetes cluster for microservices deployment 
    with auto-scaling and multi-region support"

💾 "I need object storage for a data lake, around 10TB of data, 
    infrequent access"
```

### Command-Line Usage

```bash
# Single query
python query_processing/pipeline.py "I need a database for 10000 users"

# Interactive mode
python query_processing/pipeline.py --interactive

# With custom settings
python query_processing/pipeline.py \
    --qdrant-url "https://your-cluster.qdrant.io" \
    --qdrant-api-key "your-api-key" \
    --chat-model "llama3:8b" \
    --top-k 10 \
    "Your query here"
```

---

## Data Sources

### Dataset Statistics

| Provider | Services | Data Points |
|----------|----------|-------------|
| AWS | EC2, RDS, Lambda, EKS, ECS, S3 | ~132,000 |
| GCP | Compute Engine, Cloud SQL, GKE, Cloud Run, Storage | ~19,000 |
| Azure | VMs, SQL Database, AKS, Functions, Blob Storage | ~171,000 |
| **Total** | **Multiple service types** | **~322,000** |

### Data Collection APIs

- **AWS**: Price List API, EC2/RDS/EKS/Lambda APIs
- **GCP**: Cloud Billing API, Compute Engine API
- **Azure**: Retail Prices API, Resource Manager API

### Standardized Schema

All services are transformed into a unified `CloudService` format:

```python
@dataclass
class CloudService:
    service_id: str        # Unique identifier
    provider: str          # aws, gcp, azure
    service_name: str      # Human-readable name
    service_type: str      # ec2, rds, lambda, etc.
    category: str          # compute, database, storage, etc.
    description: str       # Rich description for embeddings
    specs: TechnicalSpecs  # vCPU, memory, storage, etc.
    pricing: List[PricingInfo]  # Price per unit, currency, model
    features: List[str]    # Key capabilities
    use_cases: List[str]   # Common applications
    # ... and more
```

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **LLM Inference** | Ollama (local deployment) |
| **Chat Model** | Gemma 3 4B |
| **Embeddings** | embeddinggemma (768-dim) |
| **Vector Database** | Qdrant |
| **Sparse Retrieval** | BM25 (in-memory) |
| **Data Collection** | boto3, google-cloud-billing |
| **Language** | Python 3.10+ |

---

## Screenshots

### Welcome/Configuration Screen
Configure Ollama and Qdrant connections before starting the chat.

### Chat Interface
Ask questions in natural language and receive ranked recommendations.

### Recommendation Cards
Each recommendation shows:
- Service name and provider
- Relevance score (1-10)
- Specs and pricing summary
- Matching features (✓) and concerns (⚠)
- Expandable details view

### Pipeline Stage Visualization
View the "thinking" process with expandable sections for each stage:
- Query understanding results
- Retrieved candidates
- Reranking progress
- Final scoring breakdown

---

## References

- Qin, Z. et al. (2024). "Large Language Models are Effective Text Rankers with Pairwise Ranking Prompting." NAACL 2024.
- Robertson, S. & Zaragoza, H. (2009). "The Probabilistic Relevance Framework: BM25 and Beyond."
- Cormack, G. et al. (2009). "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods."

---

## License

This project is developed for academic purposes as part of CSCE 670 at Texas A&M University.

---

## Acknowledgments

- **Course**: CSCE 670 - Information Storage and Retrieval
- **Instructor**: Dr. Yu Zhang
- **Institution**: Texas A&M University

---

<div align="center">
Made with ❤️ for cloud infrastructure enthusiasts
</div>
