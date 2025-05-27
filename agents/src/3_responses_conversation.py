"""
OpenAI Responses Conversation File

This file demonstrates how to create a conversation flow using the responses.create API
by utilizing the previous_response_id parameter.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_initial_response(input_text=None):
    """Get the initial response using the responses.create API endpoint with web_search enabled.

    Args:
        input_text (str, optional): The text to send to the API. Defaults to None.

    Raises:
        ValueError: If the input_text is None or empty.

    Returns:
        Response: The response object from the API call.
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
        tools=[{"type": "web_search"}],  # Enable web search capability
    )

    print("Initial Response (with web search):")
    print(f"Response ID: {response.id}")

    # Print the actual response content for better readability
    if response.output and len(response.output) > 0:
        print("Response content:")
        for message in response.output:
            if hasattr(message, "content") and message.content:
                for content_item in message.content:
                    if hasattr(content_item, "text"):
                        print(content_item.text)
    print("\n")

    return response


def get_followup_response(input_text=None, previous_response_id=None):
    """Get a followup response using the responses.create API endpoint
    with a reference to a previous response and web_search enabled.

    Args:
        input_text (str, optional): The text to send to the API. Defaults to None.
        previous_response_id (str, optional): The ID of the previous response. Defaults to None.

    Raises:
        ValueError: If the input_text is None or empty.
        ValueError: If the previous_response_id is None or empty.

    Returns:
        Response: The response object from the API call.
    """
    # Validate input
    if input_text is None or input_text.strip() == "":
        raise ValueError(
            "Input text cannot be empty. Please provide a prompt for the API."
        )

    # Validate previous_response_id
    if previous_response_id is None or previous_response_id.strip() == "":
        raise ValueError(
            "Previous response ID cannot be empty. Please provide a valid response ID."
        )

    # Create a followup response using the responses.create endpoint with web_search tool
    response = client.responses.create(
        model="gpt-4o",  # Using gpt-4o as gpt-4.1 might not be available for all users
        input=input_text,
        previous_response_id=previous_response_id,
        tools=[{"type": "web_search"}],  # Enable web search capability
    )

    print(
        f"Followup Response with web search (referencing response {previous_response_id}):"
    )
    print(f"Response ID: {response.id}")

    # Print the actual response content for better readability
    if response.output and len(response.output) > 0:
        print("Response content:")
        for message in response.output:
            if hasattr(message, "content") and message.content:
                for content_item in message.content:
                    if hasattr(content_item, "text"):
                        print(content_item.text)
    print("\n")

    return response


def get_response_by_id(response_id=None):
    """Retrieve a specific response by its ID.

    Args:
        response_id (str, optional): The ID of the response to retrieve. Defaults to None.

    Raises:
        ValueError: If the response_id is None or empty.

    Returns:
        Response: The retrieved response object from the API.
    """
    # Validate response_id
    if response_id is None or response_id.strip() == "":
        raise ValueError(
            "Response ID cannot be empty. Please provide a valid response ID."
        )

    # Retrieve the response using the responses.retrieve endpoint
    response = client.responses.retrieve(response_id=response_id)

    print(f"Retrieved Response with ID: {response.id}")

    # Print the actual response content for better readability
    if response.output and len(response.output) > 0:
        print("Response content:")
        for message in response.output:
            if hasattr(message, "content") and message.content:
                for content_item in message.content:
                    if hasattr(content_item, "text"):
                        print(content_item.text)
    print("\n")

    return response


def delete_response(response_id=None):
    """Delete a specific response by its ID.

    Args:
        response_id (str, optional): The ID of the response to delete. Defaults to None.

    Raises:
        ValueError: If the response_id is None or empty.

    Returns:
        DeletionStatus: The deletion status object from the API.
    """
    # Validate response_id
    if response_id is None or response_id.strip() == "":
        raise ValueError(
            "Response ID cannot be empty. Please provide a valid response ID."
        )

    # Delete the response using the responses.delete endpoint
    deletion_status = client.responses.delete(response_id=response_id)

    print(f"Deleted Response with ID: {response_id}")
    print(f"Deletion Status: {deletion_status}")
    print("\n")

    return deletion_status


def simulate_conversation():
    """Simulate a conversation using the responses API with Olympics 2024 as the topic."""
    try:
        # Initial query about Olympics 2024
        initial_prompt = (
            "Tell me about the main highlights of the 2024 Summer Olympics in Paris."
        )
        print(f"Initial prompt: '{initial_prompt}'")
        initial_response = get_initial_response(initial_prompt)

        # First followup about specific sports
        followup_prompt_1 = (
            "Which countries won the most medals in swimming and athletics events?"
        )
        print(f"Followup prompt 1: '{followup_prompt_1}'")
        followup_response_1 = get_followup_response(
            followup_prompt_1, initial_response.id
        )

        # Second followup about memorable moments
        followup_prompt_2 = "What were some of the most memorable or surprising moments from these games?"
        print(f"Followup prompt 2: '{followup_prompt_2}'")
        followup_response_2 = get_followup_response(
            followup_prompt_2, followup_response_1.id
        )

        print("Olympics 2024 conversation completed successfully!")

        return initial_response.id, followup_response_1.id, followup_response_2.id

    except ValueError as e:
        print(f"Error caught: {e}")
        return None, None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None, None


def demonstrate_retrieve_delete():
    """Demonstrate how to retrieve and delete responses."""
    try:
        # First simulate a conversation to get some response IDs
        print("=== Starting conversation simulation ===\n")
        first_id, second_id, third_id = simulate_conversation()

        if first_id and second_id:
            # Demonstrate retrieval of a stored response
            print("\n=== Demonstrating Response Retrieval ===")
            print(f"Retrieving response with ID: {first_id}")
            retrieved_response = get_response_by_id(first_id)
            print("Retrieved response content:")
            print(retrieved_response.output[0].content)
            print("\n")
            # Demonstrate deletion of a stored response
            print("\n=== Demonstrating Response Deletion ===")
            print(f"Deleting response with ID: {second_id}")
            deletion_result = delete_response(second_id)
            print(f"Deletion result: {deletion_result}")
            print("\n")
            # Confirm deletion by attempting to retrieve the deleted response
            print(f"Attempting to retrieve deleted response with ID: {second_id}")
            # Try to retrieve the deleted response to confirm it's gone
            try:
                print("\nAttempting to retrieve the deleted response (should fail):")
                deleted_response = get_response_by_id(second_id)
            except Exception as e:
                print(f"Expected error: {e}")

    except ValueError as e:
        print(f"Error caught: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Uncomment the function you want to run
    simulate_conversation()
    demonstrate_retrieve_delete()
