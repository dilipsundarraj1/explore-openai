- [Responses API and Agents SDK](#responses-api-and-agents-sdk)
- [Agents](#agents)
  - [OpenAI Agent Platform](#openai-agent-platform)
  - [Agents SDK](#agents-sdk)
- [Responses API](#responses-api)

# Responses API and Agents SDK

# Agents

- Agents are system that can independently accomplish tasks on your behalf.
- Agents use an LLM to execute instructions and make decisions.
- They have access to tools to gather context
- Take actions always operating with clearly defined **guardrails**.
  - Guardrails ensusre that the responses are safe and are alined with what you want as a response.


## OpenAI Agent Platform

- The basic idea of OpenAI's agent platform is to provide the library, infrastructure and iterate over the agent logic in order to fulfill what you need.

## Agents SDK

- This is the evolution of the Swarm API.

# Responses API

- New API  designed for agents with built in tools and state management.
- The responses API has built in tools.
  - File Search
  - Web Search
  - Computer user and more
- It still supports tool calling to do whatever you want to do.