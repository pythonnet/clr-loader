from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from os import PathLike
from typing import Any, Callable, Dict, Optional, Union

__all__ = ["StrOrPath"]

StrOrPath = Union[str, PathLike]


@dataclass
class RuntimeInfo:
    kind: str
    version: str
    initialized: bool
    shutdown: bool
    properties: Dict[str, str] = field(repr=False)

    def __str__(self) -> str:
        return (
            f"Runtime: {self.kind}\n"
            "=============\n"
            f"  Version:      {self.version}\n"
            f"  Initialized:  {self.initialized}\n"
            f"  Shut down:    {self.shutdown}\n"
            f"  Properties:\n"
            + "\n".join(
                f"    {key} = {_truncate(value, 65 - len(key))}"
                for key, value in self.properties.items()
            )
        )


class ClrFunction:
    def __init__(
        self, runtime: "Runtime", assembly: StrOrPath, typename: str, func_name: str
    ):
        self._assembly = assembly
        self._class = typename
        self._name = func_name

        self._callable = runtime.get_callable(assembly, typename, func_name)

    def __call__(self, buffer: bytes) -> int:
        from .ffi import ffi

        buf_arr = ffi.from_buffer("char[]", buffer)
        return self._callable(ffi.cast("void*", buf_arr), len(buf_arr))

    def __repr__(self) -> str:
        return f"<ClrFunction {self._class}.{self._name} in {self._assembly}>"


class Assembly:
    def __init__(self, runtime: "Runtime", path: StrOrPath):
        self._runtime = runtime
        self._path = path

    def get_function(self, name: str, func: Optional[str] = None) -> ClrFunction:
        if func is None:
            name, func = name.rsplit(".", 1)

        return ClrFunction(self._runtime, self._path, name, func)

    def __repr__(self) -> str:
        return f"<Assembly {self._path} in {self._runtime}>"


class Runtime(metaclass=ABCMeta):
    @abstractmethod
    def info(self) -> RuntimeInfo:
        pass

    def get_assembly(self, assembly_path: StrOrPath) -> Assembly:
        return Assembly(self, assembly_path)

    @abstractmethod
    def get_callable(
        self, assembly_path: StrOrPath, typename: str, function: str
    ) -> Callable[[Any, int], Any]:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass

    def __del__(self) -> None:
        self.shutdown()


def _truncate(string: str, length: int) -> str:
    if length <= 1:
        raise TypeError("length must be > 1")
    if len(string) > length - 1:
        return f"{string[:length-1]}…"
    else:
        return string
