import argparse
import os
import time
from typing import Optional

import requests
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.batch import Batch

load_dotenv()

openai = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")

# Define file path properly using os.path
current_dir = os.path.dirname(os.path.abspath(__file__))
batch_file_path = os.path.join(current_dir, "batch_img.jsonl")


def check_batch_file_exists() -> bool:
    """Check if batch_img.jsonl file exists"""
    if not os.path.exists(batch_file_path):
        print(f"Error: File not found at {batch_file_path}")
        print(
            "Please create the batch_img.jsonl file in the same directory as this script"
        )
        return False
    return True


def create_batch() -> Optional[Batch]:
    """Create a new batch job using batch_img.jsonl file"""
    if not check_batch_file_exists():
        return None

    try:
        # Upload the input file
        with open(batch_file_path, "rb") as f:
            file = openai.files.create(file=f, purpose="batch")

        print(f"File uploaded successfully. File ID: {file.id}")

        # Create a batch job
        print(f"Creating a batch job with input file ID: {file.id}")
        batch = openai.batches.create(
            input_file_id=file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )

        print(f"Batch created successfully. Batch ID: {batch.id}")
        print(f"Initial status: {batch.status}")

        return batch
    except Exception as e:
        print(f"Error creating batch: {e}")
        return None


def get_batch_status(batch_id: str) -> None:
    """Get status of a specific batch by ID"""
    try:
        batch_status = openai.batches.retrieve(batch_id)
        print(f"\nBatch ID: {batch_status.id}")
        print(f"Status: {batch_status.status}")
        print(f"Created at: {batch_status.created_at}")
        print(
            f"Completed at: {batch_status.completed_at if batch_status.completed_at else 'Not completed yet'}"
        )
        print(
            f"Error rate: {batch_status.error_rate if hasattr(batch_status, 'error_rate') else 'N/A'}"
        )

        # Check if output file is available
        if hasattr(batch_status, "output_file_id") and batch_status.output_file_id:
            print(f"Output file ID: {batch_status.output_file_id}")
            download_output = input("Do you want to download the output file? (y/n): ")
            if download_output.lower() == "y":
                download_batch_output(batch_status.output_file_id, batch_status.id)
        else:
            print("No output file available yet.")
    except Exception as e:
        print(f"Error retrieving batch status: {e}")


def download_batch_output(file_id: str, batch_id: str) -> None:
    """Download batch output file"""
    try:
        output_file = openai.files.retrieve(file_id)

        # Download the file content
        response = requests.get(output_file.url)
        output_filename = f"output_{batch_id}.jsonl"

        with open(output_filename, "wb") as f:
            f.write(response.content)

        print(f"Output downloaded successfully to {output_filename}")
    except Exception as e:
        print(f"Error downloading output: {e}")


def list_batches() -> None:
    """List all batches with their status"""
    try:
        batches = openai.batches.list()
        if not batches.data:
            print("No batches found.")
            return

        print("\nList of batches:")
        print("=" * 80)
        print(f"{'Batch ID':<40} {'Status':<15} {'Created At':<25} {'Completed'}")
        print("-" * 80)

        for batch in batches.data:
            completed = "✓" if batch.completed_at else "-"
            print(
                f"{batch.id:<40} {batch.status:<15} {batch.created_at:<25} {completed}"
            )

        print(
            "\nTo get detailed status of a batch, use: python 12_batches.py status <batch-id>"
        )
    except Exception as e:
        print(f"Error listing batches: {e}")


def process_command(command, batch_id=None, options=None):
    """Process a single command"""
    if options is None:
        options = {}

    # Map numeric commands to string commands
    command_map = {
        "1": "create",
        "2": "list",
        "3": "status",
        "4": "monitor",
        "0": "exit",
    }

    # Convert numeric command to string command if applicable
    if command in command_map:
        command = command_map[command]

    if command == "create":
        batch = create_batch()
        # Ask if user wants to monitor the newly created batch
        if batch and batch.id:
            monitor = input(
                "Do you want to monitor this batch until completion? (y/n): "
            )
            if monitor.lower() == "y":
                interval = input("Check interval in seconds (default: 60): ")
                try:
                    interval = int(interval) if interval.strip() else 60
                except ValueError:
                    interval = 60
                monitor_batch(batch.id, interval)
    elif command == "list":
        list_batches()
    elif command == "status" and batch_id:
        get_batch_status(batch_id)
    elif command == "monitor" and batch_id:
        interval = options.get("interval", 60)
        try:
            interval = int(interval)
        except ValueError:
            interval = 60
        monitor_batch(batch_id, interval)
    elif command == "exit" or command == "quit":
        return False
    else:
        print(
            "Invalid command. Enter a number (1-5) or use 'create', 'list', 'status <batch-id>', 'monitor <batch-id>', 'help', or 'exit'"
        )
    return True


def interactive_mode():
    """Run the application in interactive mode"""
    print("\n==== OpenAI Batch Operations CLI - Interactive Mode ====")
    print("Available commands:")
    print("  1. create                    - Create a new batch job")
    print("  2. list                      - List all batch jobs")
    print("  3. status <batch-id>         - Get status of a specific batch")
    print(
        "  4. monitor <batch-id> [int]  - Monitor batch until completion (optional: interval in seconds)"
    )
    print("  5. help                      - Show this help message")
    print("  0. exit/quit                 - Exit the application")
    print("=" * 70)

    running = True
    while running:
        try:
            user_input = input("\nEnter command: ").strip()

            if user_input.lower() == "help" or user_input == "5":
                print("\nAvailable commands:")
                print("  1. create                    - Create a new batch job")
                print("  2. list                      - List all batch jobs")
                print("  3. status <batch-id>         - Get status of a specific batch")
                print(
                    "  4. monitor <batch-id> [int]  - Monitor batch until completion (optional: interval in seconds)"
                )
                print("  5. help                      - Show this help message")
                print("  0. exit/quit                 - Exit the application")
                continue

            parts = user_input.split()
            if not parts:
                continue

            command = parts[0].lower()
            batch_id = None
            options = {}

            # For numeric inputs that require an additional parameter
            if command == "3" or command == "4":  # status or monitor commands by number
                if len(parts) > 1:
                    batch_id = parts[1]
                else:
                    print(
                        f"Please provide a batch ID for the {'status' if command == '3' else 'monitor'} command"
                    )
                    print(f"Usage: {command} <batch-id>")
                    continue

            # Parse batch_id and options for text-based commands
            elif len(parts) > 1 and (command == "status" or command == "monitor"):
                batch_id = parts[1]

                # For monitor command, get the interval if provided
                if command == "monitor" and len(parts) > 2:
                    try:
                        options["interval"] = int(parts[2])
                    except ValueError:
                        print(
                            "Warning: Invalid interval value. Using default 60 seconds."
                        )
                        options["interval"] = 60

            # For monitor command by number, get the interval if provided
            if command == "4" and len(parts) > 2:
                try:
                    options["interval"] = int(parts[2])
                except ValueError:
                    print("Warning: Invalid interval value. Using default 60 seconds.")
                    options["interval"] = 60

            running = process_command(command, batch_id, options)
        except KeyboardInterrupt:
            print("\nExiting application...")
            break
        except Exception as e:
            print(f"Error processing command: {e}")

    print("Application closed.")


def monitor_batch(batch_id: str, interval: int = 60) -> None:
    """Continuously monitor a batch until it's completed"""
    print(f"\nStarting batch monitor for batch ID: {batch_id}")
    print(f"Checking status every {interval} seconds. Press Ctrl+C to stop monitoring.")

    last_status = None
    try:
        while True:
            batch_status = openai.batches.retrieve(batch_id)
            current_status = batch_status.status

            # Only print if status has changed
            if current_status != last_status:
                print(
                    f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Status: {current_status}"
                )

                if hasattr(batch_status, "error_rate") and batch_status.error_rate:
                    print(f"Error rate: {batch_status.error_rate}")

                if batch_status.completed_at:
                    print(f"Completed at: {batch_status.completed_at}")

                    if (
                        hasattr(batch_status, "output_file_id")
                        and batch_status.output_file_id
                    ):
                        print(f"Output file ID: {batch_status.output_file_id}")
                        download_output = input(
                            "Do you want to download the output file now? (y/n): "
                        )
                        if download_output.lower() == "y":
                            download_batch_output(
                                batch_status.output_file_id, batch_status.id
                            )

                    print("Batch processing completed. Monitoring stopped.")
                    break

                last_status = current_status

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"Error during monitoring: {e}")


def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description="OpenAI Batch Operations CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
When in interactive mode, you can use these numbered commands:
  1. create                    - Create a new batch job
  2. list                      - List all batch jobs
  3. status <batch-id>         - Get status of a specific batch
  4. monitor <batch-id> [int]  - Monitor batch until completion
  5. help                      - Show help message
  0. exit/quit                 - Exit the application
""",
    )

    # Add interactive mode option
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Run in interactive mode"
    )

    # Add daemon mode option for continuous operation
    parser.add_argument(
        "-d",
        "--daemon",
        action="store_true",
        help="Run in daemon mode (starts interactive mode and keeps running)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create command
    subparsers.add_parser("create", help="Create a new batch job")

    # List command
    subparsers.add_parser("list", help="List all batch jobs")

    # Status command
    status_parser = subparsers.add_parser(
        "status", help="Get status of a specific batch"
    )
    status_parser.add_argument("batch_id", help="ID of the batch to check status")

    # Monitor command
    monitor_parser = subparsers.add_parser(
        "monitor", help="Monitor a batch until completion"
    )
    monitor_parser.add_argument("batch_id", help="ID of the batch to monitor")
    monitor_parser.add_argument(
        "--interval",
        "-n",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Run in interactive mode if specified
    if args.interactive or args.daemon:
        interactive_mode()
    # Otherwise, process a single command
    elif args.command == "create":
        batch = create_batch()
        if batch and batch.id:
            print("\nBatch created successfully. You can monitor it with:")
            print(f"python 12_batches.py monitor {batch.id}")
    elif args.command == "list":
        list_batches()
    elif args.command == "status" and args.batch_id:
        get_batch_status(args.batch_id)
    elif args.command == "monitor" and args.batch_id:
        monitor_batch(args.batch_id, args.interval)
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Please try again or check your configuration.")
