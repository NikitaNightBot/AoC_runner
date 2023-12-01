"""
A python module for running AOC solutions with a certain project structure being:

solutions/
    year/
        problem_num/
            input # problem input file, the file handle object (TextIOWrapper) will be automatically provided as the 1st positional arg (after cls)
            solution.py 
                # 
                class Solution:
                    @classmethod
                    def part_1(cls, file)

                    @classmethod
                    def part_2(cls, file)
                #

Run via: run.py {year} {problem_num} {part} [you can provide additional args and kwargs]
"""

import fire
import importlib.util
import sys
import os
import pathlib
import pyperclip
import rgbprint
import time
from typing import Any
from types import ModuleType

ENV_VAR_NAME: str = "AOC_SOLUTION_DIRECTORY_PATH"
try:
    SOLUTION_DIRECTORY_PATH = pathlib.Path(os.environ[ENV_VAR_NAME]).resolve()
except KeyError:
    raise KeyError(f"Set the \x1B[38;5;129m$ENV:{ENV_VAR_NAME}\x1B[39m environment variable to be the path to the directory with your python solutions." )


def pretty_print(
    *objects: Any,
    sep: str = " ",
    end: str = "\n",
    start_color: rgbprint.Color = rgbprint.Color.aqua_marine,
    end_color: rgbprint.Color = rgbprint.Color.magenta,
) -> None:
    rgbprint.gradient_print(
        *objects,
        sep=sep,
        end=end,
        start_color=start_color,
        end_color=end_color
    )


def import_by_path(path: str | pathlib.Path, name: str = "<dynamic>") -> ModuleType:
    """
    Function for dynamic loading of modules by an absolute path, slightly cursed
    """
    spec = importlib.util.spec_from_file_location(
        name, str(path)
    )  # str(path) incase path is a pathlib path
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def run(
    year: int,
    problem_num: int,
    part: int,
    inputname: str = "input",
    classname: str = "Solution",
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] = {},
) -> None:
    # Relying on a certain file structure to get the files based on arguments
    problem_directory = SOLUTION_DIRECTORY_PATH / str(year) / str(problem_num)
    solution_file_path = problem_directory / "solution.py"
    problem_input_file_path = problem_directory / inputname

    # Dynamically loading the module with the solution & gettattring the function from it
    solution_module = import_by_path(solution_file_path)
    solution_class = getattr(solution_module, classname)
    part_function = getattr(solution_class, f"part_{part}")

    # Running the solution, providing the input file handle as first argument
    problem_file = problem_input_file_path.open()
    start_time = time.perf_counter()
    solution_result = part_function(problem_file, *args, **kwargs)
    delta_time = time.perf_counter() - start_time

    pretty_print(
        f"Running {solution_file_path}\nYear: {year}\nProblem: {problem_num}\nPart: {part}\nTime taken: {delta_time}s\nResult: {solution_result!r}"
    )
    pyperclip.copy(repr(solution_result))

    problem_file.close()

def main() -> None:
    # Intended to be run directly.
    fire.Fire(run)

if __name__ == "__main__":
    main()
