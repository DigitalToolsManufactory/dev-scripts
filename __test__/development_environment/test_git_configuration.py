from pathlib import Path
from unittest import TestCase

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
