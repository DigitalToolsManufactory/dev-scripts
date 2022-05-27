from unittest import TestCase

from utility.type_utility import get_or_else, get_or_raise


class TestTypeUtility(TestCase):
    def test_get_or_else(self) -> None:
        self.assertEqual(get_or_else("Foo", "Bar"), "Foo")
        self.assertEqual(get_or_else(None, "Bar"), "Bar")
        self.assertEqual(get_or_else(None, lambda: "Bar"), "Bar")

    def test_get_or_raise(self) -> None:
        self.assertEqual(get_or_raise("Foo", Exception("Assertion Error")), "Foo")

        with self.assertRaises(AssertionError):
            get_or_raise(None)

        with self.assertRaises(Exception):
            get_or_raise(None, Exception())

        with self.assertRaises(Exception):
            get_or_raise(None, lambda: Exception())
