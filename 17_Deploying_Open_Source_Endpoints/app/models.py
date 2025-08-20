"""Model utilities for constructing chat LLM clients.

Centralizes configuration of the default chat model and temperature so graphs can
import a single helper without repeating provider-specific wiring.
"""
from __future__ import annotations

import os
from typing import Any

# from langchain_openai import ChatOpenAI
from langchain_together import ChatTogether


def get_chat_model(model_name: str | None = None, *, temperature: float = 0) -> Any:
    """Return a configured LangChain ChatOpenAI client.

    - model_name: optional override. If not provided, uses OPENAI_MODEL env var,
      falling back to "gpt-4.1-nano".
    - temperature: sampling temperature for the chat model.

    Returns: a LangChain-compatible chat model instance.
    """
    # name = model_name or os.environ.get("OPENAI_MODEL", "gpt-4.1-nano")
    # return ChatOpenAI(model=name, temperature=temperature)
    name = model_name or "openai/gpt-oss-20b"
    
    model = ChatTogether(
        model=name,
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # other params...
    )
    
    return model


