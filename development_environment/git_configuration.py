import json
import re
from abc import abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from re import Pattern
from typing import Any, ClassVar, Dict, List, Optional, Union

from varname import nameof

from shell.command.get_git_remote_head_branch import GetGitRemoteHeadBranch
from shell.shell import DefaultShell, Shell
from shell.shell_response import ShellResponse
from utility.type_utility import get_or_else


class GitBranchProtectionRule:
    @staticmethod
    def from_json(data: Dict[str, Any]) -> "GitBranchProtectionRule":
        return GitBranchProtectionRule(str(data["branch_name_pattern"]))

    def __init__(self, branch_name_pattern: str) -> None:
        self._raw_pattern: str = branch_name_pattern
        self._pattern: Pattern = re.compile(branch_name_pattern)

    @abstractmethod
    def is_protected(self, branch_name: str) -> bool:
        return self._pattern.match(branch_name) is not None

    def to_dict(self) -> Dict[str, Any]:
        return {"branch_name_pattern": self._raw_pattern}


@dataclass(frozen=True)
class GitRemote:
    name: str
    head_branch: Optional[str] = field(default=None)
    branch_protection_rules: Optional[List[GitBranchProtectionRule]] = field(
        default_factory=list
    )

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "GitRemote":
        name: str = str(data["name"])
        head_branch: Optional[str] = (
            str(data["head_branch"]) if "head_branch" in data else None
        )
        branch_protection_rules: Optional[List[GitBranchProtectionRule]] = (
            [
                GitBranchProtectionRule.from_json(x)
                for x in list(data["branch_protection_rules"])
            ]
            if "branch_protection_rules" in data
            else None
        )

        return GitRemote(name, head_branch, branch_protection_rules)

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"name": self.name}

        if self.head_branch:
            result["head_branch"] = self.head_branch

        if (
            self.branch_protection_rules is not None
            and len(self.branch_protection_rules) > 0
        ):
            result["branch_protection_rules"] = [
                x.to_dict() for x in self.branch_protection_rules
            ]

        return result

    def is_protected_branch(self, branch_name: str) -> bool:
        if self.branch_protection_rules is None:
            return False

        return any(x.is_protected(branch_name) for x in self.branch_protection_rules)


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
                remotes.append(GitRemote.from_json(item))

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
            protection_rules: Optional[List[GitBranchProtectionRule]] = None
            if head_branch:
                protection_rules = [GitBranchProtectionRule(head_branch)]

            git_remotes.append(GitRemote(remote_name, head_branch, protection_rules))

        return GitConfiguration(git_remotes)

    # endregion
