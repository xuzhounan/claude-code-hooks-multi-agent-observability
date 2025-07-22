#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "python-dotenv",
# ]
# ///

"""
Proxy handling utilities for Claude Code hooks.
Automatically bypasses proxy for localhost connections while preserving
proxy settings for external connections.
"""

import urllib.request
import urllib.parse


def create_opener_for_url(url, debug=False):
    """
    Create a urllib opener that handles proxy settings appropriately.
    
    Args:
        url (str): The target URL
        debug (bool): Enable debug output
        
    Returns:
        urllib.request.OpenerDirector: Configured opener
    """
    try:
        parsed_url = urllib.parse.urlparse(url)
        is_localhost = parsed_url.hostname in ['localhost', '127.0.0.1', '::1']
        
        if is_localhost:
            # Create no-proxy handler for localhost
            no_proxy_handler = urllib.request.ProxyHandler({
                'http': None,
                'https': None
            })
            opener = urllib.request.build_opener(no_proxy_handler)
            if debug:
                print(f"🔍 Debug: Bypassing proxy for localhost connection to {parsed_url.hostname}")
        else:
            # Use default proxy settings for external connections
            opener = urllib.request.build_opener()
            if debug:
                print(f"🔍 Debug: Using system proxy settings for external connection to {parsed_url.hostname}")
        
        return opener
        
    except Exception as e:
        if debug:
            print(f"🔍 Debug: Error creating opener, using default: {e}")
        # Fallback to default opener
        return urllib.request.build_opener()


def make_request(url, data=None, headers=None, method='GET', timeout=10, debug=False):
    """
    Make an HTTP request with proper proxy handling.
    
    Args:
        url (str): Target URL
        data (bytes, optional): Request data for POST requests
        headers (dict, optional): Request headers
        method (str): HTTP method
        timeout (int): Request timeout in seconds
        debug (bool): Enable debug output
        
    Returns:
        tuple: (status_code, response_body, success)
    """
    try:
        # Create appropriate opener
        opener = create_opener_for_url(url, debug=debug)
        
        # Prepare headers
        if headers is None:
            headers = {}
        
        # Create request
        req = urllib.request.Request(url, data=data, headers=headers)
        req.get_method = lambda: method
        
        if debug:
            print(f"🔍 Debug: Making {method} request to {url}")
            if headers:
                print(f"🔍 Debug: Headers: {headers}")
            if data:
                print(f"🔍 Debug: Data length: {len(data)} bytes")
        
        # Make request
        with opener.open(req, timeout=timeout) as response:
            try:
                response_data = response.read()
                response_body = response_data.decode('utf-8') if response_data else ""
            except Exception as decode_error:
                if debug:
                    print(f"🔍 Debug: Failed to decode response: {decode_error}")
                response_body = ""
                
            status_code = response.status if hasattr(response, 'status') else response.getcode()
            
            if debug:
                print(f"🔍 Debug: Response status: {status_code}")
                print(f"🔍 Debug: Response body: {response_body}")
            
            return status_code, response_body, True
            
    except urllib.error.HTTPError as e:
        try:
            error_data = e.read() if hasattr(e, 'read') else None
            error_body = error_data.decode('utf-8') if error_data else str(e)
        except Exception:
            error_body = str(e)
        if debug:
            print(f"🔍 Debug: HTTP Error {e.code}: {error_body}")
        return e.code, error_body, False
        
    except urllib.error.URLError as e:
        if debug:
            print(f"🔍 Debug: URL Error: {e}")
        return 0, str(e), False
        
    except Exception as e:
        if debug:
            print(f"🔍 Debug: Unexpected error: {e}")
        return 0, str(e), False


def send_json_event(url, event_data, timeout=10, debug=False):
    """
    Send a JSON event to a server with proper proxy handling.
    
    Args:
        url (str): Target URL  
        event_data (dict): Event data to send
        timeout (int): Request timeout
        debug (bool): Enable debug output
        
    Returns:
        bool: True if successful, False otherwise
    """
    import json
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Claude-Code-Hook/1.0'
    }
    
    data = json.dumps(event_data).encode('utf-8')
    
    status_code, response_body, success = make_request(
        url=url,
        data=data, 
        headers=headers,
        method='POST',
        timeout=timeout,
        debug=debug
    )
    
    return success and status_code == 200