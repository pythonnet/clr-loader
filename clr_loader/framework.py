from .ffi import ffi, load_framework


_FW = None


class Framework:
    def __init__(self, name=None, config_file=None):
        global _FW
        if _FW is None:
            _FW = load_framework()

        self._domain = _FW.pyclr_create_appdomain(
            name or ffi.NULL, config_file or ffi.NULL
        )

    def get_callable(self, assembly_path, typename, function):
        func = _FW.pyclr_get_function(
            self._domain,
            assembly_path.encode("utf8"),
            typename.encode("utf8"),
            function.encode("utf8"),
        )

        return ffi.cast("entry_point*", func)
    
    def __del__(self):
        if self._domain and _FW:
            _FW.pyclr_close_appdomain(self._domain)
