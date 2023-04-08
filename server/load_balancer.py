import argparse
import asyncio
import random
import requests
import time
import logging

from fastapi import FastAPI, HTTPException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
nodes = []
current_node = 0

@app.post("/ask")
async def ask_endpoint(data):
    global nodes, current_node
    start_time = time.time()
    timeout = 300 # 5 minutes

    while True:
        # Check if we've exceeded the timeout
        if time.time() - start_time > timeout:
            raise HTTPException(status_code=503, detail="All nodes are currently unavailable")

        # Check if we've tried all nodes already
        if current_node >= len(nodes):
            current_node = 0
            await asyncio.sleep(1)

        node_url = f"http://{nodes[current_node]}/ask"
        current_node += 1

        try:
            response = requests.post(node_url, json=data)
            response.raise_for_status()
            logging.info("Completed on {node_url}")
            return response.json()
        except requests.exceptions.RequestException:
            logging.info("Node busy: {node_url}")
            pass

def read_node_addresses():
    try:
        with open("load_balancer_nodes.txt") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        return []

def main():
    parser = argparse.ArgumentParser(description="Load balancer")
    parser.add_argument("--nodes", type=str, nargs="+", help="List of node addresses")
    parser.add_argument("--port", type=int, default=5000, help="Port used by nodes")
    parser.add_argument("--listen", type=int, default=8000, help="Load balancer port")
    args = parser.parse_args()

    global nodes

    if args.nodes is None:
        nodes = read_node_addresses()
        if not nodes:
            raise ValueError("No node addresses found in load_balancer_nodes.txt")
    else:
        nodes = args.nodes

    random.shuffle(nodes)

    # Start the FastAPI server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.listen)

if __name__ == "__main__":
    main()
