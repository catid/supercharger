import logging

import torch
from transformers import LlamaTokenizer, LlamaForCausalLM

from model_tools import disable_torch_init

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_model_koala(model_name="koala-13b", load_in_8bit=None):
    if model_name == "koala-13b":
        base_model_name = "TheBloke/koala-13B-HF"
        if load_in_8bit is None:
            load_in_8bit = True # Should fit on one GPU
    elif model_name == "koala-7b":
        base_model_name = "TheBloke/koala-7B-HF"
        if load_in_8bit is None:
            load_in_8bit = False # Should fit on one GPU
        raise Exception("Koala-7B model appears to be broken")
    else:
        raise Exception("Unknown model_name={model_name}")

    logging.info(f"Loading base_model={base_model_name} load_in_8bit={load_in_8bit}...")

    disable_torch_init()

    tokenizer = LlamaTokenizer.from_pretrained(base_model_name)
    model = LlamaForCausalLM.from_pretrained(
        base_model_name,
        device_map="auto",
        torch_dtype=torch.float16,
        load_in_8bit=load_in_8bit,
    )

    if hasattr(model.config, "max_sequence_length"):
        context_len = model.config.max_sequence_length
    else:
        context_len = 2048

    logging.info(f"Loaded base_model={base_model_name} load_in_8bit={load_in_8bit} with context length {context_len}")

    return tokenizer, model, context_len
