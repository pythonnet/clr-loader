import os
import shutil

import cffi

from . import coreclr, hostfxr, mono

ffi = cffi.FFI()

for cdef in coreclr.cdef + hostfxr.cdef + mono.cdef:
    ffi.cdef(cdef)


def load_coreclr(runtime):
    dll_name = get_dll_name("coreclr")
    dll_path = os.path.join(runtime.path, dll_name)
    return ffi.dlopen(dll_path)


def load_hostfxr(dotnet_root):

    hostfxr_version = "3.0.0"
    hostfxr_name = get_dll_name("hostfxr")
    hostfxr_path = os.path.join(
        dotnet_root, "host", "fxr", hostfxr_version, hostfxr_name
    )

    return ffi.dlopen(hostfxr_path)


def get_dll_name(name):
    import sys

    if sys.platform == "win32":
        return f"{name}.dll"
    elif sys.platform == "darwin":
        return f"lib{name}.dylib"
    else:
        return f"lib{name}.so"
