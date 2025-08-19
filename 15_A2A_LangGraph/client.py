#!/usr/bin/env python3
"""
Simple A2A Client LangGraph Agent

This client can discover remote A2A agents and delegate tasks to them.
It accepts user input from the command line and maintains conversation state.
"""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional
from uuid import uuid4

import httpx
from langchain_openai import ChatOpenAI
from langgraph import StateGraph, END
from langgraph.graph import START
from pydantic import BaseModel, Field

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    TaskState,
)
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClientState(BaseModel):
    """State for the A2A client agent."""
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    discovered_agents: List[AgentCard] = Field(default_factory=list)
    current_agent: Optional[AgentCard] = None
    user_input: str = ""
    response: str = ""
    task_id: Optional[str] = None
    context_id: Optional[str] = None
    is_complete: bool = False
    error: Optional[str] = None


class A2AClientAgent:
    """A2A Client Agent that can discover and delegate to remote agents."""
    
    def __init__(self, base_url: str = "http://localhost:10000"):
        self.base_url = base_url
        self.httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
        self.resolver = A2ACardResolver(
            httpx_client=self.httpx_client,
            base_url=base_url
        )
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=self._get_openai_key()
        )
        
    def _get_openai_key(self) -> str:
        """Get OpenAI API key from environment."""
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return api_key
    
    async def discover_agents(self, state: ClientState) -> ClientState:
        """Discover available A2A agents."""
        try:
            logger.info(f"Discovering agents at {self.base_url}")
            
            # Try to discover agents by attempting to connect to known endpoints
            discovered = []
            
            # Try the main endpoint
            try:
                agent_card = await self.resolver.get_agent_card()
                discovered.append(agent_card)
                logger.info(f"Discovered agent: {agent_card.name}")
            except Exception as e:
                logger.warning(f"Could not discover agent at main endpoint: {e}")
            
            # You could extend this to discover multiple agents
            # For now, we'll work with the discovered agent
            
            state.discovered_agents = discovered
            if discovered:
                state.current_agent = discovered[0]
                logger.info(f"Selected agent: {state.current_agent.name}")
            
        except Exception as e:
            logger.error(f"Error discovering agents: {e}")
            state.error = f"Failed to discover agents: {e}"
        
        return state
    
    async def analyze_user_input(self, state: ClientState) -> ClientState:
        """Analyze user input and determine if delegation is needed."""
        if not state.current_agent:
            state.error = "No agents available for delegation"
            return state
        
        try:
            # Simple analysis - if user input contains specific keywords,
            # we can delegate to the remote agent
            user_input = state.user_input.lower()
            
            # For now, we'll delegate most tasks to the remote agent
            # In a more sophisticated implementation, you could use the LLM
            # to determine the best agent for the task
            
            logger.info(f"Analyzing user input: {state.user_input}")
            logger.info(f"Will delegate to agent: {state.current_agent.name}")
            
        except Exception as e:
            logger.error(f"Error analyzing user input: {e}")
            state.error = f"Failed to analyze input: {e}"
        
        return state
    
    async def delegate_to_remote_agent(self, state: ClientState) -> ClientState:
        """Delegate the task to the remote A2A agent."""
        if not state.current_agent or state.error:
            return state
        
        try:
            logger.info(f"Delegating task to {state.current_agent.name}")
            
            # Create A2A client for the remote agent
            client = A2AClient(
                httpx_client=self.httpx_client,
                agent_card=state.current_agent
            )
            
            # Generate context and task IDs
            state.context_id = str(uuid4())
            state.task_id = str(uuid4())
            
            # Create message parameters
            message_params = MessageSendParams(
                content=state.user_input,
                context_id=state.context_id,
                task_id=state.task_id
            )
            
            # Send message to remote agent
            logger.info("Sending message to remote agent...")
            response = await client.send_message(message_params)
            
            # Process the response
            if response and hasattr(response, 'content'):
                state.response = response.content
                state.is_complete = True
                logger.info("Received response from remote agent")
            else:
                state.error = "No response received from remote agent"
                
        except Exception as e:
            logger.error(f"Error delegating to remote agent: {e}")
            state.error = f"Delegation failed: {e}"
        
        return state
    
    async def format_response(self, state: ClientState) -> ClientState:
        """Format the response for display."""
        if state.error:
            state.response = f"Error: {state.error}"
        elif state.response:
            # Add context about which agent provided the response
            agent_name = state.current_agent.name if state.current_agent else "Unknown"
            state.response = f"Response from {agent_name}:\n\n{state.response}"
        
        return state
    
    async def cleanup(self, state: ClientState) -> ClientState:
        """Clean up resources."""
        try:
            await self.httpx_client.aclose()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
        return state


def build_client_graph() -> StateGraph:
    """Build the LangGraph for the A2A client agent."""
    
    # Create the agent instance
    agent = A2AClientAgent()
    
    # Create the graph
    workflow = StateGraph(ClientState)
    
    # Add nodes
    workflow.add_node("discover_agents", agent.discover_agents)
    workflow.add_node("analyze_input", agent.analyze_user_input)
    workflow.add_node("delegate_task", agent.delegate_to_remote_agent)
    workflow.add_node("format_response", agent.format_response)
    workflow.add_node("cleanup", agent.cleanup)
    
    # Define the flow
    workflow.add_edge(START, "discover_agents")
    workflow.add_edge("discover_agents", "analyze_input")
    workflow.add_edge("analyze_input", "delegate_task")
    workflow.add_edge("delegate_task", "format_response")
    workflow.add_edge("format_response", "cleanup")
    workflow.add_edge("cleanup", END)
    
    return workflow.compile()


async def main():
    """Main function for the A2A client agent."""
    print("🤖 A2A Client Agent")
    print("=" * 50)
    print("This agent can discover remote A2A agents and delegate tasks to them.")
    print("Type 'quit' to exit.")
    print()
    
    # Build the graph
    graph = build_client_graph()
    
    try:
        while True:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🔄 Processing...")
            
            # Create initial state
            initial_state = ClientState(user_input=user_input)
            
            # Run the graph
            try:
                result = await graph.ainvoke(initial_state)
                
                # Display the response
                if result.response:
                    print(f"\n🤖 Agent: {result.response}")
                else:
                    print("\n❌ No response received")
                    
            except Exception as e:
                print(f"\n❌ Error: {e}")
                logger.error(f"Graph execution error: {e}")
                
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Check if OpenAI API key is set
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key and try again.")
        sys.exit(1)
    
    # Run the main function
    asyncio.run(main())
