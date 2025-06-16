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


def get_reasoning_response(
    prompt: str,
    use_json: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> str:
    """Get a response from the OpenAI reasoning model.

    Args:
        prompt: The user prompt to send to the model
        use_json: Whether to request a JSON response
        temperature: Controls randomness (0-1), lower is more deterministic
        max_tokens: Maximum number of tokens in the response

    Returns:
        The model's response as a string
    """
    try:
        response_format = {"type": "json_object"} if use_json else {"type": "text"}

        response = openai.chat.completions.create(
            model=REASONING_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant with strong reasoning capabilities.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

        return response.choices[0].message.content
    except Exception as e:
        console.print(f"[bold red]Error calling OpenAI API:[/bold red] {e}")
        return ""


def get_reasoning_with_steps(
    problem: str, temperature: float = 0.2, max_tokens: int = 2000
) -> str:
    """Get reasoning with step-by-step breakdown for a given problem.

    Args:
        problem: The problem or question requiring reasoning
        temperature: Controls randomness (0-1), lower is more deterministic
        max_tokens: Maximum number of tokens in the response

    Returns:
        The model's step-by-step reasoning process
    """
    system_prompt = """
    You are an expert reasoning assistant. When presented with a problem:
    1. Break down the problem into clear steps
    2. Work through each step methodically
    3. Show your reasoning process explicitly
    4. State your final conclusion
    
    Format your response as a clear step-by-step analysis.
    """

    try:
        response = openai.chat.completions.create(
            model=REASONING_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": problem},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content
    except Exception as e:
        console.print(f"[bold red]Error calling OpenAI API:[/bold red] {e}")
        return ""


def multi_step_reasoning(question: str) -> Dict[str, str]:
    """Perform multi-step reasoning on a complex question.

    Args:
        question: The complex question requiring multi-step reasoning

    Returns:
        Dictionary with step-by-step reasoning and final answer
    """
    try:
        # Step 1: Problem decomposition
        decomposition_prompt = f"""
        For the following question, break it down into smaller sub-problems that need to be solved:
        
        Question: {question}
        
        Return your answer as a JSON object with:
        1. "sub_problems": a list of sub-problems
        2. "reasoning": your reasoning for this decomposition
        """

        decomposition_response = get_reasoning_response(
            decomposition_prompt, use_json=True
        )
        decomposition_data = json.loads(decomposition_response)

        # Step 2: Solve each sub-problem
        sub_problems = decomposition_data["sub_problems"]
        solutions = []

        for i, sub_problem in enumerate(sub_problems):
            solve_prompt = f"Solve this sub-problem: {sub_problem}"
            solution = get_reasoning_response(solve_prompt)
            solutions.append({"problem": sub_problem, "solution": solution})

        # Step 3: Combine solutions to answer original question
        combine_prompt = f"""
        Given these solutions to sub-problems:
        {json.dumps(solutions, indent=2)}
        
        Provide a coherent answer to the original question:
        {question}
        """

        final_answer = get_reasoning_response(combine_prompt)

        return {
            "original_question": question,
            "sub_problems": decomposition_data["sub_problems"],
            "decomposition_reasoning": decomposition_data["reasoning"],
            "sub_problem_solutions": solutions,
            "final_answer": final_answer,
        }
    except Exception as e:
        console.print(f"[bold red]Error in multi-step reasoning:[/bold red] {e}")
        return {"original_question": question, "error": str(e)}


def chain_of_thought_reasoning(question: str) -> str:
    """Perform chain-of-thought reasoning on a question.

    Args:
        question: The question to analyze using chain-of-thought reasoning

    Returns:
        The model's chain of thought reasoning as a string
    """
    prompt = f"""
    Question: {question}
    
    Please solve this step-by-step using chain-of-thought reasoning. 
    First, think about what information we need. 
    Next, work through the problem systematically.
    Show all your work and explain your thought process at each step.
    Finally, provide your conclusion.
    """

    return get_reasoning_response(prompt, temperature=0.3)


def interactive_reasoning_session():
    """Run an interactive reasoning session with the model."""
    console.print(
        Panel(
            "[bold cyan]OpenAI Reasoning Model Interactive Session[/bold cyan]\n"
            "Enter your questions or problems, and the AI will provide reasoning and solutions.\n"
            "Type [bold]'exit'[/bold], [bold]'quit'[/bold], or [bold]Ctrl+C[/bold] to end the session.",
            expand=False,
            border_style="cyan",
        )
    )

    console.print(f"[green]Using model:[/green] [bold]{REASONING_MODEL}[/bold]")
    console.print("[yellow]Type 'mode:cot' for Chain of Thought reasoning[/yellow]")
    console.print("[yellow]Type 'mode:steps' for Step-by-Step reasoning[/yellow]")
    console.print("[yellow]Type 'mode:multi' for Multi-Step reasoning[/yellow]")
    console.print("[yellow]Type 'mode:normal' for standard responses[/yellow]")

    # Default mode
    mode = "normal"

    try:
        while True:
            # Display prompt based on current mode
            mode_display = {
                "normal": "Standard",
                "cot": "Chain of Thought",
                "steps": "Step-by-Step",
                "multi": "Multi-Step",
            }.get(mode, "Standard")

            console.print(
                f"\n[bold blue]Question ([italic]{mode_display} mode[/italic]):[/bold blue]"
            )
            user_input = input()

            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                console.print(
                    "[bold green]Exiting interactive session. Goodbye![/bold green]"
                )
                break

            # Check for mode switch command
            if user_input.lower().startswith("mode:"):
                new_mode = user_input.lower().split(":", 1)[1].strip()
                if new_mode in ["normal", "cot", "steps", "multi"]:
                    mode = new_mode
                    console.print(
                        f"[bold green]Switched to [italic]{mode_display} mode[/italic][/bold green]"
                    )
                else:
                    console.print(
                        "[bold red]Invalid mode. Valid options: normal, cot, steps, multi[/bold red]"
                    )
                continue

            # Skip empty inputs
            if not user_input.strip():
                continue

            console.print("[bold blue]Thinking...[/bold blue]")

            # Process based on mode
            if mode == "cot":
                response = chain_of_thought_reasoning(user_input)
            elif mode == "steps":
                response = get_reasoning_with_steps(user_input)
            elif mode == "multi":
                result = multi_step_reasoning(user_input)
                # Format multi-step result nicely
                response = f"# Analysis for: {result['original_question']}\n\n"
                response += "## Problem Decomposition\n\n"
                response += f"{result['decomposition_reasoning']}\n\n"
                response += "## Sub-Problems\n\n"

                for i, prob in enumerate(result["sub_problems"]):
                    response += f"{i + 1}. {prob}\n"

                response += "\n## Solutions to Sub-Problems\n\n"

                for i, sol in enumerate(result["sub_problem_solutions"]):
                    response += f"### Sub-Problem {i + 1}: {sol['problem']}\n\n"
                    response += f"{sol['solution']}\n\n"

                response += f"## Final Answer\n\n{result['final_answer']}"
            else:  # normal mode
                response = get_reasoning_response(user_input)

            # Display the response using rich formatting
            console.print("[bold green]Response:[/bold green]")
            console.print(Panel(Markdown(response), border_style="green"))

    except KeyboardInterrupt:
        console.print("\n[bold green]Session terminated by user. Goodbye![/bold green]")
    except Exception as e:
        console.print(f"\n[bold red]An error occurred:[/bold red] {e}")


def main():
    """Main function to parse arguments and run the appropriate function."""
    parser = argparse.ArgumentParser(
        description="OpenAI Reasoning Model Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python 13_reasoning_model.py -i                 # Start interactive session
  python 13_reasoning_model.py -q "Solve 23 x 45" # Get a direct answer to a question
  python 13_reasoning_model.py -c "Why is the sky blue?" # Use chain-of-thought reasoning
  python 13_reasoning_model.py -s "Explain quantum computing" # Step-by-step reasoning
  python 13_reasoning_model.py -m "How would increasing interest rates affect the economy?" # Multi-step reasoning
""",
    )

    # Add arguments
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Start an interactive reasoning session",
    )
    parser.add_argument(
        "-q",
        "--question",
        type=str,
        help="Ask a direct question to the reasoning model",
    )
    parser.add_argument(
        "-c",
        "--chain-of-thought",
        type=str,
        help="Apply chain-of-thought reasoning to a question",
    )
    parser.add_argument(
        "-s",
        "--step-by-step",
        type=str,
        help="Get step-by-step reasoning for a problem",
    )
    parser.add_argument(
        "-m",
        "--multi-step",
        type=str,
        help="Use multi-step reasoning for a complex question",
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
    if args.interactive:
        interactive_reasoning_session()
    elif args.question:
        response = get_reasoning_response(args.question, temperature=args.temperature)
        console.print(Panel(Markdown(response), border_style="green"))
    elif args.chain_of_thought:
        response = chain_of_thought_reasoning(args.chain_of_thought)
        console.print(Panel(Markdown(response), border_style="green"))
    elif args.step_by_step:
        response = get_reasoning_with_steps(
            args.step_by_step, temperature=args.temperature
        )
        console.print(Panel(Markdown(response), border_style="green"))
    elif args.multi_step:
        result = multi_step_reasoning(args.multi_step)
        # Print a formatted version of the multi-step result
        console.print(
            Panel(
                f"[bold]Analysis for:[/bold] {result['original_question']}",
                border_style="blue",
            )
        )
        console.print(
            Panel(
                Markdown(result["decomposition_reasoning"]),
                title="Problem Decomposition",
                border_style="cyan",
            )
        )

        for i, prob in enumerate(result["sub_problems"]):
            console.print(f"[bold]Sub-Problem {i + 1}:[/bold] {prob}")

        for i, sol in enumerate(result["sub_problem_solutions"]):
            console.print(
                Panel(
                    Markdown(sol["solution"]),
                    title=f"Solution to Sub-Problem {i + 1}",
                    border_style="yellow",
                )
            )

        console.print(
            Panel(
                Markdown(result["final_answer"]),
                title="Final Answer",
                border_style="green",
            )
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Application terminated by user.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred:[/bold red] {e}")
