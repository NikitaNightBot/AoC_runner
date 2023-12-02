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

The part_{n} methods can also accept an optional `logger` (structlog) argument.

Run via: run.py {year} {problem_num} {part} [you can provide additional args and kwargs]
"""

import fire
import logger
import importlib.util
import sys
import os
import pathlib
import pyperclip
import time
import ast
from typing import Any, Callable, TypeVar
from types import ModuleType

T: TypeVar = TypeVar("T")

LOGGER: logger.Logger = logger.Logger()  # Configuring left to the user xd

LOG_ARG_NAME: str = "logger"  # optional argument for solution functions
SOLUTION_ENV_VAR_NAME: str = "AOC_SOLUTION_DIRECTORY_PATH"

if SOLUTION_ENV_VAR_NAME in os.environ:
    SOLUTION_DIRECTORY_PATH = pathlib.Path(os.environ[SOLUTION_ENV_VAR_NAME]).resolve()
else:
    raise KeyError(
        f"Set the \x1B[38;5;129m$ENV:{SOLUTION_ENV_VAR_NAME}\x1B[39m environment variable to be the path to the directory with your python solutions."
    )

DEP_VAR_NAME: str = "AOC_SOLUTION_DEPENDENCY_PATHS"
SOLUTION_DEPENDENCIES: list[str] = ast.literal_eval(os.environ.get(DEP_VAR_NAME, "[]"))


def name_in_function(function: Callable[..., T], arg_name: str) -> bool:
    return arg_name in function.__code__.co_varnames


def add_import_paths(*paths: (str | pathlib.Path) | list[str | pathlib.Path]) -> None:
    for path_s in paths:
        if isinstance(path_s, (str, pathlib.Path)):
            path = str(path_s)

            if pathlib.Path(path).exists():
                LOGGER.info()
            else:
                LOGGER.error()

            if path not in sys.path:
                sys.path.append(path)
        else:
            for path in path_s:
                add_import_paths(path)


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
    if problem_directory.exists():
        LOGGER.info()
    else:
        LOGGER.error()

    add_import_paths(SOLUTION_DEPENDENCIES, problem_directory)

    solution_file_path = problem_directory / "solution.py"
    problem_input_file_path = problem_directory / inputname

    # Dynamically loading the module with the solution & gettattring the function from it
    solution_module = import_by_path(solution_file_path)
    solution_class = getattr(solution_module, classname)
    part_function = getattr(solution_class, f"part_{part}")
    if name_in_function(
        part_function, LOG_ARG_NAME
    ):  # if the function expects a logger: add it to the kwargs dict
        kwargs |= {LOG_ARG_NAME: LOGGER}

    # Running the solution, providing the input file handle as first argument
    problem_file = problem_input_file_path.open()
    start_time = time.perf_counter()
    LOGGER.info(f"Running {solution_file_path}")
    solution_result = part_function(problem_file, *args, **kwargs)
    delta_time = time.perf_counter() - start_time
    LOGGER.info(f"Finished in {delta_time*1000}ms")
    LOGGER.info(year=year, problem_num=problem_num, part=part, result=solution_result)

    pyperclip.copy(repr(solution_result))

    problem_file.close()


def main() -> None:
    # Intended to be run directly.
    fire.Fire(run)


if __name__ == "__main__":
    main()
