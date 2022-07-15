import re
import xml.etree.ElementTree
from enum import Enum
from pathlib import Path
from re import Match
from typing import List, Dict, Optional, Pattern

from java.maven.maven_module import MavenModule
from java.maven.xml_maven_project import XmlMavenProject
from utility.type_utility import get_or_else
from utility.xml.e_tree_xml_document import ETreeXmlDocument

_SEMANTIC_VERSION_PATTERN: Pattern = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")


class VersionBumpType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


def bump_version(project_files: List[Path], bump_type: VersionBumpType) -> None:
    if any(filter(lambda x: x.name != "pom.xml", project_files)):
        print(f"Currently, only Maven projects are supported. Sorry 😞")
        return

    xml.etree.ElementTree.register_namespace("", "foo")

    project: XmlMavenProject = XmlMavenProject()
    for project_file in project_files:
        project.append_module_tree(ETreeXmlDocument(project_file))

    old_module_versions: Dict[str, str] = {}
    for module in project.modules:
        old_module_versions = _collect_current_versions(module, old_module_versions)

    new_module_versions: Dict[str, str] = {k: _bump_version(v, bump_type) for k, v in old_module_versions.items()}
    for module in project.modules:
        _update_versions(module, new_module_versions)

    project.save()


def _collect_current_versions(module: MavenModule, module_versions: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    result: Dict[str, str] = get_or_else(module_versions, {})

    result[f"{module.identifier.group_id}:{module.identifier.artifact_id}"] = module.identifier.version
    for sub_module in module.modules:
        result = _collect_current_versions(sub_module, result)

    return result


def _bump_version(version: str, bump_type: VersionBumpType) -> str:
    match: Match = _SEMANTIC_VERSION_PATTERN.match(version)
    if match is None:
        raise AssertionError(f"The version '{version}' is not a valid semantic version")

    major: int = int(match.group("major"))
    minor: int = int(match.group("minor"))
    patch: int = int(match.group("patch"))

    if bump_type == VersionBumpType.MAJOR:
        major += 1
        minor = 0
        patch = 0

    elif bump_type == VersionBumpType.MINOR:
        minor += 1
        patch = 0

    elif bump_type == VersionBumpType.PATCH:
        patch += 1

    return f"{major}.{minor}.{patch}"


def _update_versions(module: MavenModule, module_versions: Dict[str, str]) -> None:
    module_ga: str = f"{module.identifier.group_id}:{module.identifier.artifact_id}"
    module.identifier.set_version(module_versions[module_ga])

    if module.parent_identifier is not None:
        ga: str = f"{module.parent_identifier.group_id}:{module.parent_identifier.artifact_id}"
        if ga in module_versions:
            module.parent_identifier.set_version(module_versions[ga])

    for dependency in module.dependencies:
        ga: str = f"{dependency.group_id}:{dependency.artifact_id}"
        if ga in module_versions:
            dependency.set_version(module_versions[ga])

    for sub_module in module.modules:
        _update_versions(sub_module, module_versions)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
