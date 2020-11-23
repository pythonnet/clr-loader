import pytest
from subprocess import check_call
import os
import sys


@pytest.fixture(scope="session")
def example_netstandard(tmpdir_factory):
    return build_example(tmpdir_factory, "netstandard20")

@pytest.fixture(scope="session")
def example_netcore(tmpdir_factory):
    return build_example(tmpdir_factory, "netcoreapp31")

def build_example(tmpdir_factory, framework):
    out = str(tmpdir_factory.mktemp(f"example-{framework}"))
    proj_path = os.path.join(os.path.dirname(__file__), "../example")

    check_call(["dotnet", "build", proj_path, "-o", out, "-f", framework])

    return out


def test_mono(example_netstandard):
    from clr_loader import get_mono

    if sys.platform == 'win32':
        if sys.maxsize > 2**32:
            prog_files = os.environ.get("ProgramFiles")
        else:
            prog_files = os.environ.get("ProgramFiles(x86)")

        path = fr"{prog_files}\Mono\bin\mono-2.0-sgen.dll"

    elif sys.platform == "darwin":
        path = "/Library/Frameworks/Mono.framework/Versions/Current/lib/libmono-2.0.dylib"

    else:
        path = None

    mono = get_mono(path=path)
    asm = mono.get_assembly(os.path.join(example_netstandard, "example.dll"))

    run_tests(asm)


def test_coreclr(example_netcore):
    from clr_loader import get_coreclr

    coreclr = get_coreclr(os.path.join(example_netcore, "example.runtimeconfig.json"))
    asm = coreclr.get_assembly(os.path.join(example_netcore, "example.dll"))

    run_tests(asm)


@pytest.mark.skipif(sys.platform != 'win32', reason=".NET Framework only exists on Windows")
def test_netfx(example_netstandard):
    from clr_loader import get_netfx

    netfx = get_netfx()
    asm = netfx.get_assembly(os.path.join(example_netstandard, "example.dll"))

    run_tests(asm)


def run_tests(asm):
    func = asm.get_function("Example.TestClass", "Test")
    test_data = b"testy mctestface"
    res = func(test_data)
    assert res == len(test_data)

