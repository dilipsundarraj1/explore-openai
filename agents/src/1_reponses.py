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


def get_responses_api_response():
    """Get a response using the new responses.create API endpoint."""
    # Create a response using the responses.create endpoint
    response = client.responses.create(
        model="gpt-4o",  # Using gpt-4o as gpt-4.1 might not be available for all users
        input="Tell me a three sentence bedtime story about a unicorn.",
    )

    print("Responses API Response:")
    print(response)
    print("\n")


if __name__ == "__main__":
    get_responses_api_response()
