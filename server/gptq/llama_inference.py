import torch
import torch.nn as nn

from gptq import *
from modelutils import *
from quantize_module import *

from transformers import AutoTokenizer

def load_quant(model, checkpoint, wbits, groupsize, device, warmup_autotune = True):
    from transformers import LlamaConfig, LlamaForCausalLM 
    config = LlamaConfig.from_pretrained(model)
    def noop(*args, **kwargs):
        pass
    torch.nn.init.kaiming_uniform_ = noop 
    torch.nn.init.uniform_ = noop 
    torch.nn.init.normal_ = noop 

    torch.set_default_dtype(torch.half)
    transformers.modeling_utils._init_weights = False
    torch.set_default_dtype(torch.half)
    model = LlamaForCausalLM(config)
    torch.set_default_dtype(torch.float)
    model = model.eval()
    layers = find_layers(model)
    for name in ['lm_head']:
        if name in layers:
            del layers[name]
    make_quant(model, layers, wbits, groupsize)

    print('Loading model ...')
    if checkpoint.endswith('.safetensors'):
        from safetensors.torch import load_file as safe_load
        if device == -1:
            device = "cpu"
        model.load_state_dict(safe_load(checkpoint, device))
    else:
        model.load_state_dict(torch.load(checkpoint))
        
    make_quant_attn(model)

    if warmup_autotune:
        autotune_warmup(model)
    model.seqlen = 2048
    print('Done.')

    return model
