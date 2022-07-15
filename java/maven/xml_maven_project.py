import re
from pathlib import Path
from typing import List, Optional, ClassVar, Match, Pattern

from java.maven.maven_module import MavenModule
from java.maven.maven_project import MavenProject
from java.maven.maven_property import MavenProperty
from java.maven.xml_maven_module import XmlMavenModule
from java.maven.xml_maven_module_identifier import XmlMavenModuleIdentifier
from java.maven.xml_maven_property import XmlMavenProperty
from utility.type_utility import all_defined
from utility.xml.e_tree_xml_document import ETreeXmlDocument
from utility.xml.xml_document import XmlDocument
from utility.xml.xml_node import XmlNode


class XmlMavenProject(MavenProject):
    PROPERTY_PATTERN: ClassVar[Pattern] = re.compile(r"^\$\{(?P<name>[^}]+)}$")

    def __init__(self):
        self._xml_documents: List[XmlDocument] = []
        self._modules: List[XmlMavenModule] = []

    def append_module_tree(self, xml_document: XmlDocument) -> None:
        self._xml_documents.append(xml_document)
        self._modules.append(self._read_module(xml_document))

    def _read_module(self, xml_document: XmlDocument, parent: Optional[XmlMavenModule] = None) -> XmlMavenModule:
        def read_properties() -> List[XmlMavenProperty]:
            root: Optional[XmlNode] = xml_document.try_find_node("project", "properties")
            if root is None:
                return []

            return [XmlMavenProperty(node) for node in root.nodes]

        def read_identifier(props: List[XmlMavenProperty]) -> XmlMavenModuleIdentifier:
            g: Optional[XmlNode] = xml_document.try_find_node("project", "groupId")
            a: Optional[XmlNode] = xml_document.try_find_node("project", "artifactId")
            v: Optional[XmlNode] = xml_document.try_find_node("project", "version")

            if g is None:
                if parent is None:
                    raise AssertionError("Unable to determine Maven Group Id")

                g = parent.identifier.group_id_node

            if v is None:
                if parent is None:
                    raise AssertionError("Unable to determine Maven Version")

                v = parent.identifier.version_node

            g = resolve_property(g, props)
            a = resolve_property(a, props)
            v = resolve_property(v, props)

            if not all_defined(g, a, v):
                raise AssertionError("Unable to determine Maven GAV")

            return XmlMavenModuleIdentifier(g, a, v)

        def read_dependencies(root: Optional[XmlNode],
                              props: List[XmlMavenProperty]) -> List[XmlMavenModuleIdentifier]:
            if root is None:
                return []

            result: List[XmlMavenModuleIdentifier] = []
            for node in root.nodes:
                g: Optional[XmlNode] = node.try_find_node("groupId")
                a: Optional[XmlNode] = node.try_find_node("artifactId")
                v: Optional[XmlNode] = node.try_find_node("version")

                if not all_defined(g, a, v):
                    continue

                g = resolve_property(g, props)
                a = resolve_property(a, props)
                v = resolve_property(v, props)

                result.append(XmlMavenModuleIdentifier(g, a, v))

            return result

        def get_module_documents() -> List[XmlDocument]:
            root: Optional[XmlNode] = xml_document.try_find_node("project", "modules")
            if root is None:
                return []

            result: List[XmlDocument] = []
            for module_node in root.nodes:
                path: Path = Path(xml_document.path.parent, module_node.value, "pom.xml")
                if not path.exists() or not path.is_file():
                    continue

                result.append(ETreeXmlDocument(path))

            return result

        def resolve_property(node: XmlNode, props: List[XmlMavenProperty]) -> XmlNode:
            m: Match = XmlMavenProject.PROPERTY_PATTERN.match(node.value)
            if m is None:
                # node value does not contain a Maven Property. So nothing to resolve.
                return node

            property_name: str = m.group("name")
            for p in props:
                if p.name == property_name:
                    return p.node

            maybe_property: Optional[MavenProperty] = parent.try_find_property(property_name)
            if not isinstance(maybe_property, XmlMavenProperty):
                raise AssertionError(f"Unable to resolve Maven Property '{property_name}'")

            return maybe_property.node

        properties: List[XmlMavenProperty] = read_properties()
        identifier: XmlMavenModuleIdentifier = read_identifier(properties)

        dm_root: Optional[XmlNode] = xml_document.try_find_node("project", "dependencyManagement", "dependencies")
        d_root: Optional[XmlNode] = xml_document.try_find_node("project", "dependencies")

        dependencies: List[XmlMavenModuleIdentifier] = read_dependencies(dm_root, properties)
        dependencies.extend(read_dependencies(d_root, properties))

        module: XmlMavenModule = XmlMavenModule(identifier,
                                                parent=parent,
                                                properties=properties,
                                                dependencies=dependencies)

        for sub_doc in get_module_documents():
            sub_module: XmlMavenModule = self._read_module(sub_doc, module)
            module.modules.append(sub_module)

        return module

    @property
    def has_been_modified(self) -> bool:
        return any(filter(lambda x: x.has_been_modified, self._xml_documents))

    @property
    def modules(self) -> List[MavenModule]:
        return self._modules

    def save(self) -> None:
        for doc in self._xml_documents:
            doc.save()
