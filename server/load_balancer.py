import argparse
import asyncio
import random
import time
import logging

import aiohttp
from fastapi import FastAPI, HTTPException, Request

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
nodes = []
busy_nodes = set()

async def fetch_node_data(session: aiohttp.ClientSession, url: str, data) -> dict:
    async with session.post(url, json=data) as response:
        response.raise_for_status()
        return await response.json()

@app.post("/ask")
async def ask_endpoint(request: Request):
    data = await request.json()

    start_time = time.time()

    global nodes, busy_nodes

    for node in nodes:
        if node in busy_nodes:
            continue

        node_url = f"http://{node}/ask"

        try:
            busy_nodes.add(node)

            logging.info(f"Trying on {node_url}")
            try_start_time = time.time()

            async with aiohttp.ClientSession() as session:
                response_data = await fetch_node_data(session, node_url, data)

            logging.info(f"Completed on {node_url} in {time.time() - try_start_time:.2f} seconds (overall delay: {time.time() - start_time:.2f} seconds)")
            return response_data
        except (aiohttp.ClientError, aiohttp.ClientResponseError):
            logging.info(f"Node unreachable: {node_url}")
            pass
        finally:
            busy_nodes.remove(node)

    raise HTTPException(status_code=503, detail="All nodes are currently unavailable")

def read_node_addresses(filename="load_balancer_nodes.txt"):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
    return lines

def main():
    parser = argparse.ArgumentParser(description="Load balancer")
    parser.add_argument("--nodes", type=str, nargs="+", help="List of node addresses")
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
