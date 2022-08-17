import json
import re
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from re import Pattern
from typing import Any, Callable, ClassVar, Dict, List, Optional, Union

from varname import nameof

from java.maven.xml_maven_module import XmlMavenModule
from java.maven.xml_maven_module_reader import XmlMavenModuleReader
from shell.shell import Shell
from utility.type_utility import get_or_else


class FormatterType(Enum):
    NULL = "null"
    MAVEN = "mvn"
    VENV = "venv"


class FormatterConfiguration(ABC):
    FILE_NAME: ClassVar[str] = "formatter-configuration.json"

    @property
    def formatter_type(self) -> FormatterType:
        return self._get_formatter_type()

    @abstractmethod
    def _get_formatter_type(self) -> FormatterType:
        raise NotImplementedError

    # region store
    def store(self, directory: Path) -> None:
        file: Path = Path(directory, FormatterConfiguration.FILE_NAME)
        with file.open("w") as f:
            f.writelines(self.to_json())

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    def to_dict(self) -> Dict[str, Any]:
        return {
            nameof(FormatterConfiguration.formatter_type): self.formatter_type.value
        }

    # endregion

    # region load
    @staticmethod
    def load(directory: Optional[Path]) -> "FormatterConfiguration":
        if directory is None:
            return NullFormatterConfiguration()

        file: Path = Path(directory, FormatterConfiguration.FILE_NAME)
        if not file.is_file():
            return NullFormatterConfiguration()

        return FormatterConfiguration.from_json(file.read_text())

    @staticmethod
    def from_json(content: Union[str, Dict[str, Any]]) -> "FormatterConfiguration":
        if isinstance(content, str):
            data: Dict[str, Any] = json.loads(content)

        elif isinstance(content, Dict):
            data: Dict[str, Any] = content

        else:
            raise TypeError(
                f"The given 'content' ({content}) must be of type 'str' or 'dict'"
            )

        if nameof(FormatterConfiguration.formatter_type) not in data:
            raise AssertionError(
                f"The required property '{nameof(FormatterConfiguration.formatter_type)}' "
                f"cannot be found in '{content}'"
            )

        raw_formatter_type: Any = data[nameof(FormatterConfiguration.formatter_type)]
        formatter_type: FormatterType = FormatterType.NULL

        if isinstance(raw_formatter_type, str):
            if raw_formatter_type.lower() in [e.value for e in FormatterType]:
                formatter_type = FormatterType(raw_formatter_type.lower())

        if formatter_type == FormatterType.MAVEN:
            return MavenFormatterConfiguration.from_dict(data)

        if formatter_type == FormatterType.VENV:
            return VenvFormatterConfiguration.from_dict(data)

        return NullFormatterConfiguration()

    # endregion

    # region infer
    @staticmethod
    def infer(
        directory: Path, shell: Optional[Shell] = None
    ) -> "FormatterConfiguration":
        infer_functions: Dict[
            str, Callable[[Path, Optional[Shell]], "FormatterConfiguration"]
        ] = {
            "pom.xml": MavenFormatterConfiguration.infer,
            "requirements.txt": VenvFormatterConfiguration.infer,
        }

        for file_name, func in infer_functions.items():
            file: Path = Path(directory, file_name)
            if file.exists():
                return func(directory, shell)

        return NullFormatterConfiguration()

    # endregion


class NullFormatterConfiguration(FormatterConfiguration):
    def _get_formatter_type(self) -> FormatterType:
        return FormatterType.NULL


class MavenFormatterConfiguration(FormatterConfiguration):
    def __init__(
        self,
        goals: Optional[List[str]] = None,
        excluded_modules: Optional[List[str]] = None,
        additional_arguments: Optional[List[str]] = None,
    ):
        self._goals: List[str] = get_or_else(goals, list)
        self._excluded_modules: List[str] = get_or_else(excluded_modules, list)
        self._additional_arguments: List[str] = get_or_else(additional_arguments, list)

    def _get_formatter_type(self) -> FormatterType:
        return FormatterType.MAVEN

    @property
    def goals(self) -> List[str]:
        return self._goals

    @property
    def excluded_modules(self) -> List[str]:
        return self._excluded_modules

    @property
    def additional_arguments(self) -> List[str]:
        return self._additional_arguments

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = super().to_dict()
        result[nameof(MavenFormatterConfiguration.goals)] = self.goals
        result[
            nameof(MavenFormatterConfiguration.excluded_modules)
        ] = self.excluded_modules
        result[
            nameof(MavenFormatterConfiguration.additional_arguments)
        ] = self._additional_arguments

        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MavenFormatterConfiguration":
        goals: List[str] = []
        if nameof(MavenFormatterConfiguration.goals) in data:
            goals.extend(list(data[nameof(MavenFormatterConfiguration.goals)]))

        excluded_modules: List[str] = []
        if nameof(MavenFormatterConfiguration.excluded_modules) in data:
            excluded_modules.extend(
                list(data[nameof(MavenFormatterConfiguration.excluded_modules)])
            )

        additional_arguments: List[str] = []
        if nameof(MavenFormatterConfiguration.additional_arguments) in data:
            additional_arguments.extend(
                list(data[nameof(MavenFormatterConfiguration.additional_arguments)])
            )

        return MavenFormatterConfiguration(
            goals, excluded_modules, additional_arguments
        )

    @staticmethod
    def infer(
        directory: Path, shell: Optional[Shell] = None
    ) -> "MavenFormatterConfiguration":
        pom_file: Path = Path(directory, "pom.xml")
        if not pom_file.exists() or not pom_file.is_file():
            return MavenFormatterConfiguration()

        module: XmlMavenModule = XmlMavenModuleReader().read(pom_file)
        goals: List[str] = []

        def has_plugin(g: str, a: str) -> bool:
            for plugin in module.plugins:
                if plugin.group_id == g and plugin.artifact_id == a:
                    return True

            return False

        if has_plugin("net.revelc.code.formatter", "formatter-maven-plugin"):
            goals.append("net.revelc.code.formatter:formatter-maven-plugin:format")

        if has_plugin("net.revelc.code", "impsort-maven-plugin"):
            goals.append("net.revelc.code:impsort-maven-plugin:sort")

        if has_plugin("com.github.ekryd.sortpom", "sortpom-maven-plugin"):
            goals.append("com.github.ekryd.sortpom:sortpom-maven-plugin:sort")

        if len(goals) < 1:
            goals.append("process-test-sources")

        return MavenFormatterConfiguration(goals, additional_arguments=["-T1.0C"])


class VenvFormatterConfiguration(FormatterConfiguration):
    BLACK_FORMATTER: ClassVar[Pattern] = re.compile(
        r"(^|;)\s*black\s*($|==|>=|<=|~=|>|<)"
    )
    ISORT_FORMATTER: ClassVar[Pattern] = re.compile(
        r"(^|;)\s*isort\s*($|==|>=|<=|~=|>|<)"
    )

    def __init__(self, goals: Optional[List[str]] = None):
        self._goals: List[str] = get_or_else(goals, list)

    def _get_formatter_type(self) -> FormatterType:
        return FormatterType.VENV

    @property
    def goals(self) -> List[str]:
        return self._goals

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = super().to_dict()
        result[nameof(VenvFormatterConfiguration.goals)] = self.goals

        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "VenvFormatterConfiguration":
        goals: List[str] = []
        if nameof(VenvFormatterConfiguration.goals) in data:
            goals.extend(list(data[nameof(VenvFormatterConfiguration.goals)]))

        return VenvFormatterConfiguration(goals)

    @staticmethod
    def infer(
        directory: Path, shell: Optional[Shell] = None
    ) -> "VenvFormatterConfiguration":
        requirements_file: Path = Path(directory, "requirements.txt")
        if not requirements_file.exists() or not requirements_file.is_file():
            return VenvFormatterConfiguration()

        with requirements_file.open("r") as f:
            lines: List[str] = f.readlines()

        black_is_used: bool = False
        goals: List[str] = []

        for line in lines:
            if VenvFormatterConfiguration.BLACK_FORMATTER.match(line) is not None:
                black_is_used = True
                goals.append("black")
                break

        for line in lines:
            if VenvFormatterConfiguration.ISORT_FORMATTER.match(line) is not None:
                if black_is_used:
                    goals.append("isort --profile black")

                else:
                    goals.append("isort")
                break

        return VenvFormatterConfiguration(goals)
