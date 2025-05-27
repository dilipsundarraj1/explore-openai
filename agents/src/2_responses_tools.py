"""
OpenAI Responses File

This file demonstrates different types of responses from the OpenAI API.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_responses_api_response(input_text=None):
    """Get a response using the new responses.create API endpoint.

    Args:
        input_text (str, optional): The text to send to the API. Defaults to None.

    Raises:
        ValueError: If the input_text is None or empty.
    """
    # Validate input
    if input_text is None or input_text.strip() == "":
        raise ValueError(
            "Input text cannot be empty. Please provide a prompt for the API."
        )

    # Create a response using the responses.create endpoint
    response = client.responses.create(
        model="gpt-4o",  # Using gpt-4o as gpt-4.1 might not be available for all users
        input=input_text,
    )

    print("Responses API Response:")
    print(response)
    print("\n")


def get_responses_with_web_search(input_text=None):
    """Get a response using the responses.create API endpoint with web_search tool.

    Args:
        input_text (str, optional): The text to send to the API. Defaults to None.

    Raises:
        ValueError: If the input_text is None or empty.
    """
    # Validate input
    if input_text is None or input_text.strip() == "":
        raise ValueError(
            "Input text cannot be empty. Please provide a prompt for the API."
        )

    # Create a response using the responses.create endpoint with web_search tool
    response = client.responses.create(
        model="gpt-4o",  # Using gpt-4o as gpt-4.1 might not be available for all users
        input=input_text,
        tools=[{"type": "web_search"}],
    )

    print("Responses API with Web Search:")
    print(response)
    print("\n")

    # Print the actual response content for better readability
    if response.output and len(response.output) > 0:
        print("Response content:")
        for message in response.output:
            if hasattr(message, "content") and message.content:
                for content_item in message.content:
                    if hasattr(content_item, "text"):
                        print(content_item.text)
    print("\n")


if __name__ == "__main__":
    # Example demonstrating error handling for empty input
    try:
        get_responses_api_response()
    except ValueError as e:
        print(f"Error caught: {e}")

    # Example with empty string
    try:
        get_responses_api_response("")
    except ValueError as e:
        print(f"Error caught: {e}")

    # Valid usage with a custom input
    try:
        default_prompt = "Tell me a three sentence bedtime story about a unicorn."
        print(f"Using prompt: '{default_prompt}'")
        get_responses_api_response(default_prompt)

        custom_prompt = "Write a haiku about programming."
        print(f"Using prompt: '{custom_prompt}'")
        get_responses_api_response(custom_prompt)
    except ValueError as e:
        print(f"Error caught: {e}")

    # Example using web search tool
    try:
        web_search_prompt = "Who won the Mens basketball in 2024 Olympics?"
        print(f"\nUsing web search with prompt: '{web_search_prompt}'")
        get_responses_with_web_search(web_search_prompt)
    except ValueError as e:
        print(f"Error caught: {e}")
    except Exception as e:
        print(f"Web search error: {e}")
