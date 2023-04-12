import argparse
import logging
import asyncio
import time

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

        start_time = time.time()

        response = m.ask(
            prompt,
            stop_strs=stop_strs,
            temperature=temperature,
            max_new_tokens=max_tokens)

        end_time = time.time()
        duration = end_time - start_time

        logger.info(f"Response in {duration} seconds: {response}")

        return {
            'response': response,
            'duration': duration,
        }

    except Exception as e:
        return {'response': f"Exception while processing request: {e}"}

    finally:
        semaphore.release()

def main(args):
    global m
    m = LanguageModel(args.model, load_in_8bit=args.load_in_8bit)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.listen)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supercharged Vicuna-13B")
    parser.add_argument("--listen", type=int, default=5000, help="Port to listen on (default: 5000)")
    parser.add_argument("--model", type=str, help="Select model to use. Available options: baize-30b, baize-13b, baize-7b, galpaca-30b, galpaca-7b, koala-13b, koala-7b, vicuna-13b, vicuna-7b", default="baize-30b")
    parser.add_argument("--8bit", action="store_true", help="Use 8-bit precision (default: False)")
    parser.add_argument("--fp16", action="store_true", help="Use 16-bit precision (default: False)")

    args = parser.parse_args()

    if getattr(args, "8bit"):
        logging.info("8-bit precision selected.")
        args.load_in_8bit = True
    elif args.fp16:
        logging.info("16-bit precision selected.")
        args.load_in_8bit = False
    else:
        args.load_in_8bit = None

    main(args)
