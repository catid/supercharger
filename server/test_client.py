# Use modules from parent folder
import os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import argparse

from prompts.ask_templates import ask_assistant, ask_python_coder
from client import ask_server

def main(args):
    messages = [
        {
            "role": "Human",
            "content": "Why is the sky blue?"
        }
    ]

    prompt, stop_strs = ask_assistant(messages)
    print(f"\n\nTesting ask_assistant: {prompt}")
    print(f"Early stop strings: {stop_strs}\n\n")

    r = ask_server(
        prompt=prompt,
        stop_strs=stop_strs,
        node=args.node,
        port=args.port,
        temperature=args.temperature,
        max_tokens=args.max_tokens)
    print(r)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unit test client for LLM model requests")
    parser.add_argument("--node", type=str, default="localhost", help="Server port")
    parser.add_argument("--port", type=int, default=5000, help="Server port")
    parser.add_argument("--temperature", type=float, help="Temperature for text generation (default: 0.7)", default=0.7)
    parser.add_argument("--max-tokens", type=int, help="Maximum number of tokens in generated text (default: 1024)", default=1024)

    args = parser.parse_args()

    main(args)
