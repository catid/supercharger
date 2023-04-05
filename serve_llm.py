import argparse
from pathlib import Path

from flask import Flask, request, jsonify

from vicuna_model import VicunaModel

def create_app(m):
    app = Flask(__name__)

    @app.route('/ask_llm', methods=['POST'])
    def ask_llm_endpoint():
        data = request.json
        messages = data['messages']
        temperature = float(data.get('temperature', 0.7))
        max_tokens = int(data.get('max_tokens', 512))

        print(f"\n\nMESSAGES: {messages}")

        response = m.ask_messages(messages, temperature=temperature, max_new_tokens=max_tokens)

        print(f"\n\nRESPONSE: {response}")

        return jsonify({'response': response})

    return app

def main(args):
    m = VicunaModel(args.model, args.num_gpus)

    app = create_app(m)

    app.run(host='0.0.0.0', port=args.port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supercharged Vicuna-13B")
    parser.add_argument("--model", type=str, default=str(Path.home() / "vicuna-13b"), help="Path to the model directory (default: ~/vicuna-13b/)")
    parser.add_argument("--num-gpus", type=int, default=2, help="Number of GPUs to use for model parallelism (default: 2)")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")

    args = parser.parse_args()

    main(args)
