import sys
from pathlib import Path
from typing import Optional

import cffi  # type: ignore

from . import hostfxr, mono, netfx

__all__ = ["ffi", "load_hostfxr", "load_mono", "load_netfx"]

ffi = cffi.FFI()  # type: ignore

for cdef in hostfxr.cdef + mono.cdef + netfx.cdef:
    ffi.cdef(cdef)


def load_hostfxr(dotnet_root: Path):
    hostfxr_name = _get_dll_name("hostfxr")

    # This will fail as soon as .NET hits version 10, but hopefully by then
    # we'll have a more robust way of finding the libhostfxr
    hostfxr_path = dotnet_root / "host" / "fxr"
    hostfxr_paths = hostfxr_path.glob(f"?.*/{hostfxr_name}")

    for hostfxr_path in reversed(sorted(hostfxr_paths)):
        try:
            return ffi.dlopen(str(hostfxr_path))
        except Exception:
            pass

    raise RuntimeError(f"Could not find a suitable hostfxr library in {dotnet_root}")


def load_mono(path: Optional[Path] = None):
    # Preload C++ standard library, Mono needs that and doesn't properly link against it
    if sys.platform == "linux":
        ffi.dlopen("stdc++", ffi.RTLD_GLOBAL)

    path_str = str(path) if path else None
    return ffi.dlopen(path_str, ffi.RTLD_GLOBAL)


def load_netfx():
    if sys.platform != "win32":
        raise RuntimeError(".NET Framework is only supported on Windows")

    dirname = Path(__file__).parent / "dlls"
    if sys.maxsize > 2**32:
        arch = "amd64"
    else:
        arch = "x86"

    path = dirname / arch / "ClrLoader.dll"

    return ffi.dlopen(str(path))


def _get_dll_name(name: str) -> str:
    if sys.platform == "win32":
        return f"{name}.dll"
    elif sys.platform == "darwin":
        return f"lib{name}.dylib"
    else:
        return f"lib{name}.so"
