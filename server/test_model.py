# Use modules from parent folder
import os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import argparse
from language_model import LanguageModel
from prompts.ask_templates import ask_assistant, ask_python_coder

def main(args):
    m = LanguageModel()

    # Test ask_assistant

    messages = [
        {
            "role": "Human",
            "content": "What is the best way to make money with a 100W laser cutter?"
        }
    ]

    prompt, stop_strs = ask_assistant(messages)
    print(f"\n\nTesting ask_assistant: {prompt}")
    print(f"Early stop strings: {stop_strs}\n\n")

    r = m.ask(
        prompt=prompt,
        stop_strs=stop_strs,
        temperature=args.temperature,
        max_new_tokens=args.max_tokens)
    print(r)

    # Test ask_python_coder

    messages = [
        {
            "role": "Human",
            "content": "Write a Python function that returns the factorial of a number."
        }
    ]

    prompt, stop_strs = ask_python_coder(messages)
    print(f"\n\nTesting ask_python_coder: {prompt}")
    print(f"Early stop strings: {stop_strs}\n\n")

    r = m.ask(
        prompt=prompt,
        stop_strs=stop_strs,
        temperature=args.temperature,
        max_new_tokens=args.max_tokens)
    print(r)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unit test for BaizeModel")
    parser.add_argument("--temperature", type=float, help="Temperature for text generation (default: 0.7)", default=0.7)
    parser.add_argument("--max-tokens", type=int, help="Maximum number of tokens in generated text (default: 1024)", default=1024)

    args = parser.parse_args()

    main(args)
