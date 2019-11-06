import os
from collections import namedtuple
from subprocess import check_output

__all__ = ["Runtime", "get_runtimes"]


Runtime = namedtuple("Runtime", "name version path")


def get_runtimes():  # -> List[Runtime]
    runtimes_l = check_output(["dotnet", "--list-runtimes"])
    runtimes_l = runtimes_l.decode("utf8").splitlines()

    runtimes = []

    for line in runtimes_l:
        name, version, path = line.split(" ", 2)
        path = os.path.join(path[1:-1], version)
        runtimes.append(Runtime(name=name, version=version, path=path))

    return runtimes
