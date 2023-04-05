import argparse
from pathlib import Path

from vicuna_model import VicunaModel

def main(args):
    m = VicunaModel(args.model, args.num_gpus)

    goal_prompt = "Why is the sky blue?"

    print(f"User prompt: {goal_prompt}")

    best_result = m.supercharged_ask(goal_prompt)

    print(f"Best result: {best_result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supercharged Vicuna-13B")
    parser.add_argument("--model", type=str, default=str(Path.home() / "vicuna-13b"), help="Path to the model directory (default: ~/vicuna-13b/)")
    parser.add_argument("--num-gpus", type=int, default=2, help="Number of GPUs to use for model parallelism (default: 2)")

    args = parser.parse_args()

    main(args)
