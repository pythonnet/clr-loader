from os.path import basename
from typing import Any, Optional
from .ffi import ffi

RuntimeImpl = Any


class ClrFunction:
    def __init__(
        self, runtime: RuntimeImpl, assembly: str, typename: str, func_name: str
    ):
        self._assembly = assembly
        self._class = typename
        self._name = func_name

        self._callable = runtime.get_callable(assembly, typename, func_name)

    def __call__(self, buffer: bytes) -> int:
        buf_arr = ffi.from_buffer("char[]", buffer)
        return self._callable(ffi.cast("void*", buf_arr), len(buf_arr))

    def __repr__(self) -> str:
        return f"<ClrFunction {self._class}.{self._name} in {basename(self._assembly)}>"


class Assembly:
    def __init__(self, runtime: RuntimeImpl, path: str):
        self._runtime = runtime
        self._path = path

    def get_function(self, name: str, func: Optional[str] = None) -> ClrFunction:
        if func is None:
            name, func = name.rsplit(".", 1)

        return ClrFunction(self._runtime, self._path, name, func)

    def __getitem__(self, name: str) -> ClrFunction:
        return self.get_function(name)

    def __repr__(self) -> str:
        return f"<Assembly {self._path} in {self._runtime}>"


class Runtime:
    def __init__(self, impl: RuntimeImpl):
        self._impl = impl

    def get_assembly(self, path: str) -> Assembly:
        return Assembly(self._impl, path)

    def __getitem__(self, path: str) -> Assembly:
        return self.get_assembly(path)
