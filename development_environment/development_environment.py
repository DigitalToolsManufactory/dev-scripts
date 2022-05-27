from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from development_environment.git_configuration import GitConfiguration
from shell.shell import Shell, DefaultShell
from utility.type_utility import get_or_else


@dataclass(frozen=True)
class DevelopmentEnvironment:
    root: Path
    shell: Shell
    git_configuration: GitConfiguration

    ROOT_DIRECTORY: ClassVar[str] = ".dev-env"
    GIT_DIRECTORY: ClassVar[str] = ".git"

    @staticmethod
    def load(current_directory: Path, shell: Optional[Shell] = None) -> "DevelopmentEnvironment":
        root_dir: Optional[Path] = DevelopmentEnvironment._get_root_directory(current_directory)

        git_configuration: GitConfiguration = GitConfiguration() \
            if root_dir is None \
            else GitConfiguration.load(root_dir)

        return DevelopmentEnvironment(
            get_or_else(root_dir, current_directory),
            get_or_else(shell, DefaultShell.new),
            git_configuration
        )

    @staticmethod
    def _get_root_directory(current_directory: Path) -> Optional[Path]:
        while current_directory != current_directory.parent:
            root_dir: Path = Path(current_directory, DevelopmentEnvironment.ROOT_DIRECTORY)

            if root_dir.is_dir():
                return root_dir

            git_dir: Path = Path(current_directory, DevelopmentEnvironment.GIT_DIRECTORY)
            if git_dir.is_dir():
                # return on the first occurrence of a .git directory to not search in unrelated projects
                return None

            current_directory = current_directory.parent

        return None
