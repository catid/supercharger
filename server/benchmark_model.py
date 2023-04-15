# Use modules from parent folder
import os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import time
import logging
import argparse
from language_model import LanguageModel
from prompts.ask_templates import ask_assistant, ask_python_coder, ask_python_function_prototype, ask_python_analyzer, ask_python_code_judge

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model(m, prompt, stop_strs, max_tokens, temperature):
    start_time = time.time()

    r = m.ask(
        prompt=prompt,
        stop_strs=stop_strs,
        temperature=temperature,
        max_new_tokens=max_tokens)

    end_time = time.time()
    duration = end_time - start_time

    prompt_length = len(prompt)
    response_length = len(r)
    response_chars_per_second = response_length / duration

    logging.info(f"Response:\n\n{r}")
    logging.info(f"Prompt length: {prompt_length} characters")
    logging.info(f"Response length: {response_length} characters. Characters per second: {response_chars_per_second:.2f}. Time: {duration:.2f} seconds")

def main(args):
    start_time = time.time()
    m = LanguageModel(args.model, load_in_8bit=args.load_in_8bit)
    end_time = time.time()
    logging.info(f"Model loaded in {end_time - start_time:.2f} seconds")

    # Test ask_assistant

    messages = [
        {
            "role": "Human",
            "content": "What is the best way to make money with a 100W laser cutter?"
        }
    ]

    prompt, stop_strs = ask_assistant(messages)
    #logging.info(f"Testing ask_assistant:\n\n{prompt}")
    #logging.info(f"Early stop strings: {stop_strs}")

    test_model(m, prompt, stop_strs, max_tokens=args.max_tokens, temperature=args.temperature)

    # Test ask_python_coder

    messages = [
        {
            "role": "Human",
            "content": "Write a Python function that returns the factorial of a number."
        }
    ]

    prompt, stop_strs = ask_python_coder(messages)
    #logging.info(f"\n\nTesting ask_python_coder: {prompt}")
    #logging.info(f"Early stop strings: {stop_strs}\n\n")

    test_model(m, prompt, stop_strs, max_tokens=args.max_tokens, temperature=args.temperature)

    # Test ask_python_function_prototype

    prompt, stop_strs = ask_python_function_prototype("# Returns the factorial of n", "def factorial(n):")
    #logging.info(f"\n\nTesting ask_python_function_prototype: {prompt}")
    #logging.info(f"Early stop strings: {stop_strs}\n\n")

    test_model(m, prompt, stop_strs, max_tokens=args.max_tokens, temperature=args.temperature)

    # Test ask_python_analyzer

    prompt, stop_strs = ask_python_analyzer("# Returns the factorial of n\ndef factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n - 1)")
    #logging.info(f"\n\nTesting ask_python_analyzer: {prompt}")
    #logging.info(f"Early stop strings: {stop_strs}\n\n")

    test_model(m, prompt, stop_strs, max_tokens=args.max_tokens, temperature=args.temperature)

    # Test ask_python_code_judge

    prompt, stop_strs = ask_python_code_judge("# Returns the factorial of n\ndef factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n - 1)", "factorial")
    #logging.info(f"\n\nTesting ask_python_code_judge: {prompt}")
    #logging.info(f"Early stop strings: {stop_strs}\n\n")

    test_model(m, prompt, stop_strs, max_tokens=4, temperature=args.temperature)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unit test for BaizeModel")
    parser.add_argument("--temperature", type=float, help="Temperature for text generation (default: 0.0)", default=0.0)
    parser.add_argument("--max-tokens", type=int, help="Maximum number of tokens in generated text (default: 1024)", default=1024)
    parser.add_argument("--model", type=str, help="Select model to use (default: galpaca-30b). Available options: baize-30b, baize-13b, baize-7b, galpaca-30b, galpaca-7b, koala-13b, koala-7b, vicuna-13b, vicuna-7b, llama-65b-4bit", default="llama-65b-4bit")
    parser.add_argument("--8bit", action="store_true", help="Use 8-bit precision (default: False)")
    parser.add_argument("--fp16", action="store_true", help="Use 16-bit precision (default: False)")

    args = parser.parse_args()

    if getattr(args, "8bit"):
        logging.info("8-bit precision selected.")
        args.load_in_8bit = True
    elif args.fp16:
        logging.info("16-bit precision selected.")
        args.load_in_8bit = False
    else:
        args.load_in_8bit = None

    main(args)
