# Use modules from parent folder
import os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import time
import logging
import argparse
from language_model import LanguageModel
from prompts.ask_templates import ask_assistant, ask_python_coder

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model(m, prompt, stop_strs):
    start_time = time.time()
    r = m.ask(
        prompt=prompt,
        stop_strs=stop_strs,
        temperature=args.temperature,
        max_new_tokens=args.max_tokens)
    end_time = time.time()
    elapsed_time = end_time - start_time
    response_length = len(r)
    chars_per_second = response_length / elapsed_time

    logging.info(f"Response:\n\n{r}")
    logging.info(f"Elapsed time: {elapsed_time:.2f} seconds")
    logging.info(f"Characters per second: {chars_per_second:.2f}")

    return r, elapsed_time

def main(args):
    m = LanguageModel(args.model, load_in_8bit=args.load_in_8bit)

    # Test ask_assistant

    messages = [
        {
            "role": "Human",
            "content": "What is the best way to make money with a 100W laser cutter?"
        }
    ]

    prompt, stop_strs = ask_assistant(messages)
    logging.info(f"Testing ask_assistant:\n\n{prompt}")
    logging.info(f"Early stop strings: {stop_strs}")

    r, elapsed_time = test_model(m, prompt, stop_strs)


    # Test ask_python_coder

    messages = [
        {
            "role": "Human",
            "content": "Write a Python function that returns the factorial of a number."
        }
    ]

    prompt, stop_strs = ask_python_coder(messages)
    logging.info(f"\n\nTesting ask_python_coder: {prompt}")
    logging.info(f"Early stop strings: {stop_strs}\n\n")

    r, elapsed_time = test_model(m, prompt, stop_strs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unit test for BaizeModel")
    parser.add_argument("--temperature", type=float, help="Temperature for text generation (default: 0.7)", default=0.7)
    parser.add_argument("--max-tokens", type=int, help="Maximum number of tokens in generated text (default: 1024)", default=1024)
    parser.add_argument("--model", type=str, help="Select model to use (default: galpaca-30b). Available options: baize-30b, baize-13b, baize-7b, galpaca-30b, galpaca-7b", default="galpaca-30b")
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
