from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, List, Tuple

from development_environment.development_environment import DevelopmentEnvironment
from development_environment.git_configuration import GitRemote
from shell.command.get_git_remote_head_branch import GetGitRemoteHeadBranch
from shell.shell import Shell
from shell.shell_response import ShellResponse
from utility.type_utility import get_or_else

__DEFAULT_REMOTE_NAME: str = "origin"


@dataclass(frozen=True)
class CurrentLocalBranch:
    name: str
    remote_name: str
    tracking_name: str


def checkout_head_branch(project: Path, remote_name: Optional[str] = None, shell: Optional[Shell] = None) -> None:
    dev_env: DevelopmentEnvironment = DevelopmentEnvironment.load(project, shell)
    remote, head_branch = _get_head_branch(dev_env, remote_name)

    current_branch: CurrentLocalBranch = _get_current_branch(dev_env)

    if current_branch is None or current_branch.tracking_name != head_branch or current_branch.remote_name != remote:
        # we are not on the branch that is already tracking the head branch. So we need to switch branches
        dev_env.shell.run_or_raise("git",
                                   [
                                       "switch",
                                       "-C",
                                       head_branch,
                                       "--track",
                                       f"{remote}/{head_branch}"
                                   ],
                                   dev_env.root)

    dev_env.shell.run_or_raise("git", ["pull"], dev_env.root)


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


def _get_current_branch(dev_env: DevelopmentEnvironment) -> Optional[CurrentLocalBranch]:
    branch_response: ShellResponse = dev_env.shell.run("git", ["branch"], dev_env.root)

    if not branch_response.is_success:
        return None

    current_branch_names: List[str] = list(filter(lambda x: x.startswith("* "), branch_response.get_stdout_lines()))
    if len(current_branch_names) != 1:
        return None

    local_branch_name: str = current_branch_names[0].removeprefix("* ")
    tracking_branch_response: ShellResponse = dev_env.shell.run("git",
                                                                [
                                                                    "config",
                                                                    "--get",
                                                                    f"branch.{local_branch_name}.merge"
                                                                ],
                                                                dev_env.root)

    if not tracking_branch_response.is_success:
        return None

    tracking_branches: List[str] = list(filter(lambda x: len(x) > 0, tracking_branch_response.get_stdout_lines()))
    if len(tracking_branches) != 1:
        return None

    tracking_branch_name: str = tracking_branches[0].removeprefix("refs/heads/")

    tracking_remote_response: ShellResponse = dev_env.shell.run("git",
                                                                [
                                                                    "config",
                                                                    "--get",
                                                                    f"branch.{local_branch_name}.remote"
                                                                ],
                                                                dev_env.root)

    if not tracking_remote_response.is_success:
        return None

    tracking_remotes: List[str] = list(filter(lambda x: len(x) > 0, tracking_remote_response.get_stdout_lines()))
    if len(tracking_remotes) != 1:
        return None

    tracking_remote: str = tracking_remotes[0]

    return CurrentLocalBranch(local_branch_name, tracking_remote, tracking_branch_name)


def main() -> None:
    argument_parser: ArgumentParser = ArgumentParser(
        "Determines the head branch of the current project and checks it out"
    )

    argument_parser.add_argument(
        "--project",
        type=Path,
        required=True
    )
    argument_parser.add_argument(
        "--remote-name",
        type=str,
        required=False
    )

    parsed_args: Any = argument_parser.parse_args()
    checkout_head_branch(parsed_args.project,
                         parsed_args.remote_name)


if __name__ == "__main__":
    main()
