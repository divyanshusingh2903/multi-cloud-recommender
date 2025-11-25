"""
LLM Client for Ollama
Handles chat/generation interactions with Ollama models
"""

import requests
import json
from typing import Optional, Dict, Any, List


class LLMClient:
    """Client for interacting with Ollama LLM for chat/generation"""

    def __init__(self, host: str = "http://localhost:11434", model: str = "gemma3:4b", temperature: float = 0.3,
                 timeout: int = 120):
        """
        Initialize the LLM client

        Args:
            host: Ollama API endpoint
            model: Model name for chat/generation
            temperature: Sampling temperature (lower = more deterministic)
            timeout: Request timeout in seconds
        """
        self.host = host
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

        # Test connection
        self._test_connection()

    def _test_connection(self):
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            response.raise_for_status()

            # Check if model is available
            models = response.json().get('models', [])
            model_names = [m.get('name', '').split(':')[0] for m in models]

            if self.model.split(':')[0] not in model_names:
                print(f"  Model '{self.model}' not found. Available: {model_names}")
                print(f"   Run: ollama pull {self.model}")
            else:
                print(f"✅ Connected to Ollama, model '{self.model}' available")

        except Exception as e:
            raise ConnectionError(f"Failed to connect to Ollama at {self.host}: {str(e)}")

    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: Optional[float] = None, max_tokens: int = 2048) -> str:
        """
        Generate a response from the LLM

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens
                }
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            return response.json().get('response', '').strip()

        except requests.exceptions.Timeout:
            print(f"  LLM request timed out after {self.timeout}s")
            return ""
        except Exception as e:
            print(f" LLM generation error: {str(e)}")
            return ""

    def chat(self, messages: List[Dict[str, str]], temperature: Optional[float] = None,
             max_tokens: int = 2048) -> str:
        """
        Chat-style interaction with the LLM

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Assistant's response text
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens
                }
            }

            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            return response.json().get('message', {}).get('content', '').strip()

        except requests.exceptions.Timeout:
            print(f"  LLM chat request timed out after {self.timeout}s")
            return ""
        except Exception as e:
            print(f" LLM chat error: {str(e)}")
            return ""

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None,
                      temperature: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Generate a JSON response from the LLM"""

        json_system = system_prompt or ""
        json_system += "\n\nYou must respond with valid JSON only. No markdown, no explanation, just the JSON object. All numeric values must be actual numbers, not expressions or calculations."

        response = self.generate(prompt, system_prompt=json_system, temperature=temperature or 0.1)

        if not response:
            return None

        try:
            response = response.strip()

            # Remove markdown code blocks
            if response.startswith('```json'):
                response = response[7:]
            elif response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()

            # Fix common LLM issues: evaluate simple arithmetic expressions
            import re

            def eval_expr(match):
                try:
                    expr = match.group(1)  # Get the captured group (the expression)
                    if re.match(r'^[\d\.\+\-\*/\(\)\s]+$', expr):
                        return ': ' + str(eval(expr))
                except:
                    pass
                return match.group(0)

            # Replace arithmetic expressions in numeric contexts
            response = re.sub(r':\s*([\d\.]+\s*[/\*\+\-]\s*[\d\.]+)', eval_expr, response)

            return json.loads(response)

        except json.JSONDecodeError as e:
            print(f"  Failed to parse JSON response: {str(e)}")
            return None

class EmbeddingClient:
    """Client for generating embeddings via Ollama"""

    def __init__(self, host: str = "http://localhost:11434", model: str = "embeddinggemma:300m"):
        """
        Initialize the embedding client

        Args:
            host: Ollama API endpoint
            model: Embedding model name
        """
        self.host = host
        self.model = model
        self.dimension = None

        # Test and get dimension
        self._initialize()

    def _initialize(self):
        """Initialize and detect embedding dimension"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            print(f"✅ Connected to Ollama for embeddings")

            # Get dimension from test embedding
            test_embedding = self.embed("test")
            self.dimension = len(test_embedding)
            print(f"   Embedding dimension: {self.dimension}")

        except Exception as e:
            raise ConnectionError(f"Failed to initialize embedding client: {str(e)}")

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = requests.post(
                f"{self.host}/api/embed",
                json={
                    "model": self.model,
                    "input": text
                },
                timeout=60
            )
            response.raise_for_status()

            return response.json()["embeddings"][0]

        except Exception as e:
            print(f" Embedding error: {str(e)}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return [self.embed(text) for text in texts]

    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension


if __name__ == "__main__":
    # Test the clients
    print("\n" + "="*60)
    print("Testing LLM Client")
    print("="*60)

    llm = LLMClient(model="gemma3:4b")

    # Test generation
    print("\nTesting generation...")
    response = llm.generate("What is cloud computing in one sentence?")
    print(f"Response: {response}")

    # Test JSON generation
    print("\nTesting JSON generation...")
    json_prompt = """Extract the following from this query: "I need a database for 10000 users, budget $100/month"

Return JSON with these fields:
- service_type: string
- user_count: number
- budget_monthly: number"""

    json_response = llm.generate_json(json_prompt)
    print(f"JSON Response: {json_response}")

    # Test embeddings
    print("\n" + "="*60)
    print("Testing Embedding Client")
    print("="*60)

    embedder = EmbeddingClient()
    embedding = embedder.embed("AWS EC2 compute instance")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")