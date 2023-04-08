import os
import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    script_path = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(script_path)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
