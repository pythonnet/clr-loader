import pytest
from subprocess import check_call
import os
import sys


@pytest.fixture(scope="session")
def example_dll(tmpdir_factory):
    out = str(tmpdir_factory.mktemp("example"))
    proj_path = os.path.join(os.path.dirname(__file__), "../example")

    check_call(["dotnet", "build", proj_path, "-o", out, "-f", "netcoreapp31"])

    return out


@pytest.mark.xfail
def test_mono(example_dll):
    from clr_loader import get_mono

    mono = get_mono()
    asm = mono.get_assembly(os.path.join(example_dll, "example.dll"))

    run_tests(asm)


def test_coreclr(example_dll):
    from clr_loader import get_coreclr

    coreclr = get_coreclr(os.path.join(example_dll, "example.runtimeconfig.json"))
    asm = coreclr.get_assembly(os.path.join(example_dll, "example.dll"))

    run_tests(asm)


@pytest.mark.skipif(sys.platform != 'win32', reason=".NET Framework only exists on Windows")
def test_netfx(example_dll):
    from clr_loader import get_netfx

    netfx = get_netfx()
    asm = netfx.get_assembly(os.path.join(example_dll, "example.dll"))

    run_tests(asm)


def run_tests(asm):
    func = asm.get_function("Example.TestClass", "Test")
    test_data = b"testy mctestface"
    res = func(test_data)
    assert res == len(test_data)

