import os
import logging

import torch
from transformers import AutoTokenizer, LlamaForCausalLM

from  gptq import load_quant

import accelerate

from model_tools import disable_torch_init

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_model_llama(model_name="llama-65b-4bit", load_in_8bit=None):
    if model_name == "llama-65b-4bit":
        #model_path = "catid/llama-65b-4bit"
        model_path = "/home/catid/models/llama-65b-4bit"
        model_load = os.path.join(model_path, "llama65b-4bit-128g.safetensors")
        wbits = 4
        groupsize = 128
    else:
        raise Exception("Unknown model_name={model_name}")

    logging.info(f"Loading base_model={model_path}...")

    disable_torch_init()

    model = load_quant(model_path, model_load, wbits, groupsize, -1)
    max_memory = accelerate.utils.get_balanced_memory(model)
    device_map = accelerate.infer_auto_device_map(model, max_memory=max_memory, no_split_module_classes=["LlamaDecoderLayer"])
    logging.info(f"Using the following device map for the quantized model: {device_map}")
    model = accelerate.dispatch_model(model, device_map=device_map, offload_buffers=True)

    tokenizer = AutoTokenizer.from_pretrained(model_path)

    if hasattr(model.config, "max_sequence_length"):
        context_len = model.config.max_sequence_length
    else:
        context_len = 2048

    logging.info(f"Loaded base_model={model_path} load_in_8bit={load_in_8bit} with context length {context_len}")

    return tokenizer, model, context_len
