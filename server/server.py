import argparse
import logging
import asyncio

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from language_model import LanguageModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
semaphore = asyncio.Semaphore(1)

class AskData(BaseModel):
    prompt: str
    stop_strs: Optional[List[str]] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512

@app.post("/ask")
async def ask_endpoint(data: AskData):
    try:
        # Attempt to acquire the semaphore without waiting
        await asyncio.wait_for(semaphore.acquire(), timeout=0.1)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=503, detail="Server is busy, please try again later")

    # Process the input with semaphore held
    try:
        prompt = data.prompt
        stop_strs = data.stop_strs
        temperature = data.temperature
        max_tokens = data.max_tokens

        logger.info(f"Asking: {prompt}")
        logger.info(f"Stop strings: {stop_strs}")

        response = m.ask(
            prompt,
            stop_strs=stop_strs,
            temperature=temperature,
            max_new_tokens=max_tokens)

        logger.info(f"Response: {response}")

        return {'response': response}

    except Exception as e:
        return {'response': f"Exception while processing request: {e}"}

    finally:
        semaphore.release()

def main(args):
    global m
    m = LanguageModel()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.listen)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supercharged Vicuna-13B")
    parser.add_argument("--listen", type=int, default=5000, help="Port to listen on (default: 5000)")

    args = parser.parse_args()

    main(args)
