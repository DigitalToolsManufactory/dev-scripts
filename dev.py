from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional

from varname import nameof

from development_environment.development_environment import DevelopmentEnvironment
from shell.shell import Shell, DefaultShell
from utility.type_utility import get_or_else


def init(project: Path, shell: Optional[Shell] = None) -> DevelopmentEnvironment:
    shell = get_or_else(shell, DefaultShell.new)
    dev_env: DevelopmentEnvironment = DevelopmentEnvironment.infer(project, shell)
    dev_env.store()

    return dev_env


def main() -> None:
    argument_parser: ArgumentParser = ArgumentParser(
        "dev-scripts (https://github.com/DigitalToolsManufactory/dev-scripts) tool"
    )

    sub_parsers: Any = argument_parser.add_subparsers(dest="subparser")

    # region init command
    init_parser: ArgumentParser = sub_parsers.add_parser(nameof(init),
                                                         help="Initializes a new development environment")
    init_parser.add_argument("project",
                             type=Path)

    # endregion

    parsed_args: Any = argument_parser.parse_args()
    if parsed_args.subparser == nameof(init):
        init(parsed_args.project)
        return

    argument_parser.print_help()


if __name__ == "__main__":
    main()
