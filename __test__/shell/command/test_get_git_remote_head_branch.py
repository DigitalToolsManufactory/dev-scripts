from pathlib import Path
from typing import Optional
from unittest import TestCase

from __test__.shell.mock.mock_shell import MockShell, MockShellResponse
from __test__.string_matcher import StringMatcher
from shell.command.get_git_remote_head_branch import GetGitRemoteHeadBranch


class TestGetGitRemoteHeadBranch(TestCase):
    def test_run_success(self) -> None:
        mock: MockShell = MockShell()

        mock.when_command(StringMatcher.exact("git")).has_argument(
            StringMatcher.exact("remote show origin")
        ).then_return(
            MockShellResponse.of_success(
                """ 
            * remote origin 
              Fetch URL: https://github.com/octocat/Hello-World.git
              Push  URL: https://github.com/octocat/Hello-World.git
              HEAD branch: main
              Remote branch:
                main tracked
              Local branch configured for 'git pull':
                main merges with remote main
              Local ref configured for 'git push':
                main pushes to main (up to date)
            """
            )
        )

        actual: Optional[str] = GetGitRemoteHeadBranch.run(Path("."), "origin", mock)

        self.assertEqual(actual, "main")

    def test_run_failure(self) -> None:
        mock: MockShell = MockShell()

        mock.when_command(StringMatcher.any()).then_return(
            MockShellResponse.of_error("Failure!")
        )

        actual: Optional[str] = GetGitRemoteHeadBranch.run(Path("."), "origin", mock)

        self.assertIsNone(actual)
