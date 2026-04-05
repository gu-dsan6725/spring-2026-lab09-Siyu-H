# MCP observability (Context7)

![MCP tool in Braintrust](braintrust-mcp-tool.png)

## Setup

The agent loads tools from the Context7 MCP server at `https://mcp.context7.com/mcp`. In my runs, MCP is enabled by default, so the agent can access both documentation tools (such as `resolve-library-id` and `query-docs`) and web search tools like DuckDuckGo. MCP can be disabled by setting `DISABLE_MCP=1`, in which case the agent only uses web search.

## What I see in traces

From the Braintrust traces, I can clearly see additional tool spans when MCP is enabled. Besides the usual LLM chat spans, I observe tool calls such as:

- `resolve-library-id`
- `query-docs`

These appear inside the `execute_event_loop_cycle` spans, alongside the normal reasoning steps of the agent.

For example, in one trace, the agent first performs an LLM step, then calls `resolve-library-id` (which completes very quickly, around 0 seconds), and then continues with another LLM step. This shows that the agent is trying to identify the correct documentation source before retrieving detailed information.

Compared to DuckDuckGo, MCP tool spans are easier to identify because:
- They have more structured inputs (like library identifiers or documentation queries)
- Their outputs are more targeted and concise
- They are clearly labeled as documentation-related tools in the trace

## DuckDuckGo vs MCP

The difference between DuckDuckGo and MCP tools is very noticeable:

- **DuckDuckGo**
  - Used for general or open-ended questions
  - Returns large, unstructured text snippets
  - Often increases token usage because the model processes a lot of content

- **MCP / Context7**
  - Used for documentation-style queries (e.g., “how to use FastAPI async path operations”)
  - Returns more structured and relevant information
  - Tool calls are shorter and more focused
  - Easier to recognize in traces due to tool names like `resolve-library-id`

In my traces, MCP tool calls sometimes complete faster than DuckDuckGo, but latency can vary depending on the server. Overall, MCP feels more efficient for API-related or technical questions.

## Observations

One interesting observation is that when the prompt explicitly asks to use documentation tools (or implies a technical question), the agent tends to call MCP tools first. If MCP is not available or not used, it falls back to DuckDuckGo.

Also, MCP tool usage makes the trace slightly more complex (more spans), but it also makes the agent behavior easier to understand, since each step (library resolution → doc retrieval → answer generation) is clearly separated.