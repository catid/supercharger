import requests
import json

def query_ask_llm(messages, node, node_port=5000, temperature=1.0, max_tokens=100):
    data = {
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
    }

    response = requests.post(f"http://{node}:{node_port}/ask_llm", json=data)
    response_json = response.json()

    return response_json['response']

if __name__ == '__main__':
    messages = [
        {
            "role": "user",
            "content": "What is the best way to make money with a 100W laser cutter?"
        }
    ]
    temperature = 0.8
    max_tokens = 1024
    node = "gpu3.lan"

    response = query_ask_llm(messages, node, temperature=temperature, max_tokens=max_tokens)
    print(response)
