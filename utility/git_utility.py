from dataclasses import dataclass, field
from typing import Optional, List

from development_environment.development_environment import DevelopmentEnvironment
from shell.shell_response import ShellResponse

DEFAULT_REMOTE_NAME: str = "origin"


@dataclass(frozen=True)
class CurrentLocalBranch:
    name: str
    remote_name: Optional[str] = field(default=None)
    tracking_name: Optional[str] = field(default=None)


def get_current_local_branch(
        dev_env: DevelopmentEnvironment,
) -> Optional[CurrentLocalBranch]:
    branch_response: ShellResponse = dev_env.shell.run("git", ["branch"], dev_env.root)

    if not branch_response.is_success:
        return None

    current_branch_names: List[str] = list(
        filter(lambda x: x.startswith("* "), branch_response.get_stdout_lines())
    )
    if len(current_branch_names) != 1:
        return None

    local_branch_name: str = current_branch_names[0].removeprefix("* ")
    tracking_branch_response: ShellResponse = dev_env.shell.run(
        "git", ["config", "--get", f"branch.{local_branch_name}.merge"], dev_env.root
    )

    if not tracking_branch_response.is_success:
        return CurrentLocalBranch(current_branch_names[0])

    tracking_branches: List[str] = list(
        filter(lambda x: len(x) > 0, tracking_branch_response.get_stdout_lines())
    )
    if len(tracking_branches) != 1:
        return CurrentLocalBranch(current_branch_names[0])

    tracking_branch_name: str = tracking_branches[0].removeprefix("refs/heads/")

    tracking_remote_response: ShellResponse = dev_env.shell.run(
        "git", ["config", "--get", f"branch.{local_branch_name}.remote"], dev_env.root
    )

    if not tracking_remote_response.is_success:
        return CurrentLocalBranch(current_branch_names[0])

    tracking_remotes: List[str] = list(
        filter(lambda x: len(x) > 0, tracking_remote_response.get_stdout_lines())
    )
    if len(tracking_remotes) != 1:
        return CurrentLocalBranch(current_branch_names[0])

    tracking_remote: str = tracking_remotes[0]

    return CurrentLocalBranch(local_branch_name, tracking_remote, tracking_branch_name)
