import unittest

from fix_indentation_errors import fix_indentation_errors


class TestFixIndentationErrors(unittest.TestCase):

    test_cases = [
        {
            'code_with_errors': """
    def my_function():
    print("Hello, world!")
            """,
            'expected_output': """
def my_function():
    print("Hello, world!")
            """
        },
        {
            'code_with_errors': """
    if x > 0:
    print("x is positive")
            """,
            'expected_output': """
if x > 0:
    print("x is positive")
            """
        },
        {
            'code_with_errors': """
    for i in range(10):
    print(i)
            """,
            'expected_output': """
for i in range(10):
    print(i)
            """
        },
        {
            'code_with_errors': """
    try:
    result = 1 / 0
    except ZeroDivisionError:
    print("Cannot divide by zero!")
            """,
            'expected_output': """
try:
    result = 1 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
            """
        },
        {
            'code_with_errors': """
    if x > 0:
        print("x is positive")
    else:
    print("x is non-positive")
            """,
            'expected_output': """
if x > 0:
    print("x is positive")
else:
    print("x is non-positive")
            """
        },
        {
            'code_with_errors': """
    def my_function(x, y):
        if x > 0:
        return x + y
        else:
        return y - x
            """,
            'expected_output': """
def my_function(x, y):
    if x > 0:
        return x + y
    else:
        return y - x
            """
        },
    ]

    def test_fix_indentation(self):
        for index, test_case in enumerate(self.test_cases):
            with self.subTest(f"Test case {index}"):
                input_code = test_case['code_with_errors']
                expected_output = test_case['expected_output'].strip()
                actual_output = fix_indentation_errors(input_code).strip()
                msg = f"\nInput code:\n---\n{input_code}\n---\n\nExpected output:\n---\n{expected_output}\n---\nActual output:\n---\n{actual_output}\n---"
                self.assertEqual(actual_output, expected_output, msg=msg)

if __name__ == '__main__':
    unittest.main()
