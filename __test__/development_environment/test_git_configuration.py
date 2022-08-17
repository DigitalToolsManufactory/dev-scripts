from pathlib import Path
from unittest import TestCase

from __test__.shell.mock.mock_shell import MockShell, MockShellResponse
from __test__.string_matcher import StringMatcher
from __test__.type_assertions import TypeAssertions
from development_environment.git_configuration import GitConfiguration, GitRemote


class TestGitConfiguration(TestCase):
    resource_root: Path = Path(Path(__file__).parent, "resource")

    def test_load_with_file(self) -> None:
        root: Path = Path(self.resource_root, "dev-env", ".dev-env")

        sut: GitConfiguration = GitConfiguration.load(root)

        self.assertIsNotNone(sut.remotes)
        self.assertEqual(len(sut.remotes), 1)

        remote: GitRemote = sut.remotes[0]
        self.assertEqual(remote.name, "origin")
        self.assertEqual(remote.head_branch, "master")

    def test_load_without_file(self) -> None:
        root: Path = Path(self.resource_root, "no-dev-env")

        sut: GitConfiguration = GitConfiguration.load(root)

        self.assertIsNone(sut.remotes)

    def test_load_without_directory(self) -> None:
        sut: GitConfiguration = GitConfiguration.load(None)

        self.assertIsNone(sut.remotes)

    def test_to_json(self) -> None:
        sut: GitConfiguration = GitConfiguration([GitRemote("origin", "main")])

        actual: str = sut.to_json()

        TypeAssertions.json_equals(
            self, actual, '{"remotes": [{"name": "origin", "head_branch": "main"}]}'
        )

    def test_infer_success(self) -> None:
        mock: MockShell = MockShell()

        mock.when_command(StringMatcher.exact("git")).has_argument(
            StringMatcher.exact("fetch --all")
        ).then_return(MockShellResponse.of_success(""))

        mock.when_command(StringMatcher.exact("git")).has_argument(
            StringMatcher.exact("remote")
        ).then_return(MockShellResponse.of_success("origin\nfork"))

        mock.when_command(StringMatcher.exact("git")).has_argument(
            StringMatcher.exact("remote show origin")
        ).then_return(
            MockShellResponse.of_success(
                """ 
            * remote origin 
              Fetch URL: https://github.com/octocat/Hello-World.git
              Push  URL: https://github.com/octocat/Hello-World.git
              HEAD branch: origin-main
              Remote branch:
                origin-main tracked
              Local branch configured for 'git pull':
                origin-main merges with remote origin-main
              Local ref configured for 'git push':
                origin-main pushes to origin-main (up to date)
            """
            )
        )

        mock.when_command(StringMatcher.exact("git")).has_argument(
            StringMatcher.exact("remote show fork")
        ).then_return(
            MockShellResponse.of_success(
                """ 
            * remote fork 
              Fetch URL: https://github.com/fork/Hello-World.git
              Push  URL: https://github.com/fork/Hello-World.git
              HEAD branch: fork-main
              Remote branch:
                fork-main tracked
              Local branch configured for 'git pull':
                fork-main merges with remote fork-main
              Local ref configured for 'git push':
                fork-main pushes to fork-main (up to date)
            """
            )
        )

        sut: GitConfiguration = GitConfiguration.infer(Path("."), mock)

        self.assertEqual(len(sut.remotes), 2)

        origin: GitRemote = sut.remotes[0]
        self.assertEqual(origin.name, "origin")
        self.assertEqual(origin.head_branch, "origin-main")

        fork: GitRemote = sut.remotes[1]
        self.assertEqual(fork.name, "fork")
        self.assertEqual(fork.head_branch, "fork-main")

    def test_infer_failure(self) -> None:
        mock: MockShell = MockShell()

        mock.when_command(StringMatcher.any()).then_return(
            MockShellResponse.of_error("")
        )

        sut: GitConfiguration = GitConfiguration.infer(Path("."), mock)

        self.assertIsNone(sut.remotes)
