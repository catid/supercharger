import re
import time

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, LlamaTokenizer

from fastchat.conversation import conv_templates, SeparatorStyle

def disable_torch_init():
    """
    Disable the redundant torch default initialization to accelerate model creation.
    """
    setattr(torch.nn.Linear, "reset_parameters", lambda self: None)
    setattr(torch.nn.LayerNorm, "reset_parameters", lambda self: None)

def load_model(model_name, num_gpus):
    disable_torch_init()

    if num_gpus == 1:
        kwargs = {}
    else:
        kwargs = {
            "device_map": "auto",
            "max_memory": {i: "22GiB" for i in range(num_gpus)},
        }

    print(f"Loading model {model_name}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
    model_name, torch_dtype=torch.float16, **kwargs)

    if num_gpus == 1:
        model.cuda()

    if hasattr(model.config, "max_sequence_length"):
        context_len = model.config.max_sequence_length
    else:
        context_len = 2048

    print(f"Loaded model with context length {context_len}")

    return tokenizer, model, context_len

def filter_suggestions(suggestions, confidence_threshold):
    filtered_suggestions = [s for s in suggestions if s[1] >= confidence_threshold]
    return filtered_suggestions

def parse_suggestions(text):
    lines = text.strip().split("\n")
    suggestions = []

    for line in lines:
        # Remove line numbers or other non-alphabetic starting characters
        cleaned_line = re.sub(r"^\W*\d*\W*", "", line)

        # Search for a confidence score (a number between 0 and 1) anywhere on the line
        score_match = re.search(r"([0-9]*\.[0-9]+)", cleaned_line)

        # If a confidence score is found, extract the suggestion text and confidence score
        if score_match:
            confidence_score = float(score_match.group(1))
            if confidence_score >= 0 and confidence_score <= 1:
                suggestions.append((cleaned_line, confidence_score))

    return suggestions

def format_suggestions(suggestions, bullet_character='*'):
    formatted_suggestions = []
    for suggestion in suggestions:
        suggestion_text, confidence_score = suggestion
        formatted_line = f"{bullet_character} {suggestion_text}"
        formatted_suggestions.append(formatted_line)

    return "\n".join(formatted_suggestions)

def parse_confidence_score(text):
    match = re.search(r"\b(0(\.\d{1,})?|1(\.0{1,})?)\b", text)
    if match:
        return float(match.group(0))
    else:
        print(f"Could not parse confidence score from '{text}'")
        return 0.0

def has_system_role(messages):
    for message in messages:
        if message["role"] == "system":
            return True
    return False

def create_conversation_template(messages, separated=True):
    conversation = []

    if not has_system_role(messages):
        template = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant trained to answer questions and provide assistance on various topics."
            },
            {
                "role": "user",
                "content": "What is the capital city of France?"
            },
            {
                "role": "assistant",
                "content": "The capital city of France is Paris."
            },
            {
                "role": "user",
                "content": "Can you help me with a recipe for spaghetti carbonara?"
            },
            {
                "role": "assistant",
                "content": "Of course! Here's a simple recipe for spaghetti carbonara:\n\nIngredients:\n- 400g spaghetti\n- 4 large eggs\n- 100g grated pecorino cheese\n- 150g pancetta, diced\n- Salt and black pepper\n- 2 garlic cloves, minced\n\nInstructions:\n1. Cook the spaghetti in a large pot of boiling salted water until al dente.\n2. While the spaghetti is cooking, whisk the eggs in a bowl with the pecorino cheese"
            }
        ]
        messages = template + messages

    for message in messages:
        role = message["role"]
        content = message["content"]

        if role.capitalize() == "System":
            conversation.append(content)
        else:
            conversation.append(f"{role.capitalize()}: {content}")

        if separated:
            conversation.append("###")

    conversation.append("ASSISTANT:")

    return "\n".join(conversation)

class VicunaModel:
    def __init__(self, model_name, num_gpus=2):
        self.tokenizer, self.model, self.context_len = load_model(model_name, num_gpus)

    # This provides a raw text input to the model, which is not recommended for general queries.
    # Instead, people usually provide a conversation template and a goal prompt.
    @torch.inference_mode()
    def ask_raw(self, prompt, stop_str, temperature=0.7, max_new_tokens=512):
        #print(f"PROMPT: {prompt}")

        l_prompt = len(prompt)
        max_new_tokens = min(max_new_tokens, 1024)

        input_ids = self.tokenizer(prompt).input_ids
        #output_ids = list(input_ids)
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

                pos = output.rfind(stop_str, 0)
                if pos != -1:
                    output = output[:pos]
                    stopped = True
                    break

            if stopped:
                break

        return output

    # This performs the ask using a specified set of conversation messages as in the OpenAI API.
    # It will automatically create a conversation template for you if SYSTEM is not specified.
    def ask_messages(self, messages, temperature=0.7, max_new_tokens=512):
        prompt = create_conversation_template(messages)
        stop_str = "###"

        print(f"PROMPT: {prompt}")

        return self.ask_raw(prompt, stop_str, temperature, max_new_tokens)

    # This uses Vicuna prompt template
    def ask(self, prompt, temperature=0.7, max_new_tokens=512):
        #print(f"PROMPT: {prompt}")

        # Generate a prompt template for a helpful AI
        template_name = "v1"
        state = conv_templates[template_name].copy()
        state.append_message(state.roles[0], prompt)
        state.append_message(state.roles[1], None)
        prompt = state.get_prompt()
        stop_str = state.sep if state.sep_style == SeparatorStyle.SINGLE else state.sep2

        return self.ask_raw(prompt, stop_str, temperature, max_new_tokens)

    def supercharged_ask(self, goal_prompt):
        self.prompt_templates = {
            "analysis": "Prompt: {goal_prompt}\n---\nInitial response:\n---\n{current_response}\n---\nPlease analyze this response and suggest a list of helpful improvements each with an individual confidence score ranging from 0 to 1. Consider aspects like grammar, style, content, context, usefulness, brevity, efficiency, structure, and other potential improvements.",
            "feedback": "Prompt: {goal_prompt}\n---\nInitial response:\n---\n{current_response}\n---\nFeedback:\n---\n{filtered_suggestions}\n---\nPlease think step by step and consider multiple alternatives before incorporating this feedback into the response.",
            "check": "Prompt: {goal_prompt}\n---\nInitial response:\n---\n{current_response}\n---\nRevised response:\n---\n{proposed_response}\n---\nAssign a score to the improvement on a scale from 0 to 1. 0 means the improvement is not helpful at all, 1 means the improvement is perfect."
        }

        initial_response = self.ask(goal_prompt)

        print(f"Initial response: {initial_response}")

        improvement_iteration = 0
        max_iterations = 10
        current_response = initial_response
        confidence_threshold = 0.6
        timeout_seconds = 3000
        start_time = time.time()
        applied_suggestions = {}
        best_response = current_response

        while improvement_iteration < max_iterations:
            if time.time() - start_time > timeout_seconds:
                print(f"Done: Timeout reached")
                break

            print(f"Asking for improvements...")

            analyze_prompt = self.prompt_templates["analysis"].format(goal_prompt=goal_prompt, current_response=current_response)
            analysis_response = self.ask(analyze_prompt)

            suggestions = parse_suggestions(analysis_response)

            # Adapt the confidence threshold based on the quality metric
            filtered_suggestions = filter_suggestions(suggestions, confidence_threshold)

            if not filtered_suggestions:
                print(f"Done: No improvements suggested")
                break

            # Limit the number of times a specific suggestion is applied
            for suggestion in filtered_suggestions:
                suggestion_text = suggestion[0]
                if suggestion_text in applied_suggestions:
                    applied_suggestions[suggestion_text] += 1
                else:
                    applied_suggestions[suggestion_text] = 1

                if applied_suggestions[suggestion_text] >= 3:
                    filtered_suggestions.remove(suggestion)

            if not filtered_suggestions:
                print(f"Done: No new suggestions")
                break

            formatted_suggestions = format_suggestions(filtered_suggestions)

            print(f"Incorporating {len(filtered_suggestions)} suggestions:\n{formatted_suggestions}")

            # Incorporating feedback into the initial response
            feedback_prompt = self.prompt_templates["feedback"].format(
                goal_prompt=goal_prompt,
                current_response=current_response,
                filtered_suggestions=formatted_suggestions)
            proposed_response = self.ask(feedback_prompt)

            print(f"Incorporated feedback: {proposed_response}")

            print(f"Checking that the feedback is an improvement...")

            check_prompt = self.prompt_templates["check"].format(
                goal_prompt=goal_prompt,
                current_response=current_response,
                proposed_response=proposed_response)
            check_response = self.ask(check_prompt, max_new_tokens=64)
            score = parse_confidence_score(check_response)

            if score < confidence_threshold:
                print(f"Done: AI decided its own feedback was not an improvement score={score}")
                break

            print(f"AI decided its own feedback was an improvement score={score}")
            best_response = proposed_response

            improvement_iteration += 1
            if improvement_iteration == max_iterations:
                print(f"Done: Max iterations reached {max_iterations}")

        return best_response
