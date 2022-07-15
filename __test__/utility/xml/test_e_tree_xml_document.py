from pathlib import Path
from typing import Optional
from unittest import TestCase

from utility.xml.e_tree_xml_document import ETreeXmlDocument
from utility.xml.xml_node import XmlNode


class TestETreeXmlDocument(TestCase):
    RESOURCES: Path = Path(Path(__file__).parent, "resources")

    def test_init_with_minimal_pom(self) -> None:
        sut: ETreeXmlDocument = ETreeXmlDocument(Path(self.RESOURCES, "minimal_pom.xml"))

        self.assertIsNotNone(sut)

    def test_find_root_node(self) -> None:
        sut: ETreeXmlDocument = ETreeXmlDocument(Path(self.RESOURCES, "minimal_pom.xml"))

        self.assertIsNotNone(sut.try_find_node("project"))

    def test_find_node_matches_first_occurrence(self) -> None:
        sut: ETreeXmlDocument = ETreeXmlDocument(Path(self.RESOURCES, "minimal_pom.xml"))

        first_module_node: Optional[XmlNode] = sut.try_find_node("project", "modules", "module")

        self.assertIsNotNone(first_module_node)
        self.assertEqual(first_module_node.value, "my-first-module")

    def test_find_root_node_with_namespace(self) -> None:
        sut: ETreeXmlDocument = ETreeXmlDocument(Path(self.RESOURCES, "minimal_pom_with_namespace.xml"))

        self.assertIsNotNone(sut.try_find_node("project"))

    def test_find_node_with_namespace_matches_first_occurrence(self) -> None:
        sut: ETreeXmlDocument = ETreeXmlDocument(Path(self.RESOURCES, "minimal_pom_with_namespace.xml"))

        first_module_node: Optional[XmlNode] = sut.try_find_node("project", "modules", "module")

        self.assertIsNotNone(first_module_node)
        self.assertEqual(first_module_node.value, "my-first-module")
