import ast
import unittest

from fix_ast_errors import fix_ast_errors


class TestFixIndentationErrors(unittest.TestCase):

    test_cases = [
        """
def my_function():
    message = '''
        This is a multi-line string.
        It can span multiple lines.
        '''
    print(message)
        """,
        """
def my_function():
    message = '''
        This is a multi-line string.
        It can span multiple lines.
        '''
    print(message)
        """,
        """
    def my_function():
    print("Hello, world!")
        """,
        """
def my_function():
    print("Hello, world!")
        """,
        """
    if x > 0:
    print("x is positive")
        """,
        """
if x > 0:
    print("x is positive")
        """,
        """
    for i in range(10):
    print(i)
        """,
        """
for i in range(10):
    print(i)
        """,
        """
    try:
    result = 1 / 0
    except ZeroDivisionError:
    print("Cannot divide by zero!")
        """,
        """
try:
    result = 1 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
        """,
        """
    if x > 0:
        print("x is positive")
    else:
    print("x is non-positive")
        """,
        """
if x > 0:
    print("x is positive")
else:
    print("x is non-positive")
        """,
        """
    def my_function(x, y):
        if x > 0:
        return x + y
        else:
        return y - x
        """,
        """
def my_function(x, y):
    if x > 0:
        return x + y
    else:
        return y - x
        """,
        """
    def my_function(x, y):
        if x > 0:
        return x + y
        else:
        return y - x
        """,
        """
def my_function(x, y):
    if x > 0:
        return x + y
    else:
        return y - x
        """,
        """
    def my_function(x, \\
        y):
        if x > 0:
        return x + y
        else:
        return y - x
        """,
        """
def my_function(x, \\
y):
    if x > 0:
        return x + y
    else:
        return y - x
        """,
        """
    def my_function(x,
                    y):
        if x > 0:
        return x + y
        else:
        return y - x
            """,
            """
def my_function(x,
    y):
    if x > 0:
        return x + y
    else:
        return y - x
        """,
        "def main():\n"
        "\tprint('Hello, World!')\n"
        "\t\tif True:\n"
        "\t\t\tprint('This is indented with tabs.')\n"
        "main()",
        "def main():\n"
        "    print('Hello, World!')\n"
        "    if True:\n"
        "        print('This is indented with tabs.')\n"
        "main()",
        "def main():\n"
        "\tprint('Hello, World!')\n"
        "\t\tif True:\n"
        "\t\t\tprint('This is indented with tabs.')\n"
        "\tprint('Hello, World!')\n"
        "main()",
        "def main():\n"
        "    print('Hello, World!')\n"
        "    if True:\n"
        "        print('This is indented with tabs.')\n"
        "    print('Hello, World!')\n"
        "main()",
        "def main():\n"
        "print('Hello, World!')\n"
        "if True:\n"
        "if True:\n"
        "print('This line should be indented.')\n"
        "main()",
        "def main():\n"
        "    print('Hello, World!')\n"
        "if True:\n"
        "    if True:\n"
        "        print('This line should be indented.')\n"
        "main()"
    ]

    def test_fix_indentation(self):
        for index, code in enumerate(self.test_cases):
            with self.subTest(f"Test case {index}"):
                fixed_code = fix_ast_errors(code.strip())
                try:
                    ast.parse(fixed_code)
                except Exception as e:
                    self.fail(f"Test case {index}: Syntax error in fixed code\n"
                              f"Input code:\n---\n{code}\n---\n"
                              f"Fixed code:\n---\n{fixed_code}\n---\n"
                              f"Error: {str(e)}")

if __name__ == '__main__':
    unittest.main()
