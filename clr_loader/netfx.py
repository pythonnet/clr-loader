import atexit
from typing import Optional, Any
from .ffi import ffi, load_netfx

_FW: Optional[Any] = None


class NetFx:
    def __init__(self, name: Optional[str] = None, config_file: Optional[str] = None):
        initialize()
        self._domain = _FW.pyclr_create_appdomain(
            name or ffi.NULL, config_file or ffi.NULL
        )

    def get_callable(self, assembly_path: str, typename: str, function: str):
        func = _FW.pyclr_get_function(
            self._domain,
            assembly_path.encode("utf8"),
            typename.encode("utf8"),
            function.encode("utf8"),
        )

        return func

    def __del__(self):
        if self._domain and _FW:
            _FW.pyclr_close_appdomain(self._domain)


def initialize():
    global _FW
    if _FW is not None:
        return

    _FW = load_netfx()
    _FW.pyclr_initialize()

    atexit.register(_release)


def _release():
    global _FW
    if _FW is not None:
        _FW.pyclr_finalize()
        _FW = None
