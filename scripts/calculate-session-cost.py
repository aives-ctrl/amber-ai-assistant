#!/usr/bin/env python3
"""
Precise session cost calculator for OpenClaw heartbeat monitoring.
Uses configured Anthropic pricing to calculate exact costs from session_status output.
"""

import re
import sys

# Anthropic API pricing (USD per 1M tokens) - March 2026
PRICING = {
    'anthropic/claude-sonnet-4-20250514': {
        'input': 3.0,
        'output': 15.0,
        'cache_read': 0.30,
        'cache_write': 3.75
    },
    'anthropic/claude-opus-4-6': {
        'input': 15.0,
        'output': 75.0,
        'cache_read': 1.50,
        'cache_write': 18.75
    }
}

def parse_session_status(status_output):
    """Parse session_status output to extract token counts and model."""
    # Extract model
    model_match = re.search(r'Model:\s*([^\s]+)', status_output)
    model = model_match.group(1) if model_match else 'unknown'
    
    # Extract tokens: "🧮 Tokens: 173 in / 4.4k out"
    tokens_match = re.search(r'Tokens:\s*([0-9.]+k?)\s*in\s*/\s*([0-9.]+k?)\s*out', status_output)
    if not tokens_match:
        return None, None, None, None
    
    input_str, output_str = tokens_match.groups()
    
    # Convert k notation to numbers  
    def parse_token_count(token_str):
        if 'k' in token_str:
            return float(token_str.replace('k', '')) * 1000
        else:
            return float(token_str)
    
    input_tokens = parse_token_count(input_str)
    output_tokens = parse_token_count(output_str)
    
    return model, input_tokens, output_tokens, status_output

def calculate_cost(model, input_tokens, output_tokens):
    """Calculate precise cost based on model pricing."""
    if model not in PRICING:
        return None, f"Unknown model: {model}"
    
    pricing = PRICING[model]
    
    # Calculate costs (pricing is per 1M tokens)
    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']
    total_cost = input_cost + output_cost
    
    return total_cost, None

def format_cost_report(model, input_tokens, output_tokens, total_cost, context_pct):
    """Format the cost report for heartbeat."""
    # Determine model display name
    model_name = 'Opus' if 'opus' in model.lower() else 'Sonnet'
    
    # Format token counts (show in k for readability)
    input_display = f"{input_tokens/1000:.0f}k" if input_tokens >= 1000 else f"{input_tokens:.0f}"
    output_display = f"{output_tokens/1000:.0f}k" if output_tokens >= 1000 else f"{output_tokens:.0f}"
    
    # Context warning if >80%
    context_warning = " ⚠️ Context high!" if context_pct > 80 else ""
    
    return f"💰 Session: {input_display}in/{output_display}out → ${total_cost:.3f} | {model_name} | {context_pct}% context{context_warning}"

if __name__ == "__main__":
    # Read session_status output from stdin or command line
    if len(sys.argv) > 1:
        status_output = ' '.join(sys.argv[1:])
    else:
        status_output = sys.stdin.read()
    
    model, input_tokens, output_tokens, full_output = parse_session_status(status_output)
    
    if model is None:
        print("Error: Could not parse session_status output")
        sys.exit(1)
    
    total_cost, error = calculate_cost(model, input_tokens, output_tokens)
    
    if error:
        print(f"Error: {error}")
        sys.exit(1)
    
    # Extract context percentage from status output
    context_match = re.search(r'(\d+)k/200k.*\((\d+)%\)', full_output)
    context_pct = int(context_match.group(2)) if context_match else 0
    
    print(format_cost_report(model, input_tokens, output_tokens, total_cost, context_pct))