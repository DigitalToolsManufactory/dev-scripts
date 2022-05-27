from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional, List, Tuple

from development_environment.development_environment import DevelopmentEnvironment
from development_environment.git_configuration import GitRemote
from shell.command.get_git_remote_head_branch import GetGitRemoteHeadBranch
from shell.shell import Shell
from shell.shell_response import ShellResponse
from utility.type_utility import get_or_else

__DEFAULT_REMOTE_NAME: str = "origin"


def checkout_head_branch(repository: Path, remote_name: Optional[str] = None, shell: Optional[Shell] = None) -> None:
    dev_env: DevelopmentEnvironment = DevelopmentEnvironment.load(repository, shell)
    remote, head_branch = _get_head_branch(dev_env, remote_name)

    dev_env.shell.run_or_raise("git", ["switch", "-C", head_branch, "--track", f"{remote}/{head_branch}"], dev_env.root)


def _get_head_branch(dev_env: DevelopmentEnvironment, remote_name: Optional[str]) -> Tuple[str, str]:
    dev_env_remotes: List[GitRemote] = get_or_else(dev_env.git_configuration.remotes, [])

    # Option 1: Search for a pre-configured head branch in the dev-env
    if len(dev_env_remotes) > 0:
        matching_remotes: List[GitRemote] = [remote for remote in dev_env_remotes
                                             if remote.head_branch is not None
                                             and (remote_name is None or remote_name == remote.name)]

        if len(matching_remotes) > 0:
            return matching_remotes[0].name, matching_remotes[0].head_branch

    dev_env.shell.run_or_raise("git", ["fetch", "--all"], dev_env.root)

    # Option 2: Get the head branch via git command for a given remote name
    if remote_name is not None:
        head_branch: Optional[str] = GetGitRemoteHeadBranch.run(dev_env.root, remote_name, dev_env.shell)

        if head_branch is not None:
            return remote_name, head_branch

    # Option 3: If no remote name was given explicitly, get all remotes and determine the head branch
    remotes_response: ShellResponse = dev_env.shell.run_or_raise("git", ["remote"], dev_env.root)
    remote_names: List[str] = [remote.strip() for remote in remotes_response.get_stdout_lines()]

    # Option 3 (A): The list of remotes contains the default remote name
    # --> assume the user wants to use this remote
    if __DEFAULT_REMOTE_NAME in remote_names:
        head_branch: Optional[str] = GetGitRemoteHeadBranch.run(dev_env.root, __DEFAULT_REMOTE_NAME, dev_env.shell)

        if head_branch is not None:
            return __DEFAULT_REMOTE_NAME, head_branch

    # Option 3 (B): The list of remotes does NOT contain the default remote name
    # --> loop through all existing remotes until we find a head branch
    for name in remote_names:
        head_branch: Optional[str] = GetGitRemoteHeadBranch.run(dev_env.root, name, dev_env.shell)

        if head_branch is not None:
            return name, head_branch

    raise Exception(f"Unable to determine the HEAD branch for repository at '{dev_env.root.absolute()}'.")


def main() -> None:
    argument_parser: ArgumentParser = ArgumentParser(
        "Determines the head branch of the current project and checks it out"
    )

    argument_parser.add_argument(
        "--repository-path",
        type=Path,
        required=True
    )
    argument_parser.add_argument(
        "--remote-name",
        type=str,
        required=False
    )

    parsed_args: Any = argument_parser.parse_args()
    checkout_head_branch(parsed_args.repository_path,
                         parsed_args.remote_name)


if __name__ == "__main__":
    main()
