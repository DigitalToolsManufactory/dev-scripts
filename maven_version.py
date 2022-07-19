import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Any, Dict

from java.maven.xml_maven_module import XmlMavenModule
from java.maven.xml_maven_module_reader import XmlMavenModuleReader
from java.maven.xml_maven_project import XmlMavenProject


def bump(project_root_poms: List[Path],
         bump_type: XmlMavenProject.VersionBumpType,
         assert_uniform_version: bool = True,
         github_actions_output: bool = True) -> None:
    if any(filter(lambda x: x.name != "pom.xml", project_root_poms)):
        raise AssertionError(f"Currently, only Maven projects ('pom.xml') are supported by this operation. Sorry.")

    project: XmlMavenProject = XmlMavenProject()
    module_reader: XmlMavenModuleReader = XmlMavenModuleReader()

    for project_root_pom in project_root_poms:
        project.add_modules(*module_reader.read_recursive(project_root_pom))

    if github_actions_output:
        versions: Dict[XmlMavenModule, str] = project.get_module_versions()
        unique_versions: List[str] = list(set(versions.values()))

        if len(unique_versions) == 1:
            print(f"::set-output name=old_version::{unique_versions[0]}", file=sys.stdout)

        else:
            print(f"::set-output name=old_version::undefined", file=sys.stdout)

    project.bump_version(bump_type, assert_uniform_version=assert_uniform_version, write_modules=True)

    if github_actions_output:
        versions: Dict[XmlMavenModule, str] = project.get_module_versions()
        unique_versions: List[str] = list(set(versions.values()))

        if len(unique_versions) == 1:
            print(f"::set-output name=new_version::{unique_versions[0]}", file=sys.stdout)

        else:
            print(f"::set-output name=new_version::undefined", file=sys.stdout)


def main() -> None:
    argument_parser: ArgumentParser = ArgumentParser("Script to manage Maven project versions")

    sub_parsers: Any = argument_parser.add_subparsers(dest="subparser")

    # region bump command

    bump_parser: ArgumentParser = sub_parsers.add_parser("bump", help="Bumps a Maven project version.")
    bump_parser.add_argument("--bump-type",
                             type=str,
                             required=True,
                             help=f"Available values: '{XmlMavenProject.VersionBumpType.MAJOR}', "
                                  f"'{XmlMavenProject.VersionBumpType.MINOR}', "
                                  f"and '{XmlMavenProject.VersionBumpType.PATCH}'")
    bump_parser.add_argument("--accept-non-uniform-versions",
                             action="store_false",
                             required=False,
                             help="Indicates whether the version bump should even be performed if the project contains "
                                  "different versions. "
                                  "Note: ALL module versions will be increased if this option is enabled.")
    bump_parser.add_argument("--no-github-action-outputs",
                             action="store_true",
                             required=False,
                             help="Indicates whether the script should NOT set the GitHub action outputs.")
    bump_parser.add_argument("pom",
                             type=Path,
                             nargs="+")

    # endregion

    parsed_args: Any = argument_parser.parse_args()
    if parsed_args.subparser == "bump":
        bump(parsed_args.pom,
             XmlMavenProject.VersionBumpType[parsed_args.bump_type.upper()],
             not parsed_args.accept_non_uniform_versions,
             not parsed_args.no_github_action_outputs)


if __name__ == "__main__":
    main()
