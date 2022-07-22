import datetime
import re
from dataclasses import dataclass
from pathlib import Path
from re import Pattern
from typing import Optional, List

from development_environment.development_environment import DevelopmentEnvironment
from shell.shell import Shell
from shell.shell_response import ShellResponse


@dataclass(frozen=True)
class GitCommit:
    hash: str
    author_name: str
    author_email: str
    date: datetime.datetime
    message: str


def collect_release_notes(repository: Path,
                          since: Optional[str] = None,
                          until: Optional[str] = None,
                          shell: Optional[Shell] = None) -> str:
    dev_env: DevelopmentEnvironment = DevelopmentEnvironment.load(repository, shell)

    git_log_parameter: str
    if since is None and until is None:
        git_log_parameter = ""

    elif since is None and until is not None:
        git_log_parameter = f"{until}^"

    elif since is not None and until is None:
        git_log_parameter = f"{since}..HEAD"

    else:
        git_log_parameter = f"{since}..{until}"

    commits: List[GitCommit] = _get_git_commits(dev_env, git_log_parameter)


def _get_git_commits(dev_env: DevelopmentEnvironment, git_log_parameter: str) -> List[GitCommit]:
    git_log_response: ShellResponse = dev_env.shell.run_or_raise("git",
                                                                 ["log", git_log_parameter],
                                                                 working_directory=dev_env.root)

    commit_head_pattern: Pattern = re.compile(r"^commit (?P<hash>[\da-f]{40})$\n"
                                              r"(?:^Merge: (?P<merge_hash_a>[\da-f]{7}) (?P<merge_hash_b>[\da-f]{7})$\n)?"
                                              r"^Author: (?P<author_name>[^<]+?) <(?P<author_email>[^>]+?)>$\n"
                                              r"^Date:\s+(?P<date>.+?)$\n",
                                              re.RegexFlag.MULTILINE)

    date_time_format: str = "%a %b %d %H:%M:%S %Y %z"

    result: List[GitCommit] = []

    git_log: str = git_log_response.stdout
    matches: List[re.Match] = commit_head_pattern.findall(git_log)
    for i in range(len(matches)):
        match: re.Match = matches[i]
        is_last_match: bool = i == len(matches) - 1

        message: str
        if is_last_match:
            message = git_log[match.end():]

        else:
            message = git_log[match.end(): matches[i + 1].start()]

        result.append(GitCommit(match.group("hash"),
                                match.group("author_name"),
                                match.group("author_email"),
                                datetime.datetime.strptime(match.group("date"), date_time_format),
                                message))

    return result


def main() -> None:
    pass


if __name__ == "__main__":
    main()
