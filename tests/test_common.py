import shutil
import pytest
from subprocess import check_call
import sys
from pathlib import Path


@pytest.fixture(scope="session")
def example_netstandard(tmpdir_factory):
    return build_example(tmpdir_factory, "netstandard20")


@pytest.fixture(scope="session")
def example_netcore(tmpdir_factory):
    return build_example(tmpdir_factory, "net60")


def build_example(tmpdir_factory, framework):
    out = Path(tmpdir_factory.mktemp(f"example-{framework}"))
    proj_path = Path(__file__).parent.parent / "example" / "example.csproj"

    check_call(["dotnet", "build", str(proj_path), "-o", str(out), "-f", framework])

    return out


def test_mono(example_netstandard: Path):
    from clr_loader import get_mono

    mono = get_mono()
    asm = mono.get_assembly(example_netstandard / "example.dll")

    run_tests(asm)


def test_mono_debug(example_netstandard: Path):
    from clr_loader import get_mono

    mono = get_mono(
        debug=True,
        jit_options=[
            "--debugger-agent=address=0.0.0.0:5831,transport=dt_socket,server=y"
        ],
    )
    asm = mono.get_assembly(example_netstandard / "example.dll")

    run_tests(asm)


def test_mono_signal_chaining(example_netstandard: Path):
    from clr_loader import get_mono

    mono = get_mono(set_signal_chaining=True)
    asm = mono.get_assembly(example_netstandard / "example.dll")

    run_tests(asm)


def test_mono_set_dir(example_netstandard: Path):
    from clr_loader import get_mono

    mono = get_mono(assembly_dir="/usr/lib", config_dir="/etc")
    asm = mono.get_assembly(example_netstandard / "example.dll")

    run_tests(asm)


def test_coreclr(example_netcore: Path):
    from clr_loader import get_coreclr

    coreclr = get_coreclr(runtime_config=example_netcore / "example.runtimeconfig.json")
    asm = coreclr.get_assembly(example_netcore / "example.dll")

    run_tests(asm)


def test_coreclr_command_line(example_netcore: Path):
    run_in_subprocess(_do_test_coreclr_command_line, example_netcore)


def _do_test_coreclr_command_line(example_netcore):
    from clr_loader import get_coreclr_command_line

    coreclr = get_coreclr_command_line(entry_dll=example_netcore / "example.dll")
    asm = coreclr.get_assembly(example_netcore / "example.dll")

    run_tests(asm)


def test_coreclr_properties(example_netcore: Path):
    run_in_subprocess(
        _do_test_coreclr_autogenerated_runtimeconfig,
        example_netstandard,
        properties=dict(APP_CONTEXT_BASE_DIRECTORY=str(example_netcore)),
    )


def test_coreclr_autogenerated_runtimeconfig(example_netstandard: Path):
    run_in_subprocess(_do_test_coreclr_autogenerated_runtimeconfig, example_netstandard)


def _do_test_coreclr_autogenerated_runtimeconfig(
    example_netstandard: Path, **properties
):
    from clr_loader import get_coreclr

    coreclr = get_coreclr(properties=properties)
    asm = coreclr.get_assembly(example_netstandard / "example.dll")

    run_tests(asm)


@pytest.mark.skipif(
    sys.platform != "win32", reason=".NET Framework only exists on Windows"
)
def test_netfx(example_netstandard: Path):
    run_in_subprocess(_do_test_netfx, example_netstandard)


@pytest.mark.skipif(
    sys.platform != "win32", reason=".NET Framework only exists on Windows"
)
def test_netfx_chinese_path(example_netstandard: Path, tmpdir_factory):
    tmp_path = Path(tmpdir_factory.mktemp("example-中国"))
    shutil.copytree(example_netstandard, tmp_path, dirs_exist_ok=True)

    run_in_subprocess(_do_test_netfx, tmp_path)


@pytest.mark.skipif(
    sys.platform != "win32", reason=".NET Framework only exists on Windows"
)
def test_netfx_separate_domain(example_netstandard):
    run_in_subprocess(_do_test_netfx, example_netstandard, domain="some domain")


def _do_test_netfx(example_netstandard, **kwargs):
    from clr_loader import get_netfx

    netfx = get_netfx(**kwargs)
    asm = netfx.get_assembly(example_netstandard / "example.dll")

    run_tests(asm)


def run_tests(asm):
    func = asm.get_function("Example.TestClass", "Test")
    test_data = b"testy mctestface"
    res = func(test_data)
    assert res == len(test_data)


def run_in_subprocess(func, *args, **kwargs):
    from multiprocessing import get_context

    p = get_context("spawn").Process(target=func, args=args, kwargs=kwargs)
    p.start()
    p.join()
    p.close()
