import unittest

from extract_code_from_md import extract_code_from_md

class TestExtractCodeFromMd(unittest.TestCase):
    def test_extract_code_from_md(self):
        input_text = """
        # Example Markdown Document

        This is an example Markdown document.

```python
def add(x, y):
    return x + y
```

        Here is some text that follows the code block.

```python
def multiply(x, y):
    return x * y
```
"""

        expected_output = """
def add(x, y):
    return x + y
"""
        self.assertEqual(extract_code_from_md(input_text), expected_output.strip(), msg=f"Input:\n{input_text}\n\nExpected:\n{expected_output.strip()}\n\nActual:\n{extract_code_from_md(input_text)}")

if __name__ == '__main__':
    unittest.main()
