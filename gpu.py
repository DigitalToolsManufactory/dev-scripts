from argparse import ArgumentParser
from pathlib import Path
from typing import Any, List, Optional

from development_environment.development_environment import DevelopmentEnvironment
from development_environment.git_configuration import GitRemote
from shell.shell import Shell
from shell.shell_response import ShellResponse
from utility import git_utility
from utility.git_utility import CurrentLocalBranch
from utility.type_utility import get_or_else


def push_with_upstream(
    project: Path,
    remote_name: Optional[str] = None,
    commit_message: Optional[str] = None,
    shell: Optional[Shell] = None,
) -> None:
    dev_env: DevelopmentEnvironment = DevelopmentEnvironment.load(project, shell)

    local_branch: Optional[CurrentLocalBranch] = git_utility.get_current_local_branch(
        dev_env
    )

    if local_branch is None:
        raise Exception(
            f"Unable to determine current local branch in project '{project.expanduser().absolute()}'."
        )

    if local_branch.remote_name is not None and local_branch.tracking_name is not None:
        _commit_changed_files(dev_env, commit_message)
        dev_env.shell.run_or_raise("git", ["push"], dev_env.root)
        return

    actual_remote_name: Optional[str] = (
        remote_name if remote_name is not None else _get_remote_name(dev_env)
    )

    if actual_remote_name is None:
        raise Exception(
            f"Unable to determine remote name in project '{project.expanduser().absolute()}'."
        )

    _commit_changed_files(dev_env, commit_message)
    dev_env.shell.run_or_raise(
        "git",
        ["push", "--set-upstream", actual_remote_name, local_branch.name],
        dev_env.root,
    )


def _get_remote_name(dev_env: DevelopmentEnvironment) -> Optional[str]:
    dev_env_remotes: List[GitRemote] = get_or_else(
        dev_env.git_configuration.remotes, list
    )

    # Option 1: Check dev env for pre-configured remotes
    if len(dev_env_remotes) > 0:
        return dev_env_remotes[0].name

    # Option 2: Fallback to git command
    remote_response: ShellResponse = dev_env.shell.run("git", ["remote"], dev_env.root)

    if not remote_response.is_success:
        return None

    remote_names: List[str] = remote_response.get_stdout_lines()
    if len(remote_names) < 1:
        return None

    if git_utility.DEFAULT_REMOTE_NAME in remote_names:
        return git_utility.DEFAULT_REMOTE_NAME

    return remote_names[0]


def _commit_changed_files(
    dev_env: DevelopmentEnvironment, message: Optional[str]
) -> None:
    if message is None or not _contains_changed_files(dev_env):
        return

    dev_env.shell.run_or_raise("git", ["commit", ".", "-m", message], dev_env.root)


def _contains_changed_files(dev_env: DevelopmentEnvironment) -> bool:
    response: ShellResponse = dev_env.shell.run(
        "git", ["diff", "--name-only"], dev_env.root
    )

    return response.is_success and len(response.get_stdout_lines()) > 0


def main() -> None:
    argument_parser: ArgumentParser = ArgumentParser(
        "Pushes local commits to the (default) remote."
        "If the current branch has no tracking branch, set the tracking branch using the local branch name."
    )

    argument_parser.add_argument("--project", type=Path, required=True)
    argument_parser.add_argument("--remote-name", type=str, required=False)
    argument_parser.add_argument("--message", "-m", type=str, required=False)

    parsed_args: Any = argument_parser.parse_args()
    push_with_upstream(
        parsed_args.project, parsed_args.remote_name, parsed_args.message
    )


if __name__ == "__main__":
    main()
