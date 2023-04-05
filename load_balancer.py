# Allow you to load-balance requests to a cluster of machines running the server.

# Edit these for your setup
worker_nodes = [
    "http://gpu3.lan:5000",
    "http://gpu4.lan:5000",
    "http://gpu5.lan:5000",
    "http://gpu6.lan:5000",
]

from flask import Flask, request, jsonify
import requests
from multiprocessing import Queue
import logging

app = Flask(__name__)

free_nodes = Queue()
for node in worker_nodes:
    free_nodes.put(node)

@app.route('/ask_llm', methods=['POST'])
def ask_llm_endpoint():
    data = request.json

    node = free_nodes.get()

    response = {'response': None}

    try:
        app.logger.info(f"Sending request to {node}")
        response = requests.post(f"{node}/ask_llm", json=data)
        response = response.json()
    except (requests.exceptions.RequestException, KeyError) as e:
        # Handle the error, retry or reschedule the request, etc.
        app.logger.info(f"Handled exception {e}")
        pass
    finally:
        app.logger.info(f"Put {node} back on free list")
        free_nodes.put(node)

    return jsonify(response)

if __name__ == '__main__':
    app.logger.setLevel(logging.INFO)
    app.run(host='0.0.0.0', port=8000)
