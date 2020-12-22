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
        if sys.maxsize > 2 ** 32:
            prog_files = os.environ.get("ProgramFiles")
        else:
            prog_files = os.environ.get("ProgramFiles(x86)")

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
