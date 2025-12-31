"""Tests for LLM client."""

import os
import pytest
from assertpy import assert_that

from frontend_tester.ai.client import LLMClient
from frontend_tester.core.config import LLMConfig


@pytest.fixture
def llm_config():
    """Create test LLM config."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")

    return LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key=api_key,
        temperature=0.7,
        max_tokens=100,
    )


@pytest.fixture
def llm_client(llm_config):
    """Create LLM client instance."""
    return LLMClient(llm_config)


def test_llm_client_initialization(llm_config):
    """Test LLM client can be initialized."""
    client = LLMClient(llm_config)

    assert_that(client).is_not_none()
    assert_that(client.config).is_equal_to(llm_config)


def test_llm_client_get_model_name(llm_client):
    """Test model name generation."""
    model_name = llm_client.get_model_name()

    # OpenAI models don't need provider prefix
    assert_that(model_name).is_equal_to("gpt-3.5-turbo")


def test_llm_client_anthropic_model_name():
    """Test Anthropic model name generation."""
    config = LLMConfig(
        provider="anthropic",
        model="claude-3-opus-20240229",
    )
    client = LLMClient(config)

    model_name = client.get_model_name()
    assert_that(model_name).is_equal_to("anthropic/claude-3-opus-20240229")


@pytest.mark.asyncio
async def test_llm_client_chat(llm_client):
    """Test async chat completion."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello' and nothing else."},
    ]

    response = await llm_client.chat(messages, temperature=0.1)

    assert_that(response).is_not_none()
    assert_that(response).is_instance_of(str)
    assert_that(len(response)).is_greater_than(0)
    assert_that(response.lower()).contains("hello")


def test_llm_client_chat_sync(llm_client):
    """Test synchronous chat completion."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello' and nothing else."},
    ]

    response = llm_client.chat_sync(messages, temperature=0.1)

    assert_that(response).is_not_none()
    assert_that(response).is_instance_of(str)
    assert_that(len(response)).is_greater_than(0)
    assert_that(response.lower()).contains("hello")


@pytest.mark.asyncio
async def test_llm_client_generate_with_system_prompt(llm_client):
    """Test generation with system and user prompts."""
    system_prompt = "You are a helpful assistant that responds with single words."
    user_prompt = "What is 2+2? Answer with just the number."

    response = await llm_client.generate_with_system_prompt(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.1,
    )

    assert_that(response).is_not_none()
    assert_that(response).is_instance_of(str)
    assert_that(response.strip()).contains("4")


def test_llm_client_generate_with_system_prompt_sync(llm_client):
    """Test synchronous generation with system and user prompts."""
    system_prompt = "You are a helpful assistant that responds with single words."
    user_prompt = "What is 2+2? Answer with just the number."

    response = llm_client.generate_with_system_prompt_sync(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.1,
    )

    assert_that(response).is_not_none()
    assert_that(response).is_instance_of(str)
    assert_that(response.strip()).contains("4")


@pytest.mark.asyncio
async def test_llm_client_with_custom_params(llm_client):
    """Test chat with custom temperature and max_tokens."""
    messages = [
        {"role": "user", "content": "Count from 1 to 10."},
    ]

    # Very low max_tokens to test truncation
    response = await llm_client.chat(
        messages,
        temperature=0.1,
        max_tokens=10
    )

    assert_that(response).is_not_none()
    assert_that(response).is_instance_of(str)
    # Response should be short due to max_tokens limit
    assert_that(len(response)).is_less_than(100)
