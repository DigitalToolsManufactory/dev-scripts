from typing import cast
from unittest import TestCase

from development_environment.formatter_configuration import (
    FormatterConfiguration,
    FormatterType,
    MavenFormatterConfiguration,
    NullFormatterConfiguration,
    VenvFormatterConfiguration,
)


class TestFormatterConfiguration(TestCase):
    def test_maven_configuration_from_json(self) -> None:
        config: FormatterConfiguration = FormatterConfiguration.from_json(
            """{
    "formatter_type": "mvn",
    "goals": [
        "formatter:format",
        "impsort:sort",
        "com.github.ekryd.sortpom:sortpom-maven-plugin:sort"
    ],
    "excluded_modules": [
        "bom",
        "modules-bom"
    ],
    "additional_arguments": [
        "-DskipTests"
    ]
}"""
        )

        self.assertIsInstance(config, MavenFormatterConfiguration)
        sut: MavenFormatterConfiguration = cast(MavenFormatterConfiguration, config)

        self.assertEqual(sut.formatter_type, FormatterType.MAVEN)
        self.assertListEqual(
            sut.goals,
            [
                "formatter:format",
                "impsort:sort",
                "com.github.ekryd.sortpom:sortpom-maven-plugin:sort",
            ],
        )
        self.assertListEqual(sut.excluded_modules, ["bom", "modules-bom"])
        self.assertListEqual(sut.additional_arguments, ["-DskipTests"])

    def test_venv_configuration_from_json(self) -> None:
        config: FormatterConfiguration = FormatterConfiguration.from_json(
            """{
    "formatter_type": "venv",
    "goals": [
        "black",
        "isort --profile black"
    ]
}"""
        )

        self.assertIsInstance(config, VenvFormatterConfiguration)
        sut: VenvFormatterConfiguration = cast(VenvFormatterConfiguration, config)

        self.assertEqual(sut.formatter_type, FormatterType.VENV)
        self.assertListEqual(sut.goals, ["black", "isort --profile black"])

    def test_maven_configuration_to_json(self) -> None:
        sut: MavenFormatterConfiguration = MavenFormatterConfiguration(
            [
                "formatter:format",
                "impsort:sort",
                "com.github.ekryd.sortpom:sortpom-maven-plugin:sort",
            ],
            ["bom", "modules-bom"],
            ["-DskipTests"],
        )

        self.assertEqual(
            sut.to_json(),
            """{
    "formatter_type": "mvn",
    "goals": [
        "formatter:format",
        "impsort:sort",
        "com.github.ekryd.sortpom:sortpom-maven-plugin:sort"
    ],
    "excluded_modules": [
        "bom",
        "modules-bom"
    ],
    "additional_arguments": [
        "-DskipTests"
    ]
}""",
        )

    def test_venv_configuration_to_json(self) -> None:
        sut: VenvFormatterConfiguration = VenvFormatterConfiguration(
            ["black", "isort --profile black"]
        )

        self.assertEqual(
            sut.to_json(),
            """{
    "formatter_type": "venv",
    "goals": [
        "black",
        "isort --profile black"
    ]
}""",
        )

    def test_null_configuration_from_json(self) -> None:
        config: FormatterConfiguration = FormatterConfiguration.from_json(
            """{"formatter_type": "foobar"}"""
        )

        self.assertIsInstance(config, NullFormatterConfiguration)
        sut: NullFormatterConfiguration = cast(NullFormatterConfiguration, config)

        self.assertEqual(sut.formatter_type, FormatterType.NULL)
