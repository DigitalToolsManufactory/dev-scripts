from pathlib import Path
from unittest import TestCase

from java.maven.maven_module import MavenModule
from java.maven.maven_module_identifier import MavenModuleIdentifier
from java.maven.xml_maven_project import XmlMavenProject
from utility.xml.e_tree_xml_document import ETreeXmlDocument


class TestXmlMavenProject(TestCase):
    RESOURCES: Path = Path(Path(__file__).parent, "resources", Path(__file__).stem)

    def test_project_is_empty_by_default(self) -> None:
        sut: XmlMavenProject = XmlMavenProject()

        self.assertEqual(sut.modules, [])

    def test_read_nested_project(self) -> None:
        sut: XmlMavenProject = XmlMavenProject()

        parent_pom: Path = Path(self.RESOURCES, "nested_project", "pom.xml")
        sut.append_module_tree(ETreeXmlDocument(parent_pom))

        self.assertEqual(len(sut.modules), 1)

        parent_module: MavenModule = sut.modules[0]
        self.assertEqual(parent_module.identifier.group_id, "com.mycompany.app")
        self.assertEqual(parent_module.identifier.artifact_id, "parent")
        self.assertEqual(parent_module.identifier.version, "1.0.0")
        self.assertEqual(len(parent_module.modules), 1)

        sub_module: MavenModule = parent_module.modules[0]
        self.assertEqual(sub_module.identifier.group_id, "com.mycompany.app")
        self.assertEqual(sub_module.identifier.artifact_id, "my-first-artifact-id")
        self.assertEqual(sub_module.identifier.version, "1.0.0")
        self.assertEqual(len(sub_module.dependencies), 2)
        self.assertEqual(sub_module.parent, parent_module)

        dependency_without_version: MavenModuleIdentifier = sub_module.dependencies[0]
        self.assertEqual(dependency_without_version.group_id, "com.sample.group")
        self.assertEqual(dependency_without_version.artifact_id, "dependency")
        self.assertEqual(dependency_without_version.version, "1.33.7")

        dependency_with_version: MavenModuleIdentifier = sub_module.dependencies[1]
        self.assertEqual(dependency_with_version.group_id, "com.sample.group")
        self.assertEqual(dependency_with_version.artifact_id, "dependency-with-version")
        self.assertEqual(dependency_with_version.version, "0.42.0")
