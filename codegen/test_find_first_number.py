import unittest
from autopy import find_first_number_between_0_and_1

class TestFindFirstNumberBetween0And1(unittest.TestCase):

    def test_corner_cases(self):
        self.assertEqual(find_first_number_between_0_and_1("0"), 0)
        self.assertEqual(find_first_number_between_0_and_1("1"), 1)
        self.assertEqual(find_first_number_between_0_and_1("0.0"), 0.0)
        self.assertEqual(find_first_number_between_0_and_1("1.0"), 1.0)
        self.assertEqual(find_first_number_between_0_and_1("1.00"), 1.0)
        self.assertIsNone(find_first_number_between_0_and_1("1.1"))

    def test_whitespace_and_punctuation(self):
        self.assertEqual(find_first_number_between_0_and_1(" 0 "), 0)
        self.assertEqual(find_first_number_between_0_and_1("is 0."), 0)
        self.assertEqual(find_first_number_between_0_and_1("is 1."), 1)
        self.assertEqual(find_first_number_between_0_and_1("is 0.75."), 0.75)
        self.assertEqual(find_first_number_between_0_and_1(",0,"), 0)
        self.assertEqual(find_first_number_between_0_and_1("(1)"), 1)

    def test_embedded_numbers(self):
        self.assertEqual(find_first_number_between_0_and_1("abc0.5def"), 0.5)
        self.assertEqual(find_first_number_between_0_and_1("abc1.0def"), 1.0)
        self.assertEqual(find_first_number_between_0_and_1("abc0.0def"), 0.0)

    def test_multiple_numbers(self):
        self.assertEqual(find_first_number_between_0_and_1("0.4 0.7 1.0"), 0.4)
        self.assertEqual(find_first_number_between_0_and_1("0.45 0.7 0.1"), 0.45)
        self.assertEqual(find_first_number_between_0_and_1("1.0 0.7 0.4"), 1.0)

    def test_negative_numbers(self):
        self.assertEqual(find_first_number_between_0_and_1("-0.5 0.6"), 0.6)
        self.assertEqual(find_first_number_between_0_and_1("-1.0 1.0"), 1.0)
        self.assertIsNone(find_first_number_between_0_and_1("-1.0 -0.1"))

    def test_no_match(self):
        self.assertIsNone(find_first_number_between_0_and_1("2 3 4"))
        self.assertIsNone(find_first_number_between_0_and_1("abc"))
        self.assertIsNone(find_first_number_between_0_and_1(""))

if __name__ == '__main__':
    unittest.main()
