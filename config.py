"""
Configuration and constants for the Banking AI System
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = 'ap-south-1'
CLAUDE_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

# API Rate Limiting
import time
import asyncio
import json
import re

async def rate_limited_api_call(api_call_func, *args, max_retries=3, base_delay=2.0, **kwargs):
    """Enhanced rate-limited API call with exponential backoff"""
    
    for attempt in range(max_retries + 1):
        try:
            result = api_call_func(*args, **kwargs)
            # Add base delay after successful call
            await asyncio.sleep(1.5)  # Increased base delay
            return result
            
        except Exception as e:
            if "ThrottlingException" in str(e) or "TooManyRequestsException" in str(e):
                if attempt < max_retries:
                    # Exponential backoff: 2s, 4s, 8s, etc.
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limited (attempt {attempt + 1}/{max_retries + 1}), waiting {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"Max retries ({max_retries}) reached for rate limiting")
                    raise e
            else:
                # Non-throttling error, don't retry
                raise e
    
    return None  # Should never reach here

async def bedrock_api_call_with_retry(aws_client, model_id, body, max_retries=3):
    """Dedicated Bedrock API call with retry logic"""
    
    for attempt in range(max_retries + 1):
        try:
            # Add progressive delay before each call
            delay = 1.5 + (attempt * 0.5)  # 1.5s, 2s, 2.5s, 3s
            await asyncio.sleep(delay)
            
            response = aws_client.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            return response
            
        except Exception as e:
            if "ThrottlingException" in str(e) or "TooManyRequestsException" in str(e):
                if attempt < max_retries:
                    # Exponential backoff: 3s, 6s, 12s
                    backoff_delay = 3.0 * (2 ** attempt)
                    logger.warning(f"Bedrock throttled (attempt {attempt + 1}/{max_retries + 1}), backing off {backoff_delay}s...")
                    await asyncio.sleep(backoff_delay)
                    continue
                else:
                    logger.error(f"Bedrock max retries ({max_retries}) reached")
                    raise e
            else:
                # Non-throttling error, don't retry
                raise e
    
    return None

def clean_json_string(json_str: str) -> str:
    """
    Advanced JSON cleaning to handle control characters and formatting issues
    """
    if not json_str:
        return "{}"
    
    # Remove all control characters completely (including \n, \r, \t in strings)
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_str)
    
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Fix common JSON formatting issues
    cleaned = re.sub(r',\s*}', '}', cleaned)  # Remove trailing commas before }
    cleaned = re.sub(r',\s*]', ']', cleaned)  # Remove trailing commas before ]
    cleaned = re.sub(r'}\s*{', '},{', cleaned)  # Fix missing commas between objects
    
    # Handle quotes in strings properly
    cleaned = re.sub(r'(?<!\\)"([^"]*)"(?=\s*:)', r'"\1"', cleaned)  # Fix key quotes
    
    # Ensure proper JSON structure
    cleaned = cleaned.strip()
    
    # Extract JSON object/array from text
    json_start = -1
    json_end = -1
    
    # Find the first complete JSON object or array
    for i, char in enumerate(cleaned):
        if char in '{[':
            json_start = i
            break
    
    if json_start != -1:
        bracket_count = 0
        quote_open = False
        escape_next = False
        start_char = cleaned[json_start]
        end_char = '}' if start_char == '{' else ']'
        
        for i in range(json_start, len(cleaned)):
            char = cleaned[i]
            
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"':
                quote_open = not quote_open
                continue
            
            if not quote_open:
                if char == start_char:
                    bracket_count += 1
                elif char == end_char:
                    bracket_count -= 1
                    if bracket_count == 0:
                        json_end = i
                        break
        
        if json_end > json_start:
            cleaned = cleaned[json_start:json_end + 1]
    
    # Final fallback
    if not cleaned or not (cleaned.startswith('{') or cleaned.startswith('[')):
        cleaned = "{}"
    
    return cleaned

def safe_json_parse(json_str: str, fallback_dict: dict = None) -> dict:
    """
    Safe JSON parsing with multiple fallback strategies
    """
    if fallback_dict is None:
        fallback_dict = {}
    
    try:
        # First attempt: direct parsing
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            # Second attempt: clean and parse
            cleaned = clean_json_string(json_str)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            try:
                # Third attempt: extract JSON from text
                start_idx = json_str.find('{')
                end_idx = json_str.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    extracted = json_str[start_idx:end_idx + 1]
                    cleaned = clean_json_string(extracted)
                    return json.loads(cleaned)
            except:
                pass
            
            # Final fallback - reduce log level to avoid spam
            logger.debug(f"JSON parsing failed, using fallback: {json_str[:100]}...")
            return fallback_dict 