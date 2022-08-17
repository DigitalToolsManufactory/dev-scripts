import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Union

from varname import nameof

from shell.command.get_git_remote_head_branch import GetGitRemoteHeadBranch
from shell.shell import DefaultShell, Shell
from shell.shell_response import ShellResponse
from utility.type_utility import get_or_else


@dataclass(frozen=True)
class GitRemote:
    name: str
    head_branch: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


@dataclass(frozen=True)
class GitConfiguration:
    remotes: Optional[List[GitRemote]] = None

    FILE_NAME: ClassVar[str] = "git-configuration.json"

    # region store
    def store(self, directory: Path) -> None:
        file: Path = Path(directory, GitConfiguration.FILE_NAME)
        with file.open("w") as f:
            f.writelines(self.to_json())

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    def to_dict(self) -> Dict[str, Any]:
        return {
            nameof(GitConfiguration.remotes): [
                remote.to_dict() for remote in self.remotes
            ]
        }

    # endregion

    # region load
    @staticmethod
    def load(directory: Optional[Path]) -> "GitConfiguration":
        if directory is None:
            return GitConfiguration()

        file: Path = Path(directory, GitConfiguration.FILE_NAME)
        if not file.is_file():
            return GitConfiguration()

        return GitConfiguration.from_json(file.read_text())

    @staticmethod
    def from_json(content: Union[str, Dict[str, Any]]) -> "GitConfiguration":
        if isinstance(content, str):
            data: Dict[str, Any] = json.loads(content)

        elif isinstance(content, Dict):
            data: Dict[str, Any] = content

        else:
            raise TypeError(
                f"The given 'content' ({content}) must be of type 'str' or 'dict'"
            )

        remotes: Optional[List[GitRemote]] = None
        if nameof(GitConfiguration.remotes) in data:
            remotes = []
            for item in data[nameof(GitConfiguration.remotes)]:
                remotes.append(GitRemote(**item))

        return GitConfiguration(remotes)

    # endregion

    # region infer
    @staticmethod
    def infer(directory: Path, shell: Optional[Shell] = None) -> "GitConfiguration":
        shell = get_or_else(shell, DefaultShell.new)
        git_fetch_response: ShellResponse = shell.run(
            "git", ["fetch", "--all"], directory
        )

        if not git_fetch_response.is_success:
            # project does not use git
            return GitConfiguration()

        git_remote_response: ShellResponse = shell.run_or_raise(
            "git", ["remote"], directory
        )
        git_remotes: List[GitRemote] = []
        for remote_name in git_remote_response.get_stdout_lines():
            head_branch: Optional[str] = GetGitRemoteHeadBranch.run(
                directory, remote_name, shell
            )
            git_remotes.append(GitRemote(remote_name, head_branch))

        return GitConfiguration(git_remotes)

    # endregion
