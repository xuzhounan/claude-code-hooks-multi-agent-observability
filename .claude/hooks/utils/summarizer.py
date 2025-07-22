#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import json
from typing import Optional, Dict, Any
from .llm.anth import prompt_llm


def generate_event_summary(event_data: Dict[str, Any]) -> Optional[str]:
    """
    Generate a concise summary of a hook event for engineers.
    
    For Claude Max users, creates rule-based summaries without API dependency.

    Args:
        event_data: The hook event data containing event_type, payload, etc.

    Returns:
        str: A basic event summary, or None if generation fails
    """
    event_type = event_data.get("hook_event_type", "Unknown")
    payload = event_data.get("payload", {})

    # Rule-based summary generation for Claude Max users
    try:
        if event_type == "PreToolUse":
            tool_name = payload.get("tool_name", "unknown tool")
            return f"About to execute {tool_name}"
        
        elif event_type == "PostToolUse":
            tool_name = payload.get("tool_name", "unknown tool")
            return f"Completed execution of {tool_name}"
        
        elif event_type == "UserPromptSubmit":
            prompt = payload.get("prompt", "")
            if prompt:
                # Get first few words for summary
                words = prompt.split()[:5]
                preview = " ".join(words)
                if len(words) >= 5:
                    preview += "..."
                return f"User prompt: {preview}"
            return "User submitted prompt"
        
        elif event_type == "Notification":
            message = payload.get("message", "")
            if message:
                # Get first few words for summary  
                words = message.split()[:5]
                preview = " ".join(words)
                if len(words) >= 5:
                    preview += "..."
                return f"Notification: {preview}"
            return "System notification"
        
        elif event_type == "Stop":
            return "Task completed"
        
        elif event_type == "SubagentStop":
            return "Sub-agent task completed"
        
        else:
            return f"Hook event: {event_type}"
            
    except Exception:
        return f"Event: {event_type}"
