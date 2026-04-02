"""
Simple Strands Agent with DuckDuckGo, optional Context7 MCP, and Braintrust observability.

Demonstrates:
- DuckDuckGo web search
- Optional MCP tools (Context7 documentation) when reachable
- Braintrust + OpenTelemetry via StrandsTelemetry
- Anthropic Claude Haiku via Strands
"""

import asyncio
import json
import logging
import os
from typing import Any, List, Optional

from braintrust.otel import BraintrustSpanProcessor
from ddgs import DDGS
from dotenv import load_dotenv
from opentelemetry.sdk.trace import TracerProvider
from strands import Agent
from strands.telemetry import StrandsTelemetry
from strands.tools.decorator import tool


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()


def _get_env_var(key: str, default: Optional[str] = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} not set")
    return value


@tool
def duckduckgo_search(query: str, max_results: int = 5) -> str:
    """
    Search DuckDuckGo for the given query. Use for current events, news, and web lookup.

    Args:
        query: Search query
        max_results: Max results to return

    Returns:
        JSON string of results
    """
    try:
        logger.info("Searching DuckDuckGo for: %s", query)
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        logger.info("Found %s results", len(results))
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error("DuckDuckGo search failed: %s", e)
        return json.dumps({"error": str(e)})


def _load_mcp_tools() -> List[Any]:
    """Load Context7 MCP tools when enabled and connection succeeds."""
    if os.getenv("DISABLE_MCP", "").strip().lower() in ("1", "true", "yes"):
        logger.info("DISABLE_MCP set; skipping MCP tools")
        return []
    try:
        from mcp.client.streamable_http import streamablehttp_client
        from strands.tools.mcp import MCPClient

        url = os.getenv("MCP_CONTEXT7_URL", "https://mcp.context7.com/mcp")

        def create_transport():
            return streamablehttp_client(url)

        with MCPClient(create_transport) as client:
            tools = client.list_tools_sync()
        logger.info("Loaded %d MCP tool(s) from %s", len(tools), url)
        return list(tools)
    except Exception as e:
        logger.warning("MCP tools unavailable (%s); DuckDuckGo only", e)
        return []


def _setup_observability() -> TracerProvider:
    logger.info("Setting up Braintrust observability")
    braintrust_api_key = _get_env_var("BRAINTRUST_API_KEY")
    braintrust_project = _get_env_var("BRAINTRUST_PROJECT")

    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(
        BraintrustSpanProcessor(
            api_key=braintrust_api_key,
            parent=braintrust_project,
        )
    )
    from opentelemetry import trace

    trace.set_tracer_provider(tracer_provider)
    logger.info("Braintrust observability configured for project: %s", braintrust_project)
    return tracer_provider


def _create_agent() -> Agent:
    logger.info("Creating Strands agent")
    tracer_provider = _setup_observability()
    StrandsTelemetry(tracer_provider=tracer_provider)

    anthropic_api_key = _get_env_var("ANTHROPIC_API_KEY")
    os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key

    mcp_tools = _load_mcp_tools()
    all_tools: List[Any] = [duckduckgo_search] + mcp_tools

    if mcp_tools:
        system_prompt = """You are a helpful assistant with:
1. DuckDuckGo web search — use for news, current events, and general web lookup.
2. Context7 documentation tools — use when the user asks how to use a library, API, or framework (e.g. FastAPI, React, Strands).

Pick the best tool for each question. Cite sources when using search results."""
    else:
        system_prompt = """You are a helpful AI assistant with access to DuckDuckGo web search.

Use DuckDuckGo for current information, news, and answers that need the web.
Cite sources when using search results."""

    from strands.models import AnthropicModel

    model = AnthropicModel(
        model_id="claude-3-haiku-20240307",
        max_tokens=4096,
    )

    agent = Agent(
        system_prompt=system_prompt,
        model=model,
        tools=all_tools,
    )
    logger.info(
        "Agent ready with %d tool(s) (DuckDuckGo + %d MCP)",
        len(all_tools),
        len(mcp_tools),
    )
    return agent


async def _run_agent_async(agent: Agent, user_input: str) -> str:
    logger.info("Processing user input: %s", user_input[:120])
    response = await agent.invoke_async(user_input)
    logger.info("Agent response generated")
    return response


def _run_batch_demo(agent: Agent) -> None:
    """Non-interactive run: three web-search-style questions (Lab Problem 1)."""
    queries = [
        "What is the latest news about artificial intelligence?",
        "Who won the 2024 Nobel Prize in Physics?",
        "What are the current trends in machine learning?",
    ]
    print("\nOBSERVABILITY_BATCH=1 — running fixed queries for Braintrust traces.\n")
    for q in queries:
        print("You:", q)
        try:
            out = asyncio.run(_run_agent_async(agent, q))
            print("Agent:", out[:2000], "\n" if len(out) <= 2000 else "…\n")
        except Exception as e:
            logger.exception("Batch query failed")
            print("Error:", e, "\n")
    print("Done. Open Braintrust → Logs to view traces and metrics.")


def _run_mcp_smoke(agent: Agent) -> None:
    """Optional quick MCP exercise (Lab Problem 2): one doc-style question."""
    q = (
        "Using the documentation tools if available, give a short tip on FastAPI async "
        "path operations; otherwise say MCP tools are not loaded."
    )
    print("You:", q)
    out = asyncio.run(_run_agent_async(agent, q))
    print("Agent:", out[:3000], "\n")


def main() -> None:
    logger.info("Starting Simple Agent with Observability")
    agent = _create_agent()

    if os.getenv("OBSERVABILITY_BATCH", "").strip() == "1":
        _run_batch_demo(agent)
        if os.getenv("MCP_SMOKE", "").strip() == "1":
            _run_mcp_smoke(agent)
        return

    if os.getenv("MCP_SMOKE_ONLY", "").strip() == "1":
        _run_mcp_smoke(agent)
        return

    print("\n" + "=" * 80)
    print("Simple Agent with Observability")
    print("=" * 80 + "\n")
    print("Ask anything. I can search the web (and use Context7 docs when MCP is on).")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                print("\nGoodbye!")
                break
            if not user_input:
                continue
            response = asyncio.run(_run_agent_async(agent, user_input))
            print(f"\nAgent: {response}\n")
        except EOFError:
            print("\n\nGoodbye!")
            break
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error("Error running agent: %s", e)
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
