"""
OpenAI Responses API - Comprehensive Integration Example

This file demonstrates a complete integration of the OpenAI Responses API
showcasing all key features and best practices for production usage.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ResponsesAPIClient:
    """A comprehensive client wrapper for OpenAI Responses API."""

    def __init__(self, model: str = "gpt-4o"):
        """Initialize the Responses API client.

        Args:
            model (str): The model to use for responses. Defaults to "gpt-4o".
        """
        self.client = client
        self.model = model
        self.conversation_history: List[Dict] = []

    def create_simple_response(self, input_text: str) -> Dict:
        """Create a simple response without tools.

        Args:
            input_text (str): The input text/prompt for the API.

        Returns:
            Dict: Formatted response with content and metadata.

        Raises:
            ValueError: If input_text is empty.
        """
        if not input_text or not input_text.strip():
            raise ValueError("Input text cannot be empty.")

        try:
            response = self.client.responses.create(model=self.model, input=input_text)

            formatted_response = self._format_response(response, "simple")
            self._save_to_history(input_text, formatted_response, response.id)

            return formatted_response

        except Exception as e:
            print(f"Error creating simple response: {e}")
            raise

    def create_response_with_web_search(self, input_text: str) -> Dict:
        """Create a response with web search capabilities.

        Args:
            input_text (str): The input text/prompt for the API.

        Returns:
            Dict: Formatted response with content and metadata.
        """
        if not input_text or not input_text.strip():
            raise ValueError("Input text cannot be empty.")

        try:
            response = self.client.responses.create(
                model=self.model, input=input_text, tools=[{"type": "web_search"}]
            )

            formatted_response = self._format_response(response, "web_search")
            self._save_to_history(input_text, formatted_response, response.id)

            return formatted_response

        except Exception as e:
            print(f"Error creating web search response: {e}")
            raise

    def create_response_with_file_search(
        self, input_text: str, file_ids: Optional[List[str]] = None
    ) -> Dict:
        """Create a response with file search capabilities.

        Args:
            input_text (str): The input text/prompt for the API.
            file_ids (List[str], optional): List of file IDs to search within.

        Returns:
            Dict: Formatted response with content and metadata.
        """
        if not input_text or not input_text.strip():
            raise ValueError("Input text cannot be empty.")

        try:
            tools = [{"type": "file_search"}]

            response = self.client.responses.create(
                model=self.model, input=input_text, tools=tools
            )

            formatted_response = self._format_response(response, "file_search")
            self._save_to_history(input_text, formatted_response, response.id)

            return formatted_response

        except Exception as e:
            print(f"Error creating file search response: {e}")
            raise

    def create_conversation_response(
        self, input_text: str, previous_response_id: str, use_web_search: bool = False
    ) -> Dict:
        """Create a followup response in a conversation.

        Args:
            input_text (str): The input text/prompt for the API.
            previous_response_id (str): ID of the previous response to reference.
            use_web_search (bool): Whether to enable web search. Defaults to False.

        Returns:
            Dict: Formatted response with content and metadata.
        """
        if not input_text or not input_text.strip():
            raise ValueError("Input text cannot be empty.")

        if not previous_response_id or not previous_response_id.strip():
            raise ValueError("Previous response ID cannot be empty.")

        try:
            tools = []
            if use_web_search:
                tools.append({"type": "web_search"})

            response = self.client.responses.create(
                model=self.model,
                input=input_text,
                previous_response_id=previous_response_id,
                tools=tools if tools else None,
            )

            response_type = "conversation_web" if use_web_search else "conversation"
            formatted_response = self._format_response(response, response_type)
            self._save_to_history(
                input_text, formatted_response, response.id, previous_response_id
            )

            return formatted_response

        except Exception as e:
            print(f"Error creating conversation response: {e}")
            raise

    def create_response_with_custom_tools(
        self, input_text: str, tools: List[Dict]
    ) -> Dict:
        """Create a response with custom tools.

        Args:
            input_text (str): The input text/prompt for the API.
            tools (List[Dict]): List of custom tools to use.

        Returns:
            Dict: Formatted response with content and metadata.
        """
        if not input_text or not input_text.strip():
            raise ValueError("Input text cannot be empty.")

        if not tools:
            raise ValueError("Tools list cannot be empty when using custom tools.")

        try:
            response = self.client.responses.create(
                model=self.model, input=input_text, tools=tools
            )

            formatted_response = self._format_response(response, "custom_tools")
            self._save_to_history(input_text, formatted_response, response.id)

            return formatted_response

        except Exception as e:
            print(f"Error creating custom tools response: {e}")
            raise

    def _format_response(self, response, response_type: str) -> Dict:
        """Format the API response into a standardized structure.

        Args:
            response: The raw API response object.
            response_type (str): The type of response for tracking.

        Returns:
            Dict: Formatted response structure.
        """
        formatted = {
            "id": response.id,
            "type": response_type,
            "model": getattr(response, "model", self.model),
            "timestamp": datetime.now().isoformat(),
            "content": [],
            "usage": getattr(response, "usage", {}),
            "raw_response": response,
        }

        # Extract content from response
        if hasattr(response, "output") and response.output:
            for message in response.output:
                if hasattr(message, "content") and message.content:
                    for content_item in message.content:
                        if hasattr(content_item, "text"):
                            formatted["content"].append(content_item.text)

        return formatted

    def _save_to_history(
        self,
        input_text: str,
        formatted_response: Dict,
        response_id: str,
        previous_response_id: Optional[str] = None,
    ):
        """Save interaction to conversation history.

        Args:
            input_text (str): The input prompt.
            formatted_response (Dict): The formatted response.
            response_id (str): Current response ID.
            previous_response_id (str, optional): Previous response ID if this is a followup.
        """
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "response": formatted_response,
            "response_id": response_id,
            "previous_response_id": previous_response_id,
        }
        self.conversation_history.append(history_entry)

    def get_conversation_history(self) -> List[Dict]:
        """Get the complete conversation history.

        Returns:
            List[Dict]: List of conversation entries.
        """
        return self.conversation_history.copy()

    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history.clear()

    def print_formatted_response(self, formatted_response: Dict):
        """Print a formatted response in a readable format.

        Args:
            formatted_response (Dict): The formatted response to print.
        """
        print(f"Response ID: {formatted_response['id']}")
        print(f"Type: {formatted_response['type']}")
        print(f"Model: {formatted_response['model']}")
        print(f"Timestamp: {formatted_response['timestamp']}")

        if formatted_response["usage"]:
            print(f"Usage: {formatted_response['usage']}")

        print("Content:")
        for content in formatted_response["content"]:
            print(f"  {content}")
        print()


def demonstrate_simple_usage():
    """Demonstrate basic usage of the Responses API."""
    print("=== SIMPLE USAGE DEMONSTRATION ===")

    api_client = ResponsesAPIClient()

    # Simple response
    try:
        simple_prompt = (
            "Write a brief explanation of quantum computing in simple terms."
        )
        print(f"Input: {simple_prompt}\n")

        response = api_client.create_simple_response(simple_prompt)
        api_client.print_formatted_response(response)

    except Exception as e:
        print(f"Error in simple usage: {e}")


def demonstrate_web_search():
    """Demonstrate web search capabilities."""
    print("=== WEB SEARCH DEMONSTRATION ===")

    api_client = ResponsesAPIClient()

    try:
        web_prompt = "What are the latest developments in AI safety research in 2024?"
        print(f"Input: {web_prompt}\n")

        response = api_client.create_response_with_web_search(web_prompt)
        api_client.print_formatted_response(response)

    except Exception as e:
        print(f"Error in web search demo: {e}")


def demonstrate_conversation_flow():
    """Demonstrate conversation flow with multiple exchanges."""
    print("=== CONVERSATION FLOW DEMONSTRATION ===")

    api_client = ResponsesAPIClient()

    try:
        # Initial question
        initial_prompt = "Tell me about the benefits of renewable energy."
        print(f"Initial Input: {initial_prompt}\n")

        initial_response = api_client.create_response_with_web_search(initial_prompt)
        api_client.print_formatted_response(initial_response)

        # Followup question
        followup_prompt = (
            "Which renewable energy source is most cost-effective for residential use?"
        )
        print(f"Followup Input: {followup_prompt}\n")

        followup_response = api_client.create_conversation_response(
            followup_prompt, initial_response["id"], use_web_search=True
        )
        api_client.print_formatted_response(followup_response)

        # Show conversation history
        print("=== CONVERSATION HISTORY ===")
        history = api_client.get_conversation_history()
        print(f"Total interactions: {len(history)}")
        for i, entry in enumerate(history, 1):
            print(f"  {i}. {entry['timestamp']}: {entry['input'][:50]}...")

    except Exception as e:
        print(f"Error in conversation flow demo: {e}")


def demonstrate_custom_tools():
    """Demonstrate custom tools usage."""
    print("=== CUSTOM TOOLS DEMONSTRATION ===")

    api_client = ResponsesAPIClient()

    try:
        # Example with multiple built-in tools
        custom_tools = [{"type": "web_search"}, {"type": "file_search"}]

        custom_prompt = "Research the current state of electric vehicle adoption and find relevant data files."
        print(f"Input: {custom_prompt}\n")

        response = api_client.create_response_with_custom_tools(
            custom_prompt, custom_tools
        )
        api_client.print_formatted_response(response)

    except Exception as e:
        print(f"Error in custom tools demo: {e}")


def demonstrate_error_handling():
    """Demonstrate proper error handling."""
    print("=== ERROR HANDLING DEMONSTRATION ===")

    api_client = ResponsesAPIClient()

    # Test empty input
    try:
        api_client.create_simple_response("")
    except ValueError as e:
        print(f"Caught expected error for empty input: {e}")

    # Test invalid conversation
    try:
        api_client.create_conversation_response("test", "")
    except ValueError as e:
        print(f"Caught expected error for invalid conversation: {e}")

    print("Error handling working correctly!\n")


def main():
    """Main function to run all demonstrations."""
    print("OpenAI Responses API - Comprehensive Integration Example")
    print("=" * 60)

    # Run all demonstrations
    demonstrate_simple_usage()
    demonstrate_web_search()
    demonstrate_conversation_flow()
    demonstrate_custom_tools()
    demonstrate_error_handling()

    print("All demonstrations completed!")


if __name__ == "__main__":
    main()
