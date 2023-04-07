import requests

# If you are running the load balancer use 8000 here else use 5000.
# I'm using 4 workers so it's set to 8000 for my purposes.

def ask_llm(messages, node_port=8000, temperature=1.0, max_tokens=100):
    data = {
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
    }

    response = requests.post(f"http://localhost:{node_port}/ask_llm", json=data)
    response_json = response.json()

    return response_json['response']
