import re
from unittest import TestCase

from __test__.shell.mock.mock_shell import MockShell, StringMatcher, MockShellResponse
from shell.shell_response import ShellResponse


class TestMockShell(TestCase):

    def test_run_any_command_without_arguments(self) -> None:
        mock: MockShell = MockShell()

        mock.when_command(StringMatcher.any()).then_return(MockShellResponse.of_success("Succeeded!"))

        result: ShellResponse = mock.run("echo", ["Hello, World!"])

        self.assertEqual(result.command_line, "echo \"Hello, World!\"")
        self.assertTrue(result.is_success)
        self.assertEqual(result.stdout, "Succeeded!")
        self.assertEqual(result.stderr, "")

    def test_run_command_without_arguments(self) -> None:
        mock: MockShell = MockShell()

        mock.when_command(StringMatcher.exact("echo")).then_return(MockShellResponse.of_success("Succeeded!"))

        result: ShellResponse = mock.run("echo", ["Hello, World!"])

        self.assertEqual(result.command_line, "echo \"Hello, World!\"")
        self.assertTrue(result.is_success)
        self.assertEqual(result.stdout, "Succeeded!")
        self.assertEqual(result.stderr, "")

    def test_run_any_command_with_arguments(self) -> None:
        mock: MockShell = MockShell()

        mock.when_command(StringMatcher.any()) \
            .has_argument(StringMatcher.contains_exact("Hello, World!")) \
            .then_return(MockShellResponse.of_success("Succeeded!"))

        result: ShellResponse = mock.run("echo", ["Hello, World!"])

        self.assertEqual(result.command_line, "echo \"Hello, World!\"")
        self.assertTrue(result.is_success)
        self.assertEqual(result.stdout, "Succeeded!")
        self.assertEqual(result.stderr, "")

    def test_run_command_with_arguments(self) -> None:
        mock: MockShell = MockShell()

        mock.when_command(StringMatcher.exact("echo")) \
            .has_argument(StringMatcher.contains_exact("Hello, World!")) \
            .then_return(MockShellResponse.of_success("Succeeded!"))

        result: ShellResponse = mock.run("echo", ["Hello, World!"])

        self.assertEqual(result.command_line, "echo \"Hello, World!\"")
        self.assertTrue(result.is_success)
        self.assertEqual(result.stdout, "Succeeded!")
        self.assertEqual(result.stderr, "")

    def test_run_without_matching_rule(self) -> None:
        mock: MockShell = MockShell()

        with self.assertRaises(AssertionError):
            mock.run("echo", ["Hello, World!"])

    def test_run_rules_match_in_order(self) -> None:
        first_mock: MockShell = MockShell()

        first_mock.when_command(StringMatcher.any()).then_return(MockShellResponse.of_success("Generic!"))
        first_mock.when_command(StringMatcher.exact("echo")) \
            .has_argument(StringMatcher.contains_exact("Hello, World!")) \
            .then_return(MockShellResponse.of_success("Specific!"))

        first_result: ShellResponse = first_mock.run("echo", ["Hello, World!"])

        self.assertEqual(first_result.command_line, "echo \"Hello, World!\"")
        self.assertTrue(first_result.is_success)
        self.assertEqual(first_result.stdout, "Generic!")
        self.assertEqual(first_result.stderr, "")

        # change the order of rules
        second_mock: MockShell = MockShell()

        second_mock.when_command(StringMatcher.exact("echo")) \
            .has_argument(StringMatcher.contains_exact("Hello, World!")) \
            .then_return(MockShellResponse.of_success("Specific!"))
        second_mock.when_command(StringMatcher.any()).then_return(MockShellResponse.of_success("Generic!"))

        second_result: ShellResponse = second_mock.run("echo", ["Hello, World!"])

        self.assertEqual(second_result.command_line, "echo \"Hello, World!\"")
        self.assertTrue(second_result.is_success)
        self.assertEqual(second_result.stdout, "Specific!")
        self.assertEqual(second_result.stderr, "")
