# filepath: /Users/Z001QGD/Dilip/code-with-dilip/explore-openai/basics/src/13_reasoning_model.py
import argparse
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()
REASONING_MODEL = os.environ.get("OPEN_AI_REASONING_MODEL", "gpt-4o")


# Call the OpenAI reasoning model
def ask_reasoning_model(
    user_question: str,
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> ChatCompletion:
    print(f"Using model: {REASONING_MODEL}")

    system_message = """
    You are a helpful assistant with reasoning capabilities.
    When presented with a problem, follow these steps:
    1. Break down the problem into clear steps
    2. Work through each step methodically
    3. Show your reasoning process explicitly
    4. State your final conclusion
    """

    response = client.chat.completions.create(
        model=REASONING_MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_question},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    print(f"Response type: {type(response)}")
    return response


def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description="OpenAI Reasoning Model Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python 13_reasoning_model.py -q "Solve 23 x 45" # Get a direct answer to a question
""",
    )

    parser.add_argument(
        "-q", "--question", type=str, help="Ask a question to the reasoning model"
    )
    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=0.7,
        help="Set the temperature for the model (0.0-1.0)",
    )

    args = parser.parse_args()

    # Handle command-line arguments
    if args.question:
        response = ask_reasoning_model(args.question, temperature=args.temperature)
        print("\nResponse:")
        print(response.choices[0].message.content)
    else:
        # No arguments provided, run interactive mode
        print("\n==== OpenAI Reasoning Model Interactive Mode ====")
        print("Type 'exit' or 'quit' to end the session.")
        print("===================================================\n")

        while True:
            user_input = input("\nEnter your question: ")

            if user_input.lower() in ["exit", "quit"]:
                print("Exiting interactive session. Goodbye!")
                break

            response = ask_reasoning_model(user_input)
            print("\nResponse:")
            print(response.choices[0].message.content)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
