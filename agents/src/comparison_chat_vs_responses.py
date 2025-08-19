"""
Side-by-Side Comparison: Chat Completions vs Responses API

This file demonstrates the differences between Chat Completions API
and Responses API with practical examples.
"""

import os
from datetime import datetime
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =============================================================================
# BASIC USAGE COMPARISON
# =============================================================================


def chat_completions_basic(prompt: str) -> str:
    """Basic usage with Chat Completions API."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1000,
    )

    return response.choices[0].message.content


def responses_api_basic(prompt: str) -> str:
    """Basic usage with Responses API."""
    response = client.responses.create(model="gpt-4o", input=prompt)

    # Extract content from the new response format
    content = []
    if hasattr(response, "output") and response.output:
        for message in response.output:
            if hasattr(message, "content") and message.content:
                for content_item in message.content:
                    if hasattr(content_item, "text"):
                        content.append(content_item.text)

    return "\n".join(content)


# =============================================================================
# CONVERSATION MANAGEMENT COMPARISON
# =============================================================================


class ChatCompletionsConversation:
    """Conversation management with Chat Completions API (Manual)."""

    def __init__(self, system_prompt: str = "You are a helpful assistant."):
        self.messages = [{"role": "system", "content": system_prompt}]

    def add_user_message(self, content: str):
        """Add a user message to the conversation."""
        self.messages.append({"role": "user", "content": content})

    def get_assistant_response(self) -> str:
        """Get assistant response and add it to conversation history."""
        response = client.chat.completions.create(
            model="gpt-4o", messages=self.messages, temperature=0.7
        )

        assistant_content = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": assistant_content})

        return assistant_content

    def get_conversation_history(self) -> List[Dict]:
        """Get the full conversation history."""
        return self.messages.copy()


class ResponsesAPIConversation:
    """Conversation management with Responses API (Automatic)."""

    def __init__(self):
        self.conversation_history = []
        self.last_response_id = None

    def get_response(self, user_input: str, use_web_search: bool = False) -> Dict:
        """Get a response and automatically maintain conversation state."""
        tools = [{"type": "web_search"}] if use_web_search else None

        response = client.responses.create(
            model="gpt-4o",
            input=user_input,
            previous_response_id=self.last_response_id,
            tools=tools,
        )

        # Update conversation state
        self.last_response_id = response.id

        # Extract content
        content = []
        if hasattr(response, "output") and response.output:
            for message in response.output:
                if hasattr(message, "content") and message.content:
                    for content_item in message.content:
                        if hasattr(content_item, "text"):
                            content.append(content_item.text)

        # Save to history
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "assistant_response": "\n".join(content),
            "response_id": response.id,
            "tools_used": tools,
        }
        self.conversation_history.append(interaction)

        return interaction

    def get_conversation_history(self) -> List[Dict]:
        """Get the full conversation history."""
        return self.conversation_history.copy()


# =============================================================================
# TOOL USAGE COMPARISON
# =============================================================================


def chat_completions_with_tools(query: str) -> str:
    """Tool usage with Chat Completions API (Manual Setup)."""
    # Manual tool definition
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search the web for current information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query"}
                    },
                    "required": ["query"],
                },
            },
        }
    ]

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant with web search capabilities.",
        },
        {"role": "user", "content": query},
    ]

    response = client.chat.completions.create(
        model="gpt-4o", messages=messages, tools=tools, tool_choice="auto"
    )

    message = response.choices[0].message

    # Handle tool calls (simplified for this example)
    if message.tool_calls:
        # In a real implementation, you'd execute the tool calls
        # and add the results back to the conversation
        tool_call = message.tool_calls[0]
        return f"Would call tool: {tool_call.function.name} with args: {tool_call.function.arguments}"

    return message.content


def responses_api_with_tools(query: str) -> str:
    """Tool usage with Responses API (Built-in Tools)."""
    response = client.responses.create(
        model="gpt-4o",
        input=query,
        tools=[{"type": "web_search"}],  # Built-in web search
    )

    # Extract content (tools are automatically handled)
    content = []
    if hasattr(response, "output") and response.output:
        for message in response.output:
            if hasattr(message, "content") and message.content:
                for content_item in message.content:
                    if hasattr(content_item, "text"):
                        content.append(content_item.text)

    return "\n".join(content)


# =============================================================================
# ERROR HANDLING COMPARISON
# =============================================================================


def chat_completions_with_error_handling(prompt: str, max_retries: int = 3) -> str:
    """Chat Completions with manual error handling and retries."""
    import random
    import time

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                timeout=30,
            )
            return response.choices[0].message.content

        except Exception as e:
            if attempt == max_retries - 1:
                raise Exception(f"Failed after {max_retries} attempts: {str(e)}")

            # Exponential backoff with jitter
            delay = (2**attempt) + random.uniform(0, 1)
            time.sleep(delay)
            print(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s...")


def responses_api_with_error_handling(prompt: str, max_retries: int = 3) -> str:
    """Responses API with error handling and fallback."""
    import time

    for attempt in range(max_retries):
        try:
            response = client.responses.create(
                model="gpt-4o", input=prompt, tools=[{"type": "web_search"}]
            )

            # Extract content
            content = []
            if hasattr(response, "output") and response.output:
                for message in response.output:
                    if hasattr(message, "content") and message.content:
                        for content_item in message.content:
                            if hasattr(content_item, "text"):
                                content.append(content_item.text)

            return "\n".join(content)

        except Exception as e:
            if attempt == max_retries - 1:
                # Fallback to chat completions
                print(
                    f"Responses API failed, falling back to Chat Completions: {str(e)}"
                )
                return chat_completions_basic(prompt)

            delay = 2**attempt
            time.sleep(delay)
            print(f"Attempt {attempt + 1} failed, retrying in {delay}s...")


# =============================================================================
# DEMONSTRATION FUNCTIONS
# =============================================================================


def demonstrate_basic_comparison():
    """Demonstrate basic usage comparison."""
    print("=== BASIC USAGE COMPARISON ===\n")

    prompt = "Explain quantum computing in simple terms."

    print("CHAT COMPLETIONS API:")
    try:
        chat_result = chat_completions_basic(prompt)
        print(f"Result: {chat_result[:100]}...\n")
    except Exception as e:
        print(f"Error: {e}\n")

    print("RESPONSES API:")
    try:
        responses_result = responses_api_basic(prompt)
        print(f"Result: {responses_result[:100]}...\n")
    except Exception as e:
        print(f"Error: {e}\n")


def demonstrate_conversation_comparison():
    """Demonstrate conversation management comparison."""
    print("=== CONVERSATION MANAGEMENT COMPARISON ===\n")

    print("CHAT COMPLETIONS (Manual State Management):")
    chat_conv = ChatCompletionsConversation()

    # First exchange
    chat_conv.add_user_message("What is machine learning?")
    response1 = chat_conv.get_assistant_response()
    print(f"Assistant: {response1[:80]}...")

    # Second exchange
    chat_conv.add_user_message("Can you give me a practical example?")
    response2 = chat_conv.get_assistant_response()
    print(f"Assistant: {response2[:80]}...\n")

    print(
        f"Chat Completions - Messages in history: {len(chat_conv.get_conversation_history())}"
    )

    print("\nRESPONSES API (Automatic State Management):")
    responses_conv = ResponsesAPIConversation()

    # First exchange
    interaction1 = responses_conv.get_response("What is machine learning?")
    print(f"Assistant: {interaction1['assistant_response'][:80]}...")

    # Second exchange
    interaction2 = responses_conv.get_response("Can you give me a practical example?")
    print(f"Assistant: {interaction2['assistant_response'][:80]}...\n")

    print(
        f"Responses API - Interactions in history: {len(responses_conv.get_conversation_history())}"
    )


def demonstrate_tools_comparison():
    """Demonstrate tool usage comparison."""
    print("\n=== TOOL USAGE COMPARISON ===\n")

    query = "What are the latest developments in AI in 2024?"

    print("CHAT COMPLETIONS (Manual Tool Setup):")
    try:
        chat_tools_result = chat_completions_with_tools(query)
        print(f"Result: {chat_tools_result[:100]}...\n")
    except Exception as e:
        print(f"Error: {e}\n")

    print("RESPONSES API (Built-in Tools):")
    try:
        responses_tools_result = responses_api_with_tools(query)
        print(f"Result: {responses_tools_result[:100]}...\n")
    except Exception as e:
        print(f"Error: {e}\n")


def demonstrate_error_handling_comparison():
    """Demonstrate error handling approaches."""
    print("=== ERROR HANDLING COMPARISON ===\n")

    # Use a potentially problematic prompt
    prompt = "Generate a very long response about the history of computing."

    print("CHAT COMPLETIONS (Manual Error Handling):")
    try:
        result = chat_completions_with_error_handling(prompt)
        print(f"Success: {result[:50]}...\n")
    except Exception as e:
        print(f"Failed: {e}\n")

    print("RESPONSES API (With Fallback):")
    try:
        result = responses_api_with_error_handling(prompt)
        print(f"Success: {result[:50]}...\n")
    except Exception as e:
        print(f"Failed: {e}\n")


# =============================================================================
# MIGRATION UTILITY FUNCTIONS
# =============================================================================


def analyze_chat_completion_usage(messages: List[Dict]) -> Dict:
    """Analyze chat completion usage to help with migration planning."""
    analysis = {
        "total_messages": len(messages),
        "user_messages": len([m for m in messages if m.get("role") == "user"]),
        "system_messages": len([m for m in messages if m.get("role") == "system"]),
        "assistant_messages": len(
            [m for m in messages if m.get("role") == "assistant"]
        ),
        "has_function_calls": any(m.get("function_call") for m in messages),
        "has_tool_calls": any(m.get("tool_calls") for m in messages),
        "complexity": "simple",
    }

    # Determine complexity
    if analysis["has_function_calls"] or analysis["has_tool_calls"]:
        analysis["complexity"] = "complex"
    elif analysis["total_messages"] > 10:
        analysis["complexity"] = "medium"

    return analysis


def suggest_migration_approach(analysis: Dict) -> str:
    """Suggest migration approach based on usage analysis."""
    if analysis["complexity"] == "simple":
        return "Direct migration - Low risk, high priority"
    elif analysis["complexity"] == "medium":
        return "Gradual migration - Medium risk, test thoroughly"
    else:
        return "Complex migration - High risk, plan carefully with fallbacks"


def main():
    """Run all demonstrations."""
    print("OpenAI APIs Comparison: Chat Completions vs Responses API")
    print("=" * 70)

    try:
        demonstrate_basic_comparison()
        demonstrate_conversation_comparison()
        demonstrate_tools_comparison()
        demonstrate_error_handling_comparison()

        # Example migration analysis
        print("\n=== MIGRATION ANALYSIS EXAMPLE ===")
        sample_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "What's the weather like?"},
        ]

        analysis = analyze_chat_completion_usage(sample_messages)
        suggestion = suggest_migration_approach(analysis)

        print(f"Usage Analysis: {analysis}")
        print(f"Migration Suggestion: {suggestion}")

    except Exception as e:
        print(f"Demonstration error: {e}")
        print("Note: Some features may require proper API setup and credits.")


if __name__ == "__main__":
    main()
