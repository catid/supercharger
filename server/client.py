import requests
import time
import logging

# Use ask_templates.py to generate the prompt and stop_strs
def ask_server(prompt, stop_strs=None, node="localhost", port=5000, temperature=1.0, max_tokens=100):
    data = {
        'prompt': prompt,
        'stop_strs': stop_strs,
        'temperature': temperature,
        'max_tokens': max_tokens,
    }

    while True:
        try:
            response = requests.post(f"http://{node}:{port}/ask", json=data)
            response_json = response.json()
            break
        except Exception as e:
            logging.warn(f"Server busy: {e}")
            time.sleep(1)

    return response_json['response']
