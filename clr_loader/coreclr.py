import glob
import os
import sys

from .ffi import ffi, load_coreclr
from .util import check_result

__all__ = ["CoreClr"]


class _CoreClr:
    _loaded = False
    _shutdown = False

    def __init__(self, runtime, app_paths=None):
        if self._loaded or self._shutdown:
            raise RuntimeError("CoreClr can only be loaded once")

        self._coreclr = load_coreclr(runtime)

        handle = ffi.new("void **")
        domain = ffi.new("unsigned *")

        if app_paths is None:
            app_paths = os.path.abspath(".")

        if isinstance(app_paths, str):
            app_paths = [app_paths]

        properties = {
            "APP_PATHS": os.pathsep.join(app_paths),
            "APP_NI_PATHS": os.pathsep.join(app_paths),
            "TRUSTED_PLATFORM_ASSEMBLIES": os.pathsep.join(
                glob.glob(runtime.path + "/*.dll")
            ),
        }

        err_code = self._coreclr.coreclr_initialize(
            sys.executable.encode("utf8"),
            b"clr_loader",
            len(properties),
            list(ffi.new("char[]", i.encode("utf8")) for i in properties.keys()),
            list(ffi.new("char[]", i.encode("utf8")) for i in properties.values()),
            handle,
            domain,
        )

        check_result(err_code)

        self._handle = handle[0]
        self._domain = domain[0]
        self._loaded = True

    def get_callable(self, assembly, klass, function):
        if self._loaded and not self._shutdown:
            func_ptr = ffi.new("void**")

            err_code = self._coreclr.coreclr_create_delegate(
                self._handle,
                self._domain,
                assembly.encode("utf8"),
                klass.encode("utf8"),
                function.encode("utf8"),
                func_ptr,
            )

            check_result(err_code)

            # TODO: Check signature somehow?
            return ffi.cast("int (*func)()", func_ptr[0])

        else:
            raise RuntimeError("CoreClr is not loaded or shut down")

    def shutdown(self):
        if self._loaded and not self._shutdown:
            err_code = self._coreclr.coreclr_shutdown(self._handle, self._domain)
            check_result(err_code)
            self._shutdown = True

    def __del__(self):
        self.shutdown()


# pylint: disable=C0103
def CoreClr(runtime, app_paths=None):
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = _CoreClr(runtime, app_paths=app_paths)

    return _INSTANCE


_INSTANCE = None
