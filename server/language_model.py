import logging

import torch
from transformers import LlamaForCausalLM, LlamaTokenizer
from peft import PeftModel


def disable_torch_init():
    """
    Disable the redundant torch default initialization to accelerate model creation.
    """
    setattr(torch.nn.Linear, "reset_parameters", lambda self: None)
    setattr(torch.nn.LayerNorm, "reset_parameters", lambda self: None)

def load_model():
    base_model_name = "decapoda-research/llama-30b-hf"
    peft_model_name = "project-baize/baize-lora-30B"

    disable_torch_init()

    tokenizer = LlamaTokenizer.from_pretrained(base_model_name)

    model = LlamaForCausalLM.from_pretrained(
        base_model_name,
        load_in_8bit=True,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    model = PeftModel.from_pretrained(
        model,
        peft_model_name,
        torch_dtype=torch.float16,
    )

    if hasattr(model.config, "max_sequence_length"):
        context_len = model.config.max_sequence_length
    else:
        context_len = 2048

    logging.info(f"Loaded base_model={base_model_name} enhanced with peft_model={peft_model_name} with context length {context_len}")

    return tokenizer, model, context_len

def is_array_of_strings(input_array):
    if isinstance(input_array, list) and all(isinstance(element, str) for element in input_array):
        return True
    else:
        return False


class LanguageModel:
    def __init__(self):
        self.tokenizer, self.model, self.context_len = load_model()

    @torch.inference_mode()
    def ask(self, prompt, stop_strs=None, temperature=0.7, max_new_tokens=512):
        has_stop_strs = is_array_of_strings(stop_strs)

        max_new_tokens = min(max_new_tokens, 1024)

        input_ids = self.tokenizer(prompt).input_ids
        output_ids = []

        max_src_len = self.context_len - max_new_tokens - 8
        input_ids = input_ids[-max_src_len:]

        output = ""

        for i in range(max_new_tokens):
            if i == 0:
                out = self.model(
                    torch.as_tensor([input_ids]).cuda(), use_cache=True)
                logits = out.logits
                past_key_values = out.past_key_values
            else:
                attention_mask = torch.ones(
                    1, past_key_values[0][0].shape[-2] + 1, device="cuda")
                out = self.model(input_ids=torch.as_tensor([[token]], device="cuda"),
                            use_cache=True,
                            attention_mask=attention_mask,
                            past_key_values=past_key_values)
                logits = out.logits
                past_key_values = out.past_key_values

            last_token_logits = logits[0][-1]
            if temperature < 1e-4:
                token = int(torch.argmax(last_token_logits))
            else:
                probs = torch.softmax(last_token_logits / temperature, dim=-1)
                token = int(torch.multinomial(probs, num_samples=1))

            output_ids.append(token)

            if token == self.tokenizer.eos_token_id:
                stopped = True
            else:
                stopped = False

            if i%2 == 0 or i == max_new_tokens - 1 or stopped:
                output = self.tokenizer.decode(output_ids, skip_special_tokens=True)

                if has_stop_strs:
                    for stop_str in stop_strs:
                        pos = output.rfind(stop_str, 0)
                        if pos > 8:
                            output = output[:pos]
                            stopped = True
                            break

            if stopped:
                break

        return output
