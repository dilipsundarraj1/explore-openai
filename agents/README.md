# OpenAI Responses API vs Chat Completions Migration Guide

- [OpenAI Responses API vs Chat Completions Migration Guide](#openai-responses-api-vs-chat-completions-migration-guide)
  - [Quick Start](#quick-start)
  - [Responses API Overview](#responses-api-overview)
    - [Key Features](#key-features)
    - [Built-in Tools](#built-in-tools)
  - [Responses API vs Chat Completions API](#responses-api-vs-chat-completions-api)
    - [Architectural Differences](#architectural-differences)
    - [API Comparison](#api-comparison)
      - [Chat Completions API Structure](#chat-completions-api-structure)
      - [Responses API Structure](#responses-api-structure)
    - [Feature Comparison](#feature-comparison)
  - [Migration Guide](#migration-guide)
    - [Phase 1: Assessment and Planning](#phase-1-assessment-and-planning)
    - [Phase 2: Gradual Migration](#phase-2-gradual-migration)
      - [Step 1: Start with New Features](#step-1-start-with-new-features)
      - [Step 2: Create Abstraction Layer](#step-2-create-abstraction-layer)
      - [Step 3: Feature Flags](#step-3-feature-flags)
    - [Phase 3: Testing and Validation](#phase-3-testing-and-validation)
    - [Phase 4: Full Cutover](#phase-4-full-cutover)
  - [Code Examples](#code-examples)
    - [Chat Completions vs Responses API](#chat-completions-vs-responses-api)
      - [Before: Chat Completions with Manual Tool Integration](#before-chat-completions-with-manual-tool-integration)
      - [After: Responses API with Built-in Tools](#after-responses-api-with-built-in-tools)
      - [Conversation Management Comparison](#conversation-management-comparison)
      - [Image Input with Responses API](#image-input-with-responses-api)
  - [Best Practices](#best-practices)
    - [1. Error Handling](#1-error-handling)
    - [2. Response Processing](#2-response-processing)
    - [3. Tool Selection](#3-tool-selection)
    - [4. Performance Optimization](#4-performance-optimization)
  - [Agents and SDK Information](#agents-and-sdk-information)
    - [OpenAI Agent Platform](#openai-agent-platform)
    - [Agents SDK](#agents-sdk)

## Quick Start

For a comprehensive example of the Responses API integration, see [`15_responses_final.py`](src/15_responses_final.py).

## Responses API Overview

The Responses API is OpenAI's new endpoint designed specifically for agent-based applications with built-in tools, state management, and conversation continuity.

### Key Features

- **Built-in Tools**: Web search, file search, and computer use capabilities
- **State Management**: Automatic conversation state tracking
- **Conversation Continuity**: Reference previous responses for multi-turn conversations
- **Simplified Architecture**: Less boilerplate code for complex interactions
- **Agent-First Design**: Optimized for autonomous task completion

### Built-in Tools

- **Web Search**: Real-time web search capabilities
- **File Search**: Search through uploaded documents and files
- **Computer Use**: Direct computer interaction (coming soon)
- **Custom Tools**: Support for custom tool integration

## Responses API vs Chat Completions API

### Architectural Differences

| Aspect                | Chat Completions API             | Responses API                          |
| --------------------- | -------------------------------- | -------------------------------------- |
| **Design Philosophy** | General-purpose chat interface   | Agent-first, task-oriented             |
| **State Management**  | Client-side conversation history | Built-in state tracking                |
| **Tool Integration**  | Manual tool calling setup        | Built-in tools with automatic handling |
| **Conversation Flow** | Manual message threading         | Automatic response chaining            |
| **Error Handling**    | Manual retry logic needed        | Built-in robustness                    |

### API Comparison

#### Chat Completions API Structure
```python
# Chat Completions API
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ],
    tools=[...],  # Manual tool setup
    temperature=0.7
)
```

#### Responses API Structure
```python
# Responses API
response = client.responses.create(
    model="gpt-4o",
    input="Hello, how are you?",
    tools=[{"type": "web_search"}],  # Built-in tools
    previous_response_id="resp_123"  # Automatic conversation threading
)
```

### Feature Comparison

| Feature                   | Chat Completions       | Responses API           | Migration Impact                    |
| ------------------------- | ---------------------- | ----------------------- | ----------------------------------- |
| **Basic Text Generation** | ✅ Full support         | ✅ Full support          | Direct replacement                  |
| **Function Calling**      | ✅ Manual setup         | ✅ Simplified + built-in | Reduce boilerplate                  |
| **Streaming**             | ✅ Supported            | ⏳ Coming soon           | Temporary limitation                |
| **Fine-tuned Models**     | ✅ Full support         | ⚠️ Limited support       | May need hybrid approach            |
| **Custom Parameters**     | ✅ Full control         | ⚠️ Simplified interface  | Some parameters not available       |
| **Web Search**            | ❌ External integration | ✅ Built-in              | Major simplification                |
| **File Search**           | ❌ External integration | ✅ Built-in              | Major simplification                |
| **Conversation State**    | ❌ Manual tracking      | ✅ Automatic             | Significant reduction in complexity |

## Migration Guide

### Phase 1: Assessment and Planning

1. **Inventory Current Usage**
   ```bash
   # Search for chat completions usage
   grep -r "chat.completions.create" your_codebase/
   grep -r "ChatCompletion" your_codebase/
   ```

2. **Categorize Use Cases**
   - Simple Q&A → Direct migration candidate
   - Function calling → Enhanced with built-in tools
   - Streaming applications → Keep chat completions temporarily
   - Fine-tuned models → Hybrid approach needed

3. **Create Migration Priority Matrix**
   - High Priority: New agent-based features
   - Medium Priority: Simple conversational interfaces
   - Low Priority: Streaming-heavy applications

### Phase 2: Gradual Migration

#### Step 1: Start with New Features
```python
# New agent features should use Responses API from the start
def new_research_agent(query):
    return client.responses.create(
        model="gpt-4o",
        input=query,
        tools=[{"type": "web_search"}]
    )
```

#### Step 2: Create Abstraction Layer
```python
class LLMClient:
    def __init__(self, use_responses_api=False):
        self.use_responses_api = use_responses_api
    
    def generate_response(self, prompt, use_tools=False):
        if self.use_responses_api:
            tools = [{"type": "web_search"}] if use_tools else None
            return self.client.responses.create(
                model="gpt-4o",
                input=prompt,
                tools=tools
            )
        else:
            # Fallback to chat completions
            return self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
```

#### Step 3: Feature Flags
```python
# Use feature flags for gradual rollout
RESPONSES_API_ENABLED = os.getenv("USE_RESPONSES_API", "false").lower() == "true"

def get_ai_response(prompt):
    if RESPONSES_API_ENABLED:
        return responses_api_call(prompt)
    else:
        return chat_completions_call(prompt)
```

### Phase 3: Testing and Validation

1. **A/B Testing Framework**
   ```python
   def compare_apis(prompt, user_id=None):
       # Run both APIs for comparison
       chat_response = chat_completions_call(prompt)
       responses_response = responses_api_call(prompt)
       
       # Log results for analysis
       log_comparison(user_id, prompt, chat_response, responses_response)
       
       # Return based on user segment
       return responses_response if user_in_beta(user_id) else chat_response
   ```

2. **Metrics to Track**
   - Response quality scores
   - Response time comparison
   - Error rates
   - User satisfaction
   - Token usage and costs

3. **Testing Checklist**
   - [ ] Simple prompts work correctly
   - [ ] Tool usage functions properly
   - [ ] Conversation continuity maintained
   - [ ] Error handling works as expected
   - [ ] Performance meets requirements

### Phase 4: Full Cutover

1. **Migration Timeline**
   - Week 1-2: New features on Responses API
   - Week 3-4: Migrate simple use cases
   - Week 5-6: Migrate complex use cases
   - Week 7-8: Full cutover with fallback
   - Week 9+: Remove chat completions fallback

2. **Rollback Plan**
   ```python
   class APIFailover:
       def __init__(self):
           self.responses_api_healthy = True
       
       def call_with_failover(self, prompt):
           if self.responses_api_healthy:
               try:
                   return self.responses_api_call(prompt)
               except Exception as e:
                   self.responses_api_healthy = False
                   logger.error(f"Responses API failed: {e}")
           
           # Fallback to chat completions
           return self.chat_completions_call(prompt)
   ```

## Code Examples

### Chat Completions vs Responses API

#### Before: Chat Completions with Manual Tool Integration
```python
def research_with_chat_completions(query):
    # Manual web search integration
    search_results = external_web_search(query)
    
    # Manual conversation management
    messages = [
        {"role": "system", "content": "You are a research assistant."},
        {"role": "user", "content": f"Based on this search data: {search_results}, answer: {query}"}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7
    )
    
    return response.choices[0].message.content
```

#### After: Responses API with Built-in Tools
```python
def research_with_responses_api(query):
    # Built-in web search and automatic handling
    response = client.responses.create(
        model="gpt-4o",
        input=query,
        tools=[{"type": "web_search"}]
    )
    
    # Extract content from response
    content = []
    for message in response.output:
        if hasattr(message, 'content') and message.content:
            for content_item in message.content:
                if hasattr(content_item, 'text'):
                    content.append(content_item.text)
    
    return "\n".join(content)
```

#### Conversation Management Comparison

**Chat Completions (Manual State Management)**
```python
class ChatCompletionsConversation:
    def __init__(self):
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
    
    def get_response(self):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages
        )
        
        assistant_message = response.choices[0].message.content
        self.add_message("assistant", assistant_message)
        return assistant_message
```

**Responses API (Automatic State Management)**
```python
class ResponsesAPIConversation:
    def __init__(self):
        self.last_response_id = None
    
    def get_response(self, user_input):
        response = client.responses.create(
            model="gpt-4o",
            input=user_input,
            previous_response_id=self.last_response_id
        )
        
        self.last_response_id = response.id
        return response
```

## Best Practices

### 1. Error Handling
```python
def robust_responses_call(prompt):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.responses.create(
                model="gpt-4o",
                input=prompt,
                tools=[{"type": "web_search"}]
            )
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                # Fallback to chat completions if all retries fail
                return fallback_to_chat_completions(prompt)
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 2. Response Processing
```python
def extract_response_content(response):
    """Extract clean text content from Responses API response."""
    content = []
    
    if hasattr(response, 'output') and response.output:
        for message in response.output:
            if hasattr(message, 'content') and message.content:
                for content_item in message.content:
                    if hasattr(content_item, 'text'):
                        content.append(content_item.text)
    
    return "\n".join(content)
```

### 3. Tool Selection
```python
def smart_tool_selection(query_type):
    """Select appropriate tools based on query type."""
    tools = []
    
    if requires_current_info(query_type):
        tools.append({"type": "web_search"})
    
    if requires_document_search(query_type):
        tools.append({"type": "file_search"})
    
    return tools if tools else None
```

### 4. Performance Optimization
```python
# Cache responses for similar queries
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_responses_call(prompt_hash):
    response = client.responses.create(
        model="gpt-4o",
        input=prompt,
        tools=[{"type": "web_search"}]
    )
    return response
```

## Agents and SDK Information

### OpenAI Agent Platform

- Agents are systems that can independently accomplish tasks on your behalf
- Agents use an LLM to execute instructions and make decisions
- They have access to tools to gather context and take actions
- Always operate with clearly defined **guardrails** to ensure responses are safe and aligned

### Agents SDK

- This is the evolution of the Swarm API
- The basic idea of OpenAI's agent platform is to provide the library, infrastructure and tooling to iterate over agent logic
- Provides built-in state management, tool integration, and conversation handling