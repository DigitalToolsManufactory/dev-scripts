from dataclasses import dataclass
from subprocess import Popen
from typing import List, Union


@dataclass(frozen=True)
class ShellResponse:
    command_line: str
    exit_code: int
    stdout: str
    stderr: str

    @property
    def is_success(self) -> bool:
        return self.exit_code == 0

    def get_stdout_lines(self) -> List[str]:
        result: List[str] = []
        for line in [line.strip() for line in self.stdout.split("\n")]:
            if len(line) > 0:
                result.append(line)

        return result

    def get_stderr_lines(self) -> List[str]:
        result: List[str] = []
        for line in [line.strip() for line in self.stderr.split("\n")]:
            if len(line) > 0:
                result.append(line)

        return result

    @staticmethod
    def from_process(
        process: Popen, stdout: Union[str, List[str]], stderr: Union[str, List[str]]
    ) -> "ShellResponse":
        actual_stdout: str = stdout if isinstance(stdout, str) else "\n".join(stdout)
        actual_stderr: str = stderr if isinstance(stderr, str) else "\n".join(stderr)

        return ShellResponse(
            ShellResponse._assemble_command_line(process),
            process.returncode,
            actual_stdout,
            actual_stderr,
        )

    @staticmethod
    def _assemble_command_line(process: Popen) -> str:
        non_empty_arguments: List[str] = []
        for argument in [argument.strip() for argument in process.args]:
            if len(argument) > 0:
                non_empty_arguments.append(argument)

        arguments: List[str] = []
        for argument in non_empty_arguments:
            command_line_argument: str = argument

            if " " in command_line_argument:
                command_line_argument = f'"{command_line_argument}"'

            arguments.append(command_line_argument)

        return " ".join(arguments)
