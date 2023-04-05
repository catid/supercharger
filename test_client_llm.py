# Example of calling API for load_balancer.py or serve_llm.py

import requests
import argparse

def query_ask_llm(messages, node, node_port=5000, temperature=1.0, max_tokens=100):
    data = {
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
    }

    response = requests.post(f"http://{node}:{node_port}/ask_llm", json=data)
    response_json = response.json()

    return response_json['response']

def main(args):
    messages = [
        {
            "role": "human",
            "content": "What is the best way to make money with a 100W laser cutter?"
        }
    ]
    temperature = 0.8
    max_tokens = 1024
    node = "localhost"
    node_port = args.port

    response = query_ask_llm(messages, node, node_port, temperature=temperature, max_tokens=max_tokens)
    print(response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unit test client for LLM model requests")
    parser.add_argument("--port", type=int, default=5000, help="Server port")

    args = parser.parse_args()

    main(args)
