#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import os
import sys
from dotenv import load_dotenv


def prompt_llm(prompt_text):
    """
    Placeholder LLM prompting method for Claude Max users (no API key needed).
    
    Since Claude Max users don't have API keys, this function returns None
    to gracefully handle the absence of LLM completion features.

    Args:
        prompt_text (str): The prompt to send to the model

    Returns:
        str: Always returns None for Claude Max users
    """
    # Claude Max users don't need API keys, so we gracefully disable LLM features
    return None


def generate_completion_message():
    """
    Generate a completion message for Claude Max users (without API dependency).

    Returns:
        str: A predefined completion message
    """
    import random
    
    engineer_name = os.getenv("ENGINEER_NAME", "").strip()

    if engineer_name:
        personalized_messages = [
            f"{engineer_name}, all set!",
            f"Ready for you, {engineer_name}!",
            f"Complete, {engineer_name}!",
            f"{engineer_name}, we're done!",
            f"Task finished, {engineer_name}!",
            f"Ready for next move, {engineer_name}!"
        ]
        standard_messages = [
            "Work complete!",
            "All done!",
            "Task finished!",
            "Ready for your next move!",
            "Mission accomplished!",
            "Good to go!"
        ]
        # 30% chance for personalized, 70% for standard
        if random.random() < 0.3:
            return random.choice(personalized_messages)
        else:
            return random.choice(standard_messages)
    else:
        standard_messages = [
            "Work complete!",
            "All done!",
            "Task finished!",
            "Ready for your next move!",
            "Mission accomplished!",
            "Good to go!",
            "Task complete!",
            "Ready!"
        ]
        return random.choice(standard_messages)


def main():
    """Command line interface for testing."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--completion":
            message = generate_completion_message()
            if message:
                print(message)
            else:
                print("Error generating completion message")
        else:
            prompt_text = " ".join(sys.argv[1:])
            response = prompt_llm(prompt_text)
            if response:
                print(response)
            else:
                print("LLM features disabled for Claude Max users (no API key required)")
    else:
        print("Usage: ./anth.py 'your prompt here' or ./anth.py --completion")


if __name__ == "__main__":
    main()
