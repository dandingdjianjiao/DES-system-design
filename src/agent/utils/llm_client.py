"""
LLM Client using OpenAI-compatible API

Supports:
- OpenAI API
- DashScope (Aliyun) OpenAI-compatible endpoint
- Any OpenAI-compatible service
"""

import os
import logging
from typing import Optional, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Universal LLM client using OpenAI-compatible API.

    Supports multiple providers:
    - OpenAI (api.openai.com)
    - DashScope/Aliyun (dashscope.aliyuncs.com/compatible-mode/v1)
    - Custom OpenAI-compatible endpoints

    Attributes:
        client: OpenAI client instance
        model: Model name
        temperature: Sampling temperature
        max_tokens: Maximum completion tokens
    """

    def __init__(
        self,
        provider: str = "dashscope",
        model: str = "qwen-plus",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize LLM client.

        Args:
            provider: "openai", "dashscope", or "custom"
            model: Model name (e.g., "gpt-4o-mini", "qwen-plus")
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            api_key: API key (if None, read from env)
            base_url: Custom base URL (for custom providers)
        """
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Determine API key and base URL
        if provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.base_url = base_url or "https://api.openai.com/v1"

        elif provider == "dashscope":
            self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
            self.base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"

        else:  # custom
            self.api_key = api_key or os.getenv("LLM_API_KEY")
            if not base_url:
                raise ValueError("base_url is required for custom provider")
            self.base_url = base_url

        if not self.api_key:
            raise ValueError(
                f"API key not found for provider '{provider}'. "
                f"Set {provider.upper()}_API_KEY in environment or .env file."
            )

        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        logger.info(
            f"Initialized LLM client: provider={provider}, model={model}, "
            f"temperature={temperature}"
        )

    def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a chat completion request.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **kwargs: Additional parameters for API call

        Returns:
            Generated text response
        """
        # Build messages
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Prepare parameters
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            **kwargs
        }

        # Make API call
        try:
            response = self.client.chat.completions.create(**params)
            content = response.choices[0].message.content

            logger.debug(f"LLM response: {content[:100]}...")
            return content

        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise

    def __call__(self, prompt: str, **kwargs) -> str:
        """
        Shorthand for chat() method.

        Args:
            prompt: User prompt
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        return self.chat(prompt, **kwargs)


def create_llm_client_from_config(config: Dict[str, Any]) -> LLMClient:
    """
    Create LLM client from configuration dictionary.

    Args:
        config: Configuration dict with keys:
            - provider: "openai" or "dashscope"
            - model: Model name
            - temperature: Sampling temperature
            - max_tokens: Max tokens
            - api_key (optional): API key
            - base_url (optional): Custom base URL

    Returns:
        Configured LLMClient instance
    """
    return LLMClient(
        provider=config.get("provider", "dashscope"),
        model=config.get("model", "qwen-plus"),
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 2000),
        api_key=config.get("api_key"),
        base_url=config.get("base_url")
    )


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Example 1: DashScope (Aliyun)
    try:
        client = LLMClient(
            provider="dashscope",
            model="qwen-plus",
            temperature=0.7
        )

        response = client.chat(
            prompt="What is Deep Eutectic Solvent?",
            system_prompt="You are a chemistry expert."
        )

        print("Response from DashScope:")
        print(response)

    except Exception as e:
        print(f"Error: {e}")

    # Example 2: OpenAI
    try:
        client = LLMClient(
            provider="openai",
            model="gpt-4o-mini",
            temperature=0.7
        )

        response = client("Explain hydrogen bonding in one sentence.")

        print("\nResponse from OpenAI:")
        print(response)

    except Exception as e:
        print(f"Error: {e}")
