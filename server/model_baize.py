import logging

import torch
from transformers import LlamaForCausalLM, LlamaTokenizer
from peft import PeftModel

from model_tools import disable_torch_init

def load_model_baize(model_name="baize-30b", load_in_8bit=None):
    if model_name == "baize-30b":
        base_model_name = "decapoda-research/llama-30b-hf"
        peft_model_name = "project-baize/baize-lora-30B"
        if load_in_8bit is None:
            load_in_8bit = True # Should fit on two GPUs
    elif model_name == "baize-13b":
        base_model_name = "decapoda-research/llama-13b-hf"
        peft_model_name = "project-baize/baize-lora-13B"
        if load_in_8bit is None:
            load_in_8bit = True # Prefer running on one GPU
    elif model_name == "baize-7b":
        base_model_name = "decapoda-research/llama-7b-hf"
        peft_model_name = "project-baize/baize-lora-7B"
        if load_in_8bit is None:
            load_in_8bit = False # Should fit on one GPU
    else:
        raise Exception("Unknown model_name={model_name}")

    logging.info(f"Loading base_model={base_model_name} load_in_8bit={load_in_8bit} enhanced with peft_model={peft_model_name}...")

    disable_torch_init()

    tokenizer = LlamaTokenizer.from_pretrained(base_model_name)

    model = LlamaForCausalLM.from_pretrained(
        base_model_name,
        load_in_8bit=load_in_8bit,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    model = PeftModel.from_pretrained(
        model,
        peft_model_name,
        torch_dtype=torch.float16,
    )

    if not load_in_8bit:
        model = model.half()
        is_half = True
    else:
        is_half = False

    if hasattr(model.config, "max_sequence_length"):
        context_len = model.config.max_sequence_length
    else:
        context_len = 2048

    logging.info(f"Loaded base_model={base_model_name} load_in_8bit={load_in_8bit} enhanced with peft_model={peft_model_name} with context length {context_len}")

    return tokenizer, model, context_len
