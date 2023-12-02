import datetime
import rich
from dataclasses import dataclass
from typing import NoReturn, Any


@dataclass
class Logger:
    @staticmethod
    def fmt(prefix: str, *objects, **kwargs) -> None:
        rich.print(
            f"{datetime.datetime.now()} | [{prefix}]{(' | '+', '.join(repr(thing) for thing in objects)) * bool(objects)}{((' | '+repr(kwargs)))*bool(kwargs)}"
        )

    def info(self, *objects: Any, **kwargs: Any) -> None:
        self.fmt("INFO", *objects, **kwargs)

    def error(self, error_type: Exception, *objects: Any, **kwargs: Any) -> NoReturn:
        self.fmt(f"ERROR:{error_type}", *objects, **kwargs)
        raise error_type
