import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, Union, ClassVar, List

from varname import nameof


@dataclass(frozen=True)
class GitRemote:
    name: str
    head_branch: Optional[str]


@dataclass(frozen=True)
class GitConfiguration:
    remotes: Optional[List[GitRemote]] = None

    FILE_NAME: ClassVar[str] = "git-configuration.json"

    @staticmethod
    def load(directory: Optional[Path]) -> "GitConfiguration":
        if directory is None:
            return GitConfiguration()

        file: Path = Path(directory, GitConfiguration.FILE_NAME)
        if not file.is_file():
            return GitConfiguration()

        return GitConfiguration.from_json(file.read_text())

    @staticmethod
    def from_json(content: Union[str, Dict[str, Any]]) -> "GitConfiguration":
        if isinstance(content, str):
            data: Dict[str, Any] = json.loads(content)

        elif isinstance(content, Dict):
            data: Dict[str, Any] = content

        else:
            raise TypeError(f"The given 'content' ({content}) must be of type 'str' or 'dict'")

        remotes: Optional[List[GitRemote]] = None
        if nameof(GitConfiguration.remotes) in data:
            remotes = []
            for item in data[nameof(GitConfiguration.remotes)]:
                remotes.append(GitRemote(**item))

        return GitConfiguration(remotes)
