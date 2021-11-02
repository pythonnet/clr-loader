import os
import os.path
import shutil
import sys


def find_dotnet_root() -> str:
    dotnet_root = os.environ.get("DOTNET_ROOT", None)
    if dotnet_root is not None:
        return dotnet_root

    if sys.platform == "win32":
        # On Windows, the host library is stored separately from dotnet.exe for x86
        prog_files = os.environ.get("ProgramFiles")
        dotnet_root = os.path.join(prog_files, "dotnet")
        if os.path.isdir(dotnet_root):
            return dotnet_root

    # Try to discover dotnet from PATH otherwise
    dotnet_path = shutil.which("dotnet")
    if not dotnet_path:
        raise RuntimeError("Can not determine dotnet root")

    try:
        # Pypy does not provide os.readlink right now
        if hasattr(os, "readlink"):
            dotnet_tmp_path = os.readlink(dotnet_path)
        else:
            dotnet_tmp_path = dotnet_path

        if os.path.isabs(dotnet_tmp_path):
            dotnet_path = dotnet_tmp_path
        else:
            dotnet_path = os.path.abspath(
                os.path.join(os.path.dirname(dotnet_path), dotnet_tmp_path)
            )
    except OSError:
        pass

    return os.path.dirname(dotnet_path)


def find_libmono(sgen: bool = True) -> str:
    unix_name = f"mono{'sgen' if sgen else ''}-2.0"
    if sys.platform == "win32":
        if sys.maxsize > 2 ** 32:
            prog_files = os.environ.get("ProgramFiles")
        else:
            prog_files = os.environ.get("ProgramFiles(x86)")

        # Ignore sgen on Windows, the main installation only contains this DLL
        path = fr"{prog_files}\Mono\bin\mono-2.0-sgen.dll"

    elif sys.platform == "darwin":
        path = (
            "/Library/Frameworks/Mono.framework/Versions/"
            "Current"
            f"/lib/lib{unix_name}.dylib"
        )

    else:
        from ctypes.util import find_library

        path = find_library(unix_name)

    if path is None:
        raise RuntimeError("Could not find libmono")

    return path
