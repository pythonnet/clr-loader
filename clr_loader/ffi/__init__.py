import os
import shutil

import cffi

from . import coreclr, hostfxr, mono

__all__ = ["ffi", "load_coreclr", "load_hostfxr", "load_mono"]

ffi = cffi.FFI()

for cdef in coreclr.cdef + hostfxr.cdef + mono.cdef:
    ffi.cdef(cdef)


def load_coreclr(runtime):
    dll_name = _get_dll_name("coreclr")
    dll_path = os.path.join(runtime.path, dll_name)
    return ffi.dlopen(dll_path)


def load_hostfxr(dotnet_root):
    hostfxr_version = "3.0.0"
    hostfxr_name = _get_dll_name("hostfxr")
    hostfxr_path = os.path.join(
        dotnet_root, "host", "fxr", hostfxr_version, hostfxr_name
    )

    return ffi.dlopen(hostfxr_path)


def load_mono(path=None, gc=None):
    if path is None:
        from ctypes.util import find_library

        path = find_library(f"mono{gc or ''}-2.0")
        if path is None:
            raise RuntimeError("Could not find libmono")

    return ffi.dlopen(path)


def _get_dll_name(name):
    import sys

    if sys.platform == "win32":
        return f"{name}.dll"
    elif sys.platform == "darwin":
        return f"lib{name}.dylib"
    else:
        return f"lib{name}.so"
