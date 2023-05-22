import unittest
from lib import fizzbuzz, get_fizz_buzz


class TestFizzBuzz(unittest.TestCase):
    def test_no_fizzbuzz(self):
        self.assertEqual(fizzbuzz(2), "2")

    def test_fizz(self):
        self.assertEqual(fizzbuzz(3), "fizz")

    def test_buzz(self):
        self.assertEqual(fizzbuzz(5), "buzz")

    def test_fizzbuzz(self):
        self.assertEqual(fizzbuzz(15), "fizzbuzz")

    def test_zero(self):
        self.assertEqual(fizzbuzz(0), "0")


if __name__ == "__main__":
    unittest.main()
