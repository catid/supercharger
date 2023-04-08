import unittest
import ast
from fix_mismatched_delimiters import fix_mismatched_delimiters

class TestFixMismatchedDelimiters(unittest.TestCase):
    def check_syntax(self, code_string):
        try:
            ast.parse(code_string)
            return True
        except SyntaxError:
            return False

    def run_test_cases(self, test_cases, test_type):
        for i, (input_str, expected_output) in enumerate(test_cases):
            with self.subTest(input=input_str, expected=expected_output, test_type=test_type):
                fixed_code = fix_mismatched_delimiters(input_str)
                self.assertEqual(fixed_code, expected_output, msg=f"\n\nFailed test {i} in {test_type}. Expected output:\n\n{expected_output}\n\nGot:\n\n{fixed_code}\n\n")
                self.assertTrue(self.check_syntax(fixed_code), msg=f"\n\nFailed test {i} in {test_type}. Syntax checker found a problem with the output: {fixed_code}")

    def test_basic_cases(self):
        test_cases = [
            ("print(x[1, 2, 3]", "print(x[1, 2, 3])"),
            ("if x == 2: {print(x)", "if x == 2: {print(x)}"),
            ("print(x}", "print(x)"),
            ("{print(x[1, 2, 3]", "{print(x[1, 2, 3])}"),
        ]

        self.run_test_cases(test_cases, "Basic")

    def test_nested_delimiters(self):
        test_cases = [
            ("print(x[1, 2, [3, 4], 5]", "print(x[1, 2, [3, 4], 5])"),
            ("print({1, 2, {3, 4}, 5]", "print({1, 2, {3, 4}, 5})"),
            ("print(x(1, 2, (3, 4), 5)", "print(x(1, 2, (3, 4), 5))"),
            ("{[(print(1))]}", "{[(print(1))]}"),
        ]

        self.run_test_cases(test_cases, "Nested Delimiters")

    def test_comments_and_strings(self):
        test_cases = [
            ('print("hello) world")', 'print("hello) world")'),
            ('print("hello[ world")', 'print("hello[ world")'),
            ("# Some comment (unclosed", "# Some comment (unclosed"),
            ("'''Triple quotes { } ( ) [ ]'''", "'''Triple quotes { } ( ) [ ]'''"),
        ]

        self.run_test_cases(test_cases, "Comments and strings")

    def test_multiline_cases(self):
        test_cases = [
            (
                "if x > 2:\n    print(x[1, 2, 3]\nelse:\n    print('Error')",
                "if x > 2:\n    print(x[1, 2, 3])\nelse:\n    print('Error')"
            ),
            (
                "def func(a, b):\n    return a * (b - 1\n\nprint(func(2, 3)",
                "def func(a, b):\n    return a * (b - 1)\n\nprint(func(2, 3))"
            ),
            (
                "try:\n    x = {'key': 'value'}\n    print(x['key'\nexcept KeyError:\n    print('Key not found')",
                "try:\n    x = {'key': 'value'}\n    print(x['key'])\nexcept KeyError:\n    print('Key not found')"
            ),
            (
                "for i in range(5):\n    if i % 2 == 0:\n        print('{Even}')",
                "for i in range(5):\n    if i % 2 == 0:\n        print('{Even}')"
            ),
            (
                "if x > 2:\n    print(x[1, 2, 3]\nelse:\n    print('Error')",
                "if x > 2:\n    print(x[1, 2, 3])\nelse:\n    print('Error')"
            ),
            (
                "if x == 2:\n    print(\"Hello, World!\"\nelse:\n    print(\"Goodbye, World!\")",
                "if x == 2:\n    print(\"Hello, World!\")\nelse:\n    print(\"Goodbye, World!\")"
            ),
        ]

        self.run_test_cases(test_cases, "Multi-line Cases")

if __name__ == "__main__":
    unittest.main()
