"""Shared agent state definitions for LangGraph graphs."""
from __future__ import annotations

from typing import Annotated, TypedDict, List, Optional

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State schema for agent graphs, storing a message list with add_messages."""
    messages: Annotated[List, add_messages]
    tool_choice: Optional[str]  # Which tool to use: "rag", "web_search", "arxiv", or "direct"
    question: Optional[str]     # Extracted question text


