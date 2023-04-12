import torch

from model_baize import load_model_baize
from model_galpaca import load_model_galpaca
from model_koala import load_model_koala

def is_array_of_strings(input_array):
    if isinstance(input_array, list) and all(isinstance(element, str) for element in input_array):
        return True
    else:
        return False

class LanguageModel:
    def __init__(self, model_name="baize-30b", load_in_8bit=True):
        if "baize" in model_name:
            self.tokenizer, self.model, self.context_len = load_model_baize(model_name, load_in_8bit)
        elif "galpaca" in model_name:
            self.tokenizer, self.model, self.context_len = load_model_galpaca(model_name, load_in_8bit)
        elif "koala" in model_name:
            self.tokenizer, self.model, self.context_len = load_model_koala(model_name, load_in_8bit)
        else:
            raise Exception(f"Unknown model_name={model_name}")

    @torch.inference_mode()
    def ask(self, prompt, stop_strs=None, temperature=0.7, max_new_tokens=512):
        has_stop_strs = is_array_of_strings(stop_strs)

        max_new_tokens = min(max_new_tokens, 1024)

        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
        output_ids = []

        max_src_len = self.context_len - max_new_tokens - 8
        input_ids = input_ids[-max_src_len:]

        output = ""

        with torch.no_grad():
            for i in range(max_new_tokens):
                if i == 0:
                    input_tensor = input_ids.cuda()
                    out = self.model(input_tensor, use_cache=True)
                    logits = out.logits
                    past_key_values = out.past_key_values
                else:
                    input_tensor = torch.as_tensor([[token]], device="cuda")
                    attention_mask = torch.ones(
                        1, past_key_values[0][0].shape[-2] + 1, device="cuda")
                    out = self.model(input_ids=input_tensor,
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

        torch.cuda.empty_cache()

        return output
