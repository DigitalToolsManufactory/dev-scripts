from pathlib import Path
from typing import ClassVar, Optional

from shell.shell import DefaultShell, Shell
from shell.shell_response import ShellResponse
from utility.type_utility import get_or_else


class GetGitRemoteHeadBranch:
    HEAD_BRANCH_PREFIX: ClassVar[str] = "HEAD branch: "

    @staticmethod
    def run(
        directory: Path, remote_name: str, shell: Optional[Shell] = None
    ) -> Optional[str]:
        shell = get_or_else(shell, DefaultShell.new)

        response: ShellResponse = shell.run(
            "git", ["remote", "show", remote_name], directory
        )

        if not response.is_success:
            return None

        for line in [line.strip() for line in response.get_stdout_lines()]:
            if line.startswith(GetGitRemoteHeadBranch.HEAD_BRANCH_PREFIX):
                return line.removeprefix(GetGitRemoteHeadBranch.HEAD_BRANCH_PREFIX)

        return None
