import re
from argparse import ArgumentParser
from pathlib import Path
from re import Pattern
from typing import Any, List, Optional, Set, cast

from development_environment.development_environment import DevelopmentEnvironment
from development_environment.formatter_configuration import (
    FormatterType,
    MavenFormatterConfiguration,
    VenvFormatterConfiguration,
)
from java.maven.xml_maven_module import XmlMavenModule
from java.maven.xml_maven_module_reader import XmlMavenModuleReader
from shell.shell import Shell
from shell.shell_response import ShellResponse
from utility.type_utility import get_or_else


def format_source_code(project: Path, shell: Optional[Shell] = None) -> None:
    dev_env: DevelopmentEnvironment = DevelopmentEnvironment.load(project, shell)

    if dev_env.formatter_configuration.formatter_type == FormatterType.MAVEN:
        _format_maven_project(dev_env)
        return

    if dev_env.formatter_configuration.formatter_type == FormatterType.VENV:
        _format_venv_project(dev_env)
        return

    print(
        f"The given formatter type '{dev_env.formatter_configuration.formatter_type.value}' is not supported"
    )


# region Maven
def _format_maven_project(dev_env: DevelopmentEnvironment) -> None:
    config: MavenFormatterConfiguration = cast(
        MavenFormatterConfiguration, dev_env.formatter_configuration
    )
    arguments: List[str] = []
    arguments.extend(config.goals)
    arguments.extend(_get_maven_modules_arguments(dev_env, config))
    arguments.extend(config.additional_arguments)

    dev_env.shell.run_or_raise("mvn", arguments, dev_env.root)


def _get_maven_modules_arguments(
    dev_env: DevelopmentEnvironment,
    formatter_configuration: MavenFormatterConfiguration,
) -> List[str]:
    files_to_format: Optional[List[Path]] = _get_files_to_format(dev_env)
    if files_to_format is None:
        result: List[str] = []
        for exclusion in set(formatter_configuration.excluded_modules):
            result.extend(["-pl", f"!{exclusion}"])

        return result

    poms: Set[Path] = set()
    for file in filter(_is_relevant_for_maven_formatting, files_to_format):
        parent: Path = file.parent
        while parent != dev_env.root:
            pom: Path = Path(parent, "pom.xml")
            if pom.exists() and pom.is_file():
                poms.add(pom)
                break

            parent = parent.parent

    module_reader: XmlMavenModuleReader = XmlMavenModuleReader()
    modules: List[XmlMavenModule] = [module_reader.read(pom) for pom in poms]
    module_names: Set[str] = set(
        f"{m.identifier.group_id}:{m.identifier.artifact_id}" for m in modules
    )
    module_names -= set(formatter_configuration.excluded_modules)

    result: List[str] = []
    for name in module_names:
        result.extend(["-pl", name])

    for exclusion in set(formatter_configuration.excluded_modules):
        result.extend(["-pl", f"!{exclusion}"])

    return result


def _is_relevant_for_maven_formatting(file: Path) -> bool:
    if file.name == "pom.xml":
        return True

    if file.suffix == ".java":
        return True

    return False


# endregion


# region Venv
def _format_venv_project(dev_env: DevelopmentEnvironment) -> None:
    config: VenvFormatterConfiguration = cast(
        VenvFormatterConfiguration, dev_env.formatter_configuration
    )
    arguments: Optional[List[List[str]]] = _get_venv_python_arguments(dev_env, config)
    if arguments is None:
        return

    python_executable: Optional[Path] = _find_venv_python_executable(dev_env)
    if python_executable is None:
        print(f"Unable to find python executable for VENV project in '{dev_env.root.resolve().absolute()}'")
        return

    for argument_list in arguments:
        dev_env.shell.run_or_raise(
            str(python_executable), ["-m"] + argument_list, dev_env.root
        )


def _get_venv_python_arguments(
    dev_env: DevelopmentEnvironment, formatter_configuration: VenvFormatterConfiguration
) -> Optional[List[List[str]]]:
    if len(formatter_configuration.goals) < 1:
        return None

    files_to_format: List[Path] = get_or_else(_get_files_to_format(dev_env), list)
    files_to_format = list(filter(_is_relevant_for_venv_formatting, files_to_format))
    result: List[List[str]] = []
    for goal in formatter_configuration.goals:
        arguments: List[str] = [g.strip() for g in goal.split(" ")]

        if len(files_to_format) < 1:
            arguments.append(
                str(dev_env.root.resolve().absolute())
            )  # format the entire project

        else:
            arguments.extend([str(f.resolve().absolute()) for f in files_to_format])

        result.append(arguments)

    return result


def _is_relevant_for_venv_formatting(file: Path) -> bool:
    return file.suffix == ".py"


def _find_venv_python_executable(dev_env: DevelopmentEnvironment) -> Optional[Path]:
    venv_pattern: Pattern = re.compile(r"^.*venv.*", re.RegexFlag.IGNORECASE)
    scripts_pattern: Pattern = re.compile("^scripts$", re.RegexFlag.IGNORECASE)

    for venv_dir in dev_env.root.iterdir():
        if not venv_dir.is_dir():
            continue

        if venv_pattern.match(venv_dir.name) is None:
            continue

        for scripts_dir in venv_dir.iterdir():
            if not scripts_dir.is_dir():
                continue

            if scripts_pattern.match(scripts_dir.name) is None:
                continue

            for python_file in scripts_dir.iterdir():
                if not python_file.is_file():
                    continue

                if python_file.stem.lower() == "python":
                    return python_file.resolve().absolute()

    return None


# endregion


def _get_files_to_format(dev_env: DevelopmentEnvironment) -> Optional[List[Path]]:
    # Option 1: Get changed files compared to the current branch
    diff_response: ShellResponse = dev_env.shell.run(
        "git", ["diff", "--name-only"], dev_env.root
    )

    if not diff_response.is_success:
        # Project doesn't use git for version control
        return None

    std_out_lines: List[str] = diff_response.get_stdout_lines()
    if len(std_out_lines) > 0:
        return [Path(dev_env.root, file_name) for file_name in std_out_lines]

    # Option 2: Get changed files compared to the head branch
    if dev_env.git_configuration.remotes is None:
        return None

    head_branch: Optional[str] = None
    for remote in dev_env.git_configuration.remotes:
        if remote.head_branch is not None:
            head_branch = remote.head_branch
            break

    if head_branch is None:
        return None

    diff_response = dev_env.shell.run(
        "git", ["diff", "--name-only", head_branch], dev_env.root
    )
    std_out_lines = diff_response.get_stdout_lines()
    if len(std_out_lines) < 1:
        return None

    return [Path(dev_env.root, file_name) for file_name in std_out_lines]


def main() -> None:
    argument_parser: ArgumentParser = ArgumentParser("Formats source code")

    argument_parser.add_argument("--project", type=Path, required=True)

    parsed_args: Any = argument_parser.parse_args()
    format_source_code(parsed_args.project)


if __name__ == "__main__":
    main()
