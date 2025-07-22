#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "python-dotenv",
# ]
# ///

"""
Multi-Agent Observability Hook Script
Sends Claude Code hook events to the observability server.
"""

import json
import sys
import os
import argparse
import urllib.request
import urllib.error
from datetime import datetime
from utils.summarizer import generate_event_summary

def send_event_to_server(event_data, server_url='http://localhost:4000/events', debug=False):
    """Send event data to the observability server."""
    if debug:
        print(f"🔍 Debug: Sending event to {server_url}", file=sys.stderr)
        print(f"🔍 Debug: Event data: {json.dumps(event_data, indent=2)}", file=sys.stderr)
        
    try:
        # Prepare the request
        req = urllib.request.Request(
            server_url,
            data=json.dumps(event_data).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Claude-Code-Hook/1.0'
            }
        )
        
        if debug:
            print(f"🔍 Debug: Request headers: {req.headers}", file=sys.stderr)
        
        # Send the request
        with urllib.request.urlopen(req, timeout=10) as response:
            response_body = response.read().decode('utf-8')
            if debug:
                print(f"🔍 Debug: Response status: {response.status}", file=sys.stderr)
                print(f"🔍 Debug: Response body: {response_body}", file=sys.stderr)
                
            if response.status == 200:
                return True
            else:
                print(f"Server returned status: {response.status}", file=sys.stderr)
                return False
                
    except urllib.error.URLError as e:
        if debug:
            print(f"🔍 Debug: URLError details: {type(e).__name__}: {e}", file=sys.stderr)
        print(f"Failed to send event: {e}", file=sys.stderr)
        return False
    except Exception as e:
        if debug:
            print(f"🔍 Debug: Exception details: {type(e).__name__}: {e}", file=sys.stderr)
        print(f"Unexpected error: {e}", file=sys.stderr)
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Send Claude Code hook events to observability server')
    parser.add_argument('--source-app', required=True, help='Source application name')
    parser.add_argument('--event-type', required=True, help='Hook event type (PreToolUse, PostToolUse, etc.)')
    parser.add_argument('--server-url', default='http://localhost:4000/events', help='Server URL')
    parser.add_argument('--add-chat', action='store_true', help='Include chat transcript if available')
    parser.add_argument('--summarize', action='store_true', help='Generate AI summary of the event')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    if args.debug:
        print(f"🔍 Debug: Arguments: {vars(args)}", file=sys.stderr)
    
    try:
        # Read hook data from stdin
        input_data = json.load(sys.stdin)
        if args.debug:
            print(f"🔍 Debug: Input data: {json.dumps(input_data, indent=2)}", file=sys.stderr)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Prepare event data for server
    event_data = {
        'source_app': args.source_app,
        'session_id': input_data.get('session_id', 'unknown'),
        'hook_event_type': args.event_type,
        'payload': input_data,
        'timestamp': int(datetime.now().timestamp() * 1000)
    }
    
    # Handle --add-chat option
    if args.add_chat and 'transcript_path' in input_data:
        transcript_path = input_data['transcript_path']
        if os.path.exists(transcript_path):
            # Read .jsonl file and convert to JSON array
            chat_data = []
            try:
                with open(transcript_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                chat_data.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass  # Skip invalid lines
                
                # Add chat to event data
                event_data['chat'] = chat_data
            except Exception as e:
                print(f"Failed to read transcript: {e}", file=sys.stderr)
    
    # Generate summary if requested
    if args.summarize:
        summary = generate_event_summary(event_data)
        if summary:
            event_data['summary'] = summary
        # Continue even if summary generation fails
    
    # Send to server
    success = send_event_to_server(event_data, args.server_url, debug=args.debug)
    
    if args.debug:
        print(f"🔍 Debug: Send result: {success}", file=sys.stderr)
    
    # Always exit with 0 to not block Claude Code operations
    sys.exit(0)

if __name__ == '__main__':
    main()