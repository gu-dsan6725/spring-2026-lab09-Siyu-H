# Agent observability — Braintrust analysis

This write-up reflects runs of `simple-agent-observability/agent.py` with OpenTelemetry exported to Braintrust.

## Traces and spans

In the Logs view, each user query shows up as a separate trace. Inside each trace, I can see a clear hierarchy of spans. A typical structure looks like:

- Root span: `invoke_agent`
- Multiple `execute_event_loop_cycle` spans
- LLM chat spans
- Tool spans (DuckDuckGo or MCP)

From the trace details, I can see that the agent operates in a loop:
1. The model generates a response (LLM span)
2. The agent decides whether to call a tool
3. A tool span is executed (e.g., DuckDuckGo or MCP)
4. The model processes the tool output and continues

For example, in one trace, the agent first generates a response, then calls `resolve-library-id`, and then continues with another LLM step. This makes the reasoning process very transparent and easy to follow.

When MCP is enabled, additional spans appear for documentation tools, which makes the trace more detailed compared to runs that only use DuckDuckGo.

## Metrics

Braintrust provides useful metrics such as:

- Total tokens
- Prompt tokens vs completion tokens
- Duration (latency)
- Estimated cost

In one of my runs, I observed:
- ~31,000 total tokens
- ~3.4 seconds latency
- ~$0.049 estimated cost

Queries that involve tool usage (especially DuckDuckGo) tend to have higher token usage and longer latency, because the model needs to process large amounts of external text.

In contrast, MCP-based queries sometimes use fewer tokens since the retrieved documentation is more concise and relevant.

## Observations

From the overview page, I can see multiple traces generated within a short time. Even similar prompts create separate traces, which makes it easy to compare their behavior.

One pattern I noticed is that:
- The agent dynamically decides whether to use DuckDuckGo or MCP tools
- Technical questions tend to trigger MCP tool calls
- General questions tend to trigger DuckDuckGo search

Overall, Braintrust makes it very easy to:
- Understand the agent’s reasoning process
- Identify when and why tools are used
- Compare performance across different runs

The combination of traces, spans, and metrics gives a clear picture of how the agent works internally and how tool usage affects both latency and token consumption.