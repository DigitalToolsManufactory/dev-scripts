from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from __test__.string_matcher import StringMatcher
from shell.shell import Shell
from shell.shell_response import ShellResponse


@dataclass(frozen=True)
class MockShellResponse:
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""

    @staticmethod
    def of_success(stdout: str) -> "MockShellResponse":
        return MockShellResponse(0, stdout, "")

    @staticmethod
    def of_error(stderr: str) -> "MockShellResponse":
        return MockShellResponse(1, "", stderr)

    def to_shell_response(self, command_line: str) -> ShellResponse:
        return ShellResponse(command_line, self.exit_code, self.stdout, self.stderr)


@dataclass(frozen=True)
class MockShellInvocation:
    command: str
    arguments: Optional[str] = None
    working_directory: Optional[Path] = None

    def get_command_line(self) -> str:
        return (
            self.command + f" {self.arguments}"
            if self.arguments is not None and len(self.arguments) > 0
            else ""
        )


@dataclass(frozen=True)
class MockShellInvocationMatcher:
    command_matcher: Optional[StringMatcher] = None
    argument_matchers: Optional[List[StringMatcher]] = None

    def matches(self, invocation: MockShellInvocation) -> bool:
        result: bool = True

        if self.command_matcher is not None:
            result &= self.command_matcher.matches(invocation.command)

        if self.argument_matchers is not None:
            for argument_matcher in self.argument_matchers:
                result &= argument_matcher.matches(invocation.arguments)

        return result


@dataclass(frozen=True)
class MockShellRule:
    invocation_matcher: MockShellInvocationMatcher
    response: MockShellResponse

    def matches(self, invocation: MockShellInvocation) -> bool:
        return self.invocation_matcher.matches(invocation)

    def get_shell_response(self, command_line: str) -> ShellResponse:
        return self.response.to_shell_response(command_line)


class MockShell(Shell):
    def __init__(self):
        self._mock_rules: List[MockShellRule] = []

    def run(
        self,
        command: str,
        arguments: Optional[List[str]] = None,
        working_directory: Optional[Path] = None,
    ) -> ShellResponse:
        invocation: MockShellInvocation = MockShellInvocation(
            command, self._combine_arguments(arguments), working_directory
        )
        for rule in self._mock_rules:
            if rule.matches(invocation):
                return rule.get_shell_response(invocation.get_command_line())

        raise AssertionError(
            f"No rule specified that matches following command line: {invocation.get_command_line()}"
        )

    def _combine_arguments(self, arguments: List[str]) -> str:
        return " ".join(
            f'"{argument.strip()}"' if " " in argument else argument.strip()
            for argument in arguments
            if len(argument.strip()) > 0
        )

    # region MockRule builder
    def when_command(
        self, command_matcher: StringMatcher
    ) -> "MockShell.InitialArgumentMatcherBuilder":
        return MockShell.InitialArgumentMatcherBuilder(self, command_matcher)

    class InitialArgumentMatcherBuilder:
        def __init__(
            self, mock_shell: "MockShell", command_matcher: Optional[StringMatcher]
        ):
            self._mock_shell: "MockShell" = mock_shell
            self._command_matcher: Optional[StringMatcher] = command_matcher

        def has_argument(
            self, argument_matcher: StringMatcher
        ) -> "MockShell.RepeatedArgumentMatcherBuilder":
            return MockShell.RepeatedArgumentMatcherBuilder(
                self._mock_shell, argument_matcher, self._command_matcher
            )

        def then_return(self, response: MockShellResponse) -> None:
            rule: MockShellRule = MockShellRule(
                MockShellInvocationMatcher(self._command_matcher, None), response
            )
            self._mock_shell._mock_rules.append(rule)

    class RepeatedArgumentMatcherBuilder:
        def __init__(
            self,
            mock_shell: "MockShell",
            first_argument_matcher: StringMatcher,
            command_matcher: Optional[StringMatcher],
        ):
            self._mock_shell: "MockShell" = mock_shell
            self._argument_matchers: List[StringMatcher] = [first_argument_matcher]
            self._command_matcher: Optional[StringMatcher] = command_matcher

        def has_argument(
            self, argument_matcher: StringMatcher
        ) -> "MockShell.RepeatedArgumentMatcherBuilder":
            self._argument_matchers.append(argument_matcher)
            return self

        def then_return(self, response: MockShellResponse) -> None:
            rule: MockShellRule = MockShellRule(
                MockShellInvocationMatcher(
                    self._command_matcher, self._argument_matchers
                ),
                response,
            )
            self._mock_shell._mock_rules.append(rule)

    # endregion
