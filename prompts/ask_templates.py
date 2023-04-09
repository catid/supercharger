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

def create_conversation_template(messages, default_template=None, custom_start="", user_role="Human", assistant_role="Assistant"):
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

    if len(custom_start) > 0:
        conversation.append(f"{decorate_role(assistant_role)}: {custom_start}")
    else:
        conversation.append(f"{decorate_role(assistant_role)}:")

    stop_strs = [
        f"{decorate_role(user_role)}:",
        f"{decorate_role(assistant_role)}:"
    ]

    return "\n".join(conversation), stop_strs

# This version has a history for the assistant role
def ask_assistant(messages, user_role="Human", assistant_role="Assistant"):
    user_role, assistant_role = normalize_role(user_role), normalize_role(assistant_role)
    template = [
        {
            "role": "System",
            "content": f"The following is a conversation between {user_role} and {assistant_role}. {user_role} and {assistant_role} take turns chatting. {assistant_role} is a helpful AI assistant. {assistant_role} always considers responses carefully and thinks step by step before answering."
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
    user_role, assistant_role = normalize_role(user_role), normalize_role(assistant_role)
    template = [
        {
            "role": "System",
            "content": f"The following is a Python conversation between {user_role} and {assistant_role}. {user_role} and {assistant_role} take turns chatting. {assistant_role} always considers responses carefully and thinks step by step before answering. {assistant_role} always writes syntactically correct Python code."
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

# Generate a python function with a specific prototype
def ask_python_function_prototype(comments, prototype, user_role="Human", assistant_role="Coder"):
    user_role, assistant_role = normalize_role(user_role), normalize_role(assistant_role)
    messages = [
        {
            "role": "system",
            "content": f"The following is a conversation between {user_role} and {assistant_role}. {user_role} and {assistant_role} take turns chatting. {assistant_role} always considers responses carefully and thinks step by step before answering. {assistant_role} always writes syntactically correct Python code."
        },
        {
            "role": user_role,
            "content": "# Add two numbers and return their sum\ndef add_nums(x, y)"
        },
        {
            "role": assistant_role,
            "content": """```
def add_nums(x, y):
    return x + y
```"""
        },
        {
            "role": user_role,
            "content": "# Write a function that multiplies two floats\ndef mul_nums(a, b)"
        },
        {
            "role": assistant_role,
            "content": """```
def mul_nums(x: float, y: float) -> float:
    return x * y
```"""
        },
        {
            "role": user_role,
            "content": "# A function that checks if an integer is prime\n# Returns true or false\ndef is_prime(n)"
        },
        {
            "role": assistant_role,
            "content": """```
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
```"""
        },
        {
            "role": user_role,
            "content": f"{comments}\n{prototype}"
        },
    ]

    return create_conversation_template(messages, assistant_role=assistant_role, user_role=user_role)

# Generate a python unit test for a function with a specific prototype
def ask_python_pytest_prototype(comments, prototype, user_role="Human", assistant_role="Coder"):
    user_role, assistant_role = normalize_role(user_role), normalize_role(assistant_role)
    messages = [
        {
            "role": "system",
            "content": f"The following is a conversation between {user_role} and {assistant_role}. {user_role} and {assistant_role} take turns chatting. {assistant_role} always considers responses carefully and thinks step by step before answering with a Python program using pytest to exercise the given function. {assistant_role} always writes syntactically correct Python code using pytest."
        },
        {
            "role": user_role,
            "content": "# Add two numbers and return their sum\ndef add_nums(x, y):"
        },
        {
            "role": assistant_role,
            "content": """```
import pytest
from add_nums import add_nums

def test_add_nums_positive():
    # Test case 1: adding two positive numbers
    result = add_nums(2, 3)
    assert result == 5

def test_add_nums_negative():
    # Test case 2: adding two negative numbers
    result = add_nums(-2, -3)
    assert result == -5

def test_add_nums_mixed():
    # Test case 3: adding a positive and a negative number
    result = add_nums(2, -3)
    assert result == -1
```"""
        },
        {
            "role": user_role,
            "content": "# A function that checks if an integer is prime\n# Returns true or false\ndef is_prime(n):"
        },
        {
            "role": assistant_role,
            "content": """```
import pytest
from is_prime import is_prime

def test_is_prime():
    assert is_prime(2) == True
    assert is_prime(3) == True
    assert is_prime(4) == False
    assert is_prime(5) == True
    assert is_prime(6) == False
    assert is_prime(7) == True
    assert is_prime(8) == False
    assert is_prime(9) == False
    assert is_prime(10) == False
```"""
        },
        {
            "role": user_role,
            "content": f"{comments}\n{prototype}"
        },
    ]

    return create_conversation_template(messages, assistant_role=assistant_role, user_role=user_role)

# This version has a history for python code analysis and improvement
def ask_python_analyzer(code, user_role="Human", assistant_role="Analyst"):
    user_role, assistant_role = normalize_role(user_role), normalize_role(assistant_role)
    messages = [
        {
            "role": "System",
            "content": f"The following is a Python conversation between {user_role} and {assistant_role}. {user_role} and {assistant_role} take turns chatting. {assistant_role} always considers the previous query carefully and summarizes before responding. {assistant_role} always provides valid Python code with improvements over the original."
        },
        {
            "role": user_role,
            "content": """Please analyze the following code and suggest a fixed or improved version of the code:
```python
# Add two numbers and return their sum
def add_numbers(x, y):
    return x + y * 2
```"""
        },
        {
            "role": assistant_role,
            "content": """It seems like there's a mistake in the given code. The code defines a function add_numbers(x, y) that takes two arguments, x and y. The function is supposed to add the two numbers and return their sum. However, the current implementation returns x plus two times y (i.e., x + 2*y), which is incorrect for the intended purpose.

Here's the corrected version of the code:
```python
# Add two numbers and return their sum
def add_numbers(x, y):
    return x + y
```

Now, the function add_numbers(x, y) correctly adds x and y together and returns the sum.
"""
        },
        {
            "role": user_role,
            "content": """Please analyze the following code and suggest a fixed or improved version of the code:
```python
# A function that checks if an integer is prime
# Returns true or false
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.4) + 1):
        if n % i == 0:
            return False
    return True
```"""
        },
        {
            "role": assistant_role,
            "content": """The given code is intended to check if a number is prime. However, there's a mistake in the loop range. It uses n ** 0.4 instead of n ** 0.5 (square root of n) as the upper limit. Here's a fixed and improved version of the code:

Here's the corrected version of the code:
```python
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
```

In this version, the function correctly checks for prime numbers by iterating up to the square root of n. This is an optimized approach since any factor larger than the square root would have a corresponding factor smaller than the square root, so it's not necessary to check beyond that point.
"""
        },
        {
            "role": user_role,
            "content": f"""Please analyze the following code and suggest a fixed or improved version of the code:
```python
{code}
```"""
        },
    ]

    return create_conversation_template(messages, assistant_role=assistant_role, user_role=user_role)

# This version has a history for python test code analysis and improvement
def ask_python_test_analyzer(comments, prototype, function_name, test_code, user_role="Human", assistant_role="Analyst"):
    user_role, assistant_role = normalize_role(user_role), normalize_role(assistant_role)
    messages = [
        {
            "role": "System",
            "content": f"The following is a Python conversation between {user_role} and {assistant_role}. {user_role} and {assistant_role} take turns chatting. {assistant_role} always considers the previous query carefully and summarizes before responding. {assistant_role} always provides valid pytest Python code with improvements over the original."
        },
        {
            "role": user_role,
            "content": """Given description and prototype of add_nums function to test:
```
# Add two numbers and return their sum
def add_nums(x, y):
```

Please analyze the following pytest code and suggest a fixed version of the pytest code that covers more scenarios:
```python
import pytest
from add_nums import add_nums

def test_add_nums_positive():
    # Test case 1: adding two positive numbers
    result = add_nums(2, 3)
    assert result == 6

def test_add_nums_negative():
    # Test case 2: adding two negative numbers
    result = add_nums(-2, -3)
    assert result == -5

def test_add_nums_mixed():
    # Test case 3: adding a positive and a negative number
    result = add_nums(2, -3)
    assert result == -1
```"""
        },
        {
            "role": assistant_role,
            "content": """The given pytest code has a minor issue in the first test case, where it asserts the result to be 6 instead of 5. Also, it's a good idea to add more test cases to cover additional scenarios. Here's a fixed and improved version of the pytest code:
```python
import pytest
from add_nums import add_nums

def test_add_nums_positive():
    # Test case 1: adding two positive numbers
    result = add_nums(2, 3)
    assert result == 5

def test_add_nums_negative():
    # Test case 2: adding two negative numbers
    result = add_nums(-2, -3)
    assert result == -5

def test_add_nums_mixed():
    # Test case 3: adding a positive and a negative number
    result = add_nums(2, -3)
    assert result == -1

def test_add_nums_zero():
    # Test case 4: adding zero to a positive number
    result = add_nums(0, 3)
    assert result == 3

    # Test case 5: adding zero to a negative number
    result = add_nums(0, -3)
    assert result == -3

    # Test case 6: adding two zeros
    result = add_nums(0, 0)
    assert result == 0

def test_add_nums_large():
    # Test case 7: adding large numbers
    result = add_nums(100000, 200000)
    assert result == 300000

```

Now, the function add_numbers(x, y) correctly adds x and y together and returns the sum.
"""
        },
        {
            "role": user_role,
            "content": f"""Given description and prototype of {function_name} function to test:
```python
{comments}
{prototype}
```

Please analyze the following pytest code and suggest a fixed version of the pytest code that covers more scenarios:
```python
{test_code}
```"""
        },
    ]

    return create_conversation_template(messages, assistant_role=assistant_role, user_role=user_role)

# This version ranks the quality of python code
def ask_python_code_judge(commented_code, function_name, user_role="Human", assistant_role="Judge"):
    user_role, assistant_role = normalize_role(user_role), normalize_role(assistant_role)
    messages = [
        {
            "role": "System",
            "content": f"The following is a Python conversation between {user_role} and {assistant_role}. {user_role} and {assistant_role} take turns chatting. {assistant_role} always considers the previous query carefully. {assistant_role} always provides an expert rating from 0 to 1 of the provided Python code."
        },
        {
            "role": user_role,
            "content": """Please rank the following add_nums function from 0 to 1, where 0 means the code is not good and 1 means the code is good:
```
# Add two numbers and return their sum
def add_nums(x, y):
    return x + y
```"""
        },
        {
            "role": assistant_role,
            "content": """After careful consideration, I would rate the given add_nums function as 0.9. The code is simple, clean, and easy to understand. It performs the expected operation of adding two numbers together and returning their sum. However, the function could be improved with better documentation (for example, specifying input types and return type in a docstring)."""
        },
        {
            "role": user_role,
            "content": f"""Please rank the following {function_name} function from 0 to 1, where 0 means the code is not good and 1 means the code is good:
```python
{commented_code}
```"""
        },
    ]

    custom_start = f"After careful consideration, I would rate the given {function_name} function as "

    return create_conversation_template(messages, custom_start=custom_start, assistant_role=assistant_role, user_role=user_role)

# This version ranks the quality of python test code
def ask_python_test_judge(commented_code, function_name, test_code, user_role="Human", assistant_role="Judge"):
    user_role, assistant_role = normalize_role(user_role), normalize_role(assistant_role)
    messages = [
        {
            "role": "System",
            "content": f"The following is a Python conversation between {user_role} and {assistant_role}. {user_role} and {assistant_role} take turns chatting. {assistant_role} always considers the previous query carefully. {assistant_role} always provides an expert rating from 0 to 1 of the provided Python code."
        },
        {
            "role": user_role,
            "content": """Given the add_nums function:
```
# Add two numbers and return their sum
def add_nums(x, y):
    return x + y
```

Please rank the following unit test code from 0 to 1, where 0 means the code is not good and 1 means the code is good:
```python
import pytest
from add_nums import add_nums

def test_add_nums_positive():
    # Test case 1: adding two positive numbers
    result = add_nums(2, 3)
    assert result == 6

def test_add_nums_negative():
    # Test case 2: adding two negative numbers
    result = add_nums(-2, -3)
    assert result == -5

def test_add_nums_mixed():
    # Test case 3: adding a positive and a negative number
    result = add_nums(2, -3)
    assert result == -1
```"""
        },
        {
            "role": assistant_role,
            "content": """After careful consideration, I would rank the given unit test code as 0.75 out of 1. The test cases cover different scenarios (adding two positive numbers, two negative numbers, and a positive and a negative number), which is good. However, there's an error in the first test case:
```python
def test_add_nums_positive():
    # Test case 1: adding two positive numbers
    result = add_nums(2, 3)
    assert result == 6
```
The assertion should be assert result == 5 instead of assert result == 6. The correct version would be:
```python
def test_add_nums_positive():
    # Test case 1: adding two positive numbers
    result = add_nums(2, 3)
    assert result == 5
```
After fixing this issue, the test code would be ranked as 1 out of 1, since it would be fully correct.
"""
        },
        {
            "role": user_role,
            "content": f"""Given the {function_name} function:
```python
{commented_code}
```

Please rank the following unit test code from 0 to 1, where 0 means the code is not good and 1 means the code is good:
```python
{test_code}
```"""
        },
    ]

    custom_start = "After careful consideration, I would rank the given unit test code as "

    return create_conversation_template(messages, custom_start=custom_start, assistant_role=assistant_role, user_role=user_role)
