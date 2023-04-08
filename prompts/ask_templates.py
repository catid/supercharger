# Prompt engineering to improve the odds that the LLM produces useful output

def has_system_role(messages):
    for message in messages:
        if message["role"] == "system":
            return True
    return False

def normalize_role(role):
    return f"{role.capitalize()}"

def decorate_role(role):
    return f"[|{normalize_role(role)}|]"

def create_conversation_template(messages, default_template=None, user_role="Human", assistant_role="Assistant"):
    conversation = []

    if not has_system_role(messages) and default_template is not None:
        messages = default_template + messages

    for message in messages:
        role = message["role"]
        content = message["content"]

        if role.capitalize() == "System":
            conversation.append(content)
        else:
            conversation.append(f"{decorate_role(role)}: {content}")

    conversation.append(f"{decorate_role(assistant_role)}:")
    stop_strs = [
        f"{decorate_role(user_role)}:",
        f"{decorate_role(assistant_role)}:"
    ]

    return "\n".join(conversation), stop_strs

# This version has a history for the assistant role
def ask_assistant(messages, user_role="Human", assistant_role="Assistant"):
    template = [
        {
            "role": "System",
            "content": f"The following is a conversation between {normalize_role(user_role)} and {normalize_role(assistant_role)}. {normalize_role(user_role)} and {normalize_role(assistant_role)} take turns chatting. {normalize_role(assistant_role)} is a helpful AI assistant. {normalize_role(assistant_role)} always considers responses carefully and thinks step by step before answering."
        },
        {
            "role": user_role,
            "content": "What is a microorganism?"
        },
        {
            "role": assistant_role,
            "content": """A microorganism, or microbe, is a microscopic living organism that is too small to be seen with the naked eye. Microorganisms can be single-celled, such as bacteria and protozoa, or multi-cellular, like some fungi and algae. They can be found in various environments, including soil, water, air, and inside the bodies of plants and animals.

Microorganisms play vital roles in many ecosystems, such as decomposing organic matter, recycling nutrients, and participating in symbiotic relationships. Some microorganisms can also cause diseases, while others are beneficial to humans and are used in various applications, such as food production (e.g., yogurt, cheese, and bread) and biotechnology (e.g., producing antibiotics, enzymes, and biofuels)."""
        },
        {
            "role": user_role,
            "content": "What's a good way to use a fiber laser?"
        },
        {
            "role": assistant_role,
            "content": """Fiber lasers are versatile tools with many applications across various industries. A good way to use a fiber laser depends on your specific needs and requirements. Some common applications include:

* Material processing: Fiber lasers are widely used for cutting, welding, and drilling materials, especially metals. They offer high precision, speed, and quality, making them ideal for manufacturing processes in the aerospace, automotive, electronics, and medical industries.

* Marking and engraving: Fiber lasers can create high-resolution marks and engravings on a variety of materials such as metals, plastics, ceramics, and glass. This makes them suitable for product identification, traceability, and branding purposes."""
        },
    ]

    return create_conversation_template(template + messages, assistant_role=assistant_role, user_role=user_role)

# This version has a history for python code generation
def ask_python_coder(messages, user_role="Human", assistant_role="Coder"):
    template = [
        {
            "role": "System",
            "content": f"The following is a Python conversation between {normalize_role(user_role)} and {normalize_role(assistant_role)}. {normalize_role(user_role)} and {normalize_role(assistant_role)} take turns chatting. {normalize_role(assistant_role)} always considers responses carefully and thinks step by step before answering. {normalize_role(assistant_role)} always writes syntactically correct Python code."
        },
        {
            "role": user_role,
            "content": "Write a function that adds two numbers."
        },
        {
            "role": assistant_role,
            "content": """```
def add_numbers(x, y):
    return x + y
```"""
        },
        {
            "role": user_role,
            "content": "Write a Python function that checks if a number is even"
        },
        {
            "role": assistant_role,
            "content": """```
def is_even(x):
    return (x%2) == 0
```"""
        },
    ]

    return create_conversation_template(template + messages, assistant_role=assistant_role, user_role=user_role)