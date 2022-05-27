from pathlib import Path
from sys import platform
from typing import List


def bootstrap_windows_commands() -> None:
    current_path: Path = Path(__file__).parent.resolve().absolute()
    template_path: Path = Path(current_path, "dev-scripts.template.ps1")
    scripts_path: Path = Path(current_path, "dev-scripts.ps1")

    with template_path.open("r") as f:
        lines: List[str] = f.readlines()

    current_path_as_string: str = str(current_path).replace("\\", "/")
    lines[0] = f"$__scripts_path = \"{current_path_as_string}\"\n"

    with scripts_path.open("w") as f:
        f.writelines(lines)


def main() -> None:
    if platform == "win32":
        bootstrap_windows_commands()


if __name__ == "__main__":
    main()
