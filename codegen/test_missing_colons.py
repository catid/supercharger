import ast
import unittest
from fix_ast_errors import fix_ast_errors

class TestAddMissingColons(unittest.TestCase):
    def check_syntax(self, code_string):
        try:
            ast.parse(code_string)
            return True
        except SyntaxError:
            return False

    def run_test_cases(self, test_cases, test_type, syntax_check=True):
        for i, (input_str, expected_output) in enumerate(test_cases):
            with self.subTest(input=input_str, expected=expected_output, test_type=test_type):
                fixed_code = fix_ast_errors(input_str)
                self.assertEqual(fixed_code, expected_output, msg=f"\n\nFailed test {i} in {test_type}. Expected output:\n\n{expected_output}\n\nGot:\n\n{fixed_code}\n\n")
                if syntax_check:
                    self.assertTrue(self.check_syntax(fixed_code), msg=f"\n\nFailed test {i} in {test_type}. Syntax checker found a problem with the output: {fixed_code}")

    def test_basic_cases(self):
        test_cases = [
            ("def foo(x)\n    pass", "def foo(x):\n    pass"),
            ("if x > 0\n    pass\nelif x < 0\n    pass", "if x > 0:\n    pass\nelif x < 0:\n    pass"),
            ("if x > 0\n    pass\nelse\n    pass", "if x > 0:\n    pass\nelse:\n    pass"),
            ("for i in range(10)\n    pass", "for i in range(10):\n    pass"),
            ("while True\n    pass", "while True:\n    pass"),
            ("with open('file.txt') as f\n    pass", "with open('file.txt') as f:\n    pass"),
            ("class MyClass\n    def f():\n        pass", "class MyClass:\n    def f():\n        pass"),
            ("print(f\"The area of a circle with radius {radius} is {area:.2f}\")", "print(f\"The area of a circle with radius {radius} is {area:.2f}\")")
        ]

        self.run_test_cases(test_cases, "Basic", syntax_check=False)

    def test_single_line(self):
        test_cases = [
            ("x = 1\n", "x = 1\n"),
            ("def func(x):\n    pass\n", "def func(x):\n    pass\n"),
            ("if x == 2\n    print(x)\n", "if x == 2:\n    print(x)\n"),
            ("for i in range(10)\n    print(i)\n", "for i in range(10):\n    print(i)\n"),
            ("while x < 10\n    x += 1\n", "while x < 10:\n    x += 1\n"),
        ]

        self.run_test_cases(test_cases, "Single-Line")

    def test_multi_line(self):
        test_cases = [
            ("if x == 2\n    print(x)\nelse:\n    print('Error')\n", "if x == 2:\n    print(x)\nelse:\n    print('Error')\n"),
            ('if x > 0: print("x is positive")\nif y < 0: print("y is negative")\n', 'if x > 0: print("x is positive")\nif y < 0: print("y is negative")\n'),
            ("for i in range(10)\n    if i % 2 == 0:\n        print(i)\n", "for i in range(10):\n    if i % 2 == 0:\n        print(i)\n"),
            ("with open('file.txt') as f\n    data = f.read()\n    print(data)\n", "with open('file.txt') as f:\n    data = f.read()\n    print(data)\n")
        ]

        self.run_test_cases(test_cases, "Multi-Line")

if __name__ == "__main__":
    unittest.main()
