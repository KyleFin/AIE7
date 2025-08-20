"""A minimal tool-using agent graph.

The graph:
- Calls a chat model to determine if tools are needed
- Routes to appropriate tools based on question analysis
- Generates final response with tool results
"""
from __future__ import annotations

import re
from typing import Dict, Any, List

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.state import AgentState
from app.models import get_chat_model
from app.tools import get_tool_belt


def _should_use_rag(question: str) -> bool:
    """Determine if the question is about student loans and should use RAG."""
    rag_keywords = [
        "student loan", "financial aid", "pell grant", "fafsa", "tuition", 
        "scholarship", "education loan", "federal aid", "college funding",
        "direct loan", "subsidized", "unsubsidized", "plus loan",
        "loan forgiveness", "repayment", "interest rate"
    ]
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in rag_keywords)


def _should_use_web_search(question: str) -> bool:
    """Determine if the question needs current web information."""
    web_keywords = [
        "current", "latest", "recent", "today", "news", "update",
        "2024", "2025", "now", "this year"
    ]
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in web_keywords)


def _should_use_arxiv(question: str) -> bool:
    """Determine if the question is academic/research oriented."""
    arxiv_keywords = [
        "research", "paper", "study", "academic", "publication",
        "machine learning", "AI", "artificial intelligence", "neural network",
        "algorithm", "computer science", "mathematics"
    ]
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in arxiv_keywords)


def analyze_question(state: AgentState) -> Dict[str, Any]:
    """Analyze the user's question to determine which tools to use."""
    messages = state["messages"]
    last_human_message = None
    
    # Find the last human message
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_human_message = msg.content
            break
    
    if not last_human_message:
        print("DEBUG: No human message found")
        return {"tool_choice": "direct", "question": ""}
    
    question = last_human_message
    print(f"DEBUG: Analyzing question: '{question}'")
    
    # Determine which tool(s) to use
    tools_to_use = []
    
    if _should_use_rag(question):
        print("DEBUG: Question matches RAG keywords")
        tools_to_use.append("rag")
    elif _should_use_web_search(question):
        print("DEBUG: Question matches web search keywords")
        tools_to_use.append("web_search")
    elif _should_use_arxiv(question):
        print("DEBUG: Question matches ArXiv keywords")
        tools_to_use.append("arxiv")
    
    if not tools_to_use:
        print("DEBUG: No tools matched, using direct response")
        return {"tool_choice": "direct", "question": question}
    
    print(f"DEBUG: Selected tool: {tools_to_use[0]}")
    return {"tool_choice": tools_to_use[0], "question": question}


def use_rag_tool(state: AgentState) -> Dict[str, Any]:
    """Use the RAG tool to get information about student loans."""
    print("DEBUG: RAG tool called!")
    from app.rag import retrieve_information
    
    question = state.get("question", "")
    if not question:
        # Extract question from messages
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                question = msg.content
                break
    
    print(f"DEBUG: RAG tool processing question: '{question}'")
    
    try:
        rag_result = retrieve_information.invoke({"query": question})
        print(f"DEBUG: RAG tool result: {rag_result[:200]}...")
        
        # Add the tool result as a system message
        tool_message = SystemMessage(
            content=f"RAG Tool Result: {rag_result}"
        )
        return {"messages": [tool_message]}
    except Exception as e:
        print(f"DEBUG: RAG tool error: {e}")
        error_message = SystemMessage(
            content=f"RAG tool error: {str(e)}"
        )
        return {"messages": [error_message]}


def use_web_search_tool(state: AgentState) -> Dict[str, Any]:
    """Use the web search tool for current information."""
    print("DEBUG: Web search tool called!")
    from langchain_community.tools.tavily_search import TavilySearchResults
    
    question = state.get("question", "")
    if not question:
        # Extract question from messages
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                question = msg.content
                break
    
    print(f"DEBUG: Web search tool processing question: '{question}'")
    
    try:
        tavily_tool = TavilySearchResults(max_results=3)
        search_result = tavily_tool.invoke({"query": question})
        print(f"DEBUG: Web search tool result: {search_result[:200]}...")
        
        # Format the search results
        formatted_results = "\n".join([
            f"- {result.get('title', 'No title')}: {result.get('content', 'No content')}"
            for result in search_result
        ])
        
        tool_message = SystemMessage(
            content=f"Web Search Results: {formatted_results}"
        )
        return {"messages": [tool_message]}
    except Exception as e:
        print(f"DEBUG: Web search tool error: {e}")
        error_message = SystemMessage(
            content=f"Web search error: {str(e)}"
        )
        return {"messages": [error_message]}


def use_arxiv_tool(state: AgentState) -> Dict[str, Any]:
    """Use the ArXiv search tool for academic papers."""
    print("DEBUG: ArXiv tool called!")
    from langchain_community.tools.arxiv.tool import ArxivQueryRun
    
    question = state.get("question", "")
    if not question:
        # Extract question from messages
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                question = msg.content
                break
    
    print(f"DEBUG: ArXiv tool processing question: '{question}'")
    
    try:
        arxiv_tool = ArxivQueryRun()
        arxiv_result = arxiv_tool.invoke({"query": question})
        print(f"DEBUG: ArXiv tool result: {arxiv_result[:200]}...")
        
        tool_message = SystemMessage(
            content=f"ArXiv Search Results: {arxiv_result}"
        )
        return {"messages": [tool_message]}
    except Exception as e:
        print(f"DEBUG: ArXiv tool error: {e}")
        error_message = SystemMessage(
            content=f"ArXiv search error: {str(e)}"
        )
        return {"messages": [tool_message]}


def generate_response(state: AgentState) -> Dict[str, Any]:
    """Generate final response using the chat model with any tool results."""
    model = get_chat_model()
    messages = state["messages"]
    
    # Add a system message to help the model use tool results if available
    system_prompt = SystemMessage(
        content="You are a helpful assistant. If tool results are provided in the conversation, use them to answer the user's question. If no tool results are available, answer based on your knowledge."
    )
    
    # Prepare messages for the model
    model_messages = [system_prompt] + messages
    
    response = model.invoke(model_messages)
    return {"messages": [response]}


def route_to_tool(state: AgentState):
    """Route to the appropriate tool or direct response."""
    tool_choice = state.get("tool_choice", "direct")
    
    if tool_choice == "rag":
        return "use_rag"
    elif tool_choice == "web_search":
        return "use_web_search"
    elif tool_choice == "arxiv":
        return "use_arxiv"
    else:
        return "generate_response"


def build_graph():
    """Build an agent graph that uses manual tool routing."""
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("analyze_question", analyze_question)
    graph.add_node("use_rag", use_rag_tool)
    graph.add_node("use_web_search", use_web_search_tool)
    graph.add_node("use_arxiv", use_arxiv_tool)
    graph.add_node("generate_response", generate_response)
    
    # Set entry point
    graph.set_entry_point("analyze_question")
    
    # Add conditional routing from analyze_question
    graph.add_conditional_edges(
        "analyze_question",
        route_to_tool,
        {
            "use_rag": "use_rag",
            "use_web_search": "use_web_search", 
            "use_arxiv": "use_arxiv",
            "generate_response": "generate_response"
        }
    )
    
    # All tools route to generate_response
    graph.add_edge("use_rag", "generate_response")
    graph.add_edge("use_web_search", "generate_response")
    graph.add_edge("use_arxiv", "generate_response")
    
    # generate_response ends the graph
    graph.add_edge("generate_response", END)
    
    return graph


# Export compiled graph for LangGraph Platform
graph = build_graph().compile()


