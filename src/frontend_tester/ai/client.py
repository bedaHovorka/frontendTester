"""LiteLLM client wrapper for unified LLM access."""

import os
from typing import Any

import litellm
from litellm import acompletion, completion

from frontend_tester.core.config import LLMConfig


class LLMClient:
    """Unified LLM client using LiteLLM."""

    def __init__(self, config: LLMConfig | None = None):
        """
        Initialize LLM client.

        Args:
            config: LLM configuration. If None, uses environment variables.
        """
        self.config = config or LLMConfig()

        # Set API key in environment if provided
        if self.config.api_key:
            if self.config.provider == "openai":
                os.environ["OPENAI_API_KEY"] = self.config.api_key
            elif self.config.provider == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = self.config.api_key

        # Configure LiteLLM
        litellm.drop_params = True  # Drop unsupported params instead of erroring

    def get_model_name(self) -> str:
        """Get the full model name for LiteLLM."""
        # LiteLLM uses format: provider/model
        if self.config.provider == "openai":
            return self.config.model
        else:
            return f"{self.config.provider}/{self.config.model}"

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Send chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens (overrides config)
            **kwargs: Additional parameters for LiteLLM

        Returns:
            Response content as string
        """
        response = await acompletion(
            model=self.get_model_name(),
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            **kwargs,
        )

        return response.choices[0].message.content

    def chat_sync(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Send chat completion request (synchronous version).

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens (overrides config)
            **kwargs: Additional parameters for LiteLLM

        Returns:
            Response content as string
        """
        response = completion(
            model=self.get_model_name(),
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            **kwargs,
        )

        return response.choices[0].message.content

    async def generate_with_system_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate response with system and user prompts.

        Args:
            system_prompt: System instruction
            user_prompt: User query
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Response content
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        return await self.chat(messages, temperature, max_tokens)

    def generate_with_system_prompt_sync(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate response with system and user prompts (synchronous).

        Args:
            system_prompt: System instruction
            user_prompt: User query
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Response content
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        return self.chat_sync(messages, temperature, max_tokens)
