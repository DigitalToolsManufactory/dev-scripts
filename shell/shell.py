import platform
import subprocess
from pathlib import Path
from subprocess import Popen
from typing import Callable, List, Optional, Union

from shell.shell_response import ShellResponse


class DefaultShell:
    @staticmethod
    def new() -> "Shell":
        system: str = platform.system()
        if system == "Windows":
            return WindowsShell()

        return Shell()

    def __int__(self):
        raise AssertionError("This utility class must not be instantiated.")


class Shell:
    def run_or_raise(
        self,
        command: str,
        arguments: Optional[List[str]] = None,
        working_directory: Optional[Path] = None,
        exception: Optional[
            Union[Exception, Callable[[ShellResponse], Exception]]
        ] = None,
    ) -> ShellResponse:
        response: ShellResponse = self.run(command, arguments, working_directory)
        if response.is_success:
            return response

        if exception is None:
            raise Exception(
                f"The command '{response.command_line}' returned {response.exit_code}:\n"
                f"stdout:\n'{response.stdout}'\n"
                f"stderr:\n'{response.stderr}'"
            )

        if isinstance(exception, Exception):
            raise exception

        raise exception(response)

    def run(
        self,
        command: str,
        arguments: Optional[List[str]] = None,
        working_directory: Optional[Path] = None,
    ) -> ShellResponse:
        process_arguments: List[str] = self._assemble_process_arguments(
            command, arguments
        )
        directory: Path = (
            working_directory.resolve() if working_directory else Path(".").resolve()
        )

        return self._execute(process_arguments, directory)

    def _assemble_process_arguments(
        self, command: str, arguments: Optional[List[str]] = None
    ) -> List[str]:
        result: List[str] = [command]
        if arguments:
            result.extend([argument for argument in arguments if len(argument) > 0])

        return result

    def _execute(self, arguments: List[str], working_directory: Path) -> ShellResponse:
        process: Popen = Popen(
            arguments,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=working_directory,
        )

        stdout, stderr = process.communicate()

        return ShellResponse.from_process(process, stdout, stderr)


class WindowsShell(Shell):
    def _assemble_process_arguments(
        self, command: str, arguments: Optional[List[str]] = None
    ) -> List[str]:
        result: List[str] = ["cmd", "/c", command]
        if arguments:
            result.extend([argument for argument in arguments if len(argument) > 0])

        return result
