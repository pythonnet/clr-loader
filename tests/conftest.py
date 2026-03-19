from pathlib import Path
from subprocess import check_call

import pytest

NETCORE_VERSION = "net10.0"


@pytest.fixture(scope="session")
def example_netstandard(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return build_example(tmp_path_factory, "netstandard2.0")


@pytest.fixture(scope="session")
def example_netcore(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return build_example(tmp_path_factory, NETCORE_VERSION)


def build_example(tmp_path_factory: pytest.TempPathFactory, framework: str) -> Path:
    out = tmp_path_factory.mktemp(f"example-{framework}")
    proj_path = Path(__file__).parent.parent / "example" / "example.csproj"

    _ = check_call(["dotnet", "build", str(proj_path), "-o", str(out), "-f", framework])

    return out
