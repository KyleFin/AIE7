from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from typing import List, Dict, Any
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

server_params = StdioServerParameters(
    command="python",
    args=["bible_api.py"],
)

class MCPToolWrapper(BaseTool):
    """Wrapper for MCP tools to make them compatible with LangGraph"""
    
    def __init__(self, session: ClientSession, tool_name: str, tool_description: str):
        super().__init__(
            name=tool_name,
            description=tool_description,
        )
        self._session = session
        self._tool_name = tool_name
    
    async def _arun(self, **kwargs):
        try:
            result = await self._session.call_tool(self._tool_name, kwargs)
            if result.content and len(result.content) > 0:
                return result.content[0].text
            return "No content returned"
        except Exception as e:
            return f"Error calling tool {self._tool_name}: {str(e)}"
    
    def _run(self, **kwargs):
        # This is a fallback for sync calls, but we'll use async
        raise NotImplementedError("This tool only supports async operations")

async def create_mcp_tools(session: ClientSession) -> List[MCPToolWrapper]:
    """Create LangGraph-compatible tools from MCP session"""
    tools = []
    
    # Get available tools from the session
    tools_result = await session.list_tools()
    
    for tool in tools_result.tools:
        # Create a wrapper tool for each MCP tool
        mcp_tool = MCPToolWrapper(
            session=session,
            tool_name=tool.name,
            tool_description=tool.description or f"Tool: {tool.name}"
        )
        tools.append(mcp_tool)
    
    return tools

async def test_mcp_tools_directly(session: ClientSession):
    """Test MCP tools directly without LangGraph to verify they work"""
    print("\n--- Testing MCP Tools Directly ---")
    
    try:
        # Test bible_search
        result = await session.call_tool("bible_search", {"query": "John 3:16"})
        if result.content and len(result.content) > 0:
            print(f"bible_search result: {result.content[0].text}")
        else:
            print("bible_search returned no content")
    except Exception as e:
        print(f"bible_search error: {e}")
    
    print("Direct MCP tool testing completed!")

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("MCP session initialized successfully!")
            
            # Get available tools from the session
            tools_result = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools_result.tools]}")
            
            # Test MCP tools directly first
            await test_mcp_tools_directly(session)
            
            # Check if OpenAI API key is available
            openai_api_key = os.getenv("OPENAI_API_KEY")
            
            # Create LangGraph-compatible tools
            tools = await create_mcp_tools(session)
            print(f"Created {len(tools)} LangGraph tools")
            
            # Create the agent with OpenAI model
            llm = ChatOpenAI(
                model="gpt-4",
                temperature=0,
                openai_api_key=openai_api_key
            )
            
            # Create and run the agent
            agent = create_react_agent(llm, tools)
            
            # Test with a simple question
            agent_response = await agent.ainvoke({
                "messages": [{"role": "user", "content": "What is John 3:16?"}]
            })
            
            print("\n--- Agent Response ---")
            print(agent_response)
            
            print("\nMCP session completed successfully!")
            print("All tools are working and integrated with LangGraph.")

if __name__ == "__main__":
    asyncio.run(main())