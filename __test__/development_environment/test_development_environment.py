from pathlib import Path
from unittest import TestCase

from development_environment.development_environment import DevelopmentEnvironment
from development_environment.git_configuration import GitConfiguration, GitRemote


class TestDevelopmentEnvironment(TestCase):
    resource_root: Path = Path(Path(__file__).parent, "resource")

    def test_load_from_root(self) -> None:
        root: Path = Path(self.resource_root, "dev-env")

        sut: DevelopmentEnvironment = DevelopmentEnvironment.load(root)

        self.assert_filled_git_config(sut)

    def test_load_from_sub_directory(self) -> None:
        root: Path = Path(self.resource_root, "dev-env", "sub-dir")

        sut: DevelopmentEnvironment = DevelopmentEnvironment.load(root)

        self.assert_filled_git_config(sut)

    def test_load_without_root(self) -> None:
        root: Path = Path(self.resource_root, "no-dev-env")
        DevelopmentEnvironment.GIT_DIRECTORY = "git-root"

        sut: DevelopmentEnvironment = DevelopmentEnvironment.load(root)

        self.assert_empty_git_config(sut)

    def test_load_stops_at_first_git_root(self) -> None:
        root: Path = Path(self.resource_root, "dev-env", "git-dir")
        DevelopmentEnvironment.GIT_DIRECTORY = "git-root"

        sut: DevelopmentEnvironment = DevelopmentEnvironment.load(root)

        self.assert_empty_git_config(sut)

    def assert_filled_git_config(self, development_environment: DevelopmentEnvironment) -> None:
        sut: GitConfiguration = development_environment.git_configuration

        self.assertIsNotNone(sut.remotes)
        self.assertEqual(len(sut.remotes), 1)

        remote: GitRemote = sut.remotes[0]
        self.assertEqual(remote.name, "origin")
        self.assertEqual(remote.head_branch, "master")

    def assert_empty_git_config(self, development_environment: DevelopmentEnvironment) -> None:
        sut: GitConfiguration = development_environment.git_configuration

        self.assertIsNone(sut.remotes)