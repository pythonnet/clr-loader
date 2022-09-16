from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Optional, Sequence

from .types import Assembly, Runtime, RuntimeInfo
from .util import StrOrPath
from .util.find import find_dotnet_root, find_libmono, find_runtimes
from .util.runtime_spec import DotnetCoreRuntimeSpec

__all__ = [
    "get_mono",
    "get_netfx",
    "get_coreclr",
    "find_dotnet_root",
    "find_libmono",
    "find_runtimes",
    "Runtime",
    "Assembly",
    "RuntimeInfo",
]


def get_mono(
    *,
    domain: Optional[str] = None,
    config_file: Optional[StrOrPath] = None,
    global_config_file: Optional[StrOrPath] = None,
    libmono: Optional[StrOrPath] = None,
    sgen: bool = True,
    debug: bool = False,
    jit_options: Optional[Sequence[str]] = None,
) -> Runtime:
    from .mono import Mono

    libmono = _maybe_path(libmono)
    if libmono is None:
        libmono = find_libmono(sgen)

    impl = Mono(
        domain=domain,
        debug=debug,
        jit_options=jit_options,
        config_file=_maybe_path(config_file),
        global_config_file=_maybe_path(global_config_file),
        libmono=libmono,
    )
    return impl


def get_coreclr(
    *,
    runtime_config: Optional[StrOrPath] = None,
    dotnet_root: Optional[StrOrPath] = None,
    properties: Optional[Dict[str, str]] = None,
    runtime_spec: Optional[DotnetCoreRuntimeSpec] = None,
) -> Runtime:
    from .hostfxr import DotnetCoreRuntime

    dotnet_root = _maybe_path(dotnet_root)
    if dotnet_root is None:
        dotnet_root = find_dotnet_root()

    temp_dir = None
    runtime_config = _maybe_path(runtime_config)
    if runtime_config is None:
        if runtime_spec is None:
            candidates = [
                rt for rt in find_runtimes() if rt.name == "Microsoft.NETCore.App"
            ]
            candidates.sort(key=lambda spec: spec.version, reverse=True)
            if not candidates:
                raise RuntimeError("Failed to find a suitable runtime")

            runtime_spec = candidates[0]

        temp_dir = TemporaryDirectory()
        runtime_config = Path(temp_dir.name) / "runtimeconfig.json"

        with open(runtime_config, "w") as f:
            runtime_spec.write_config(f)

    impl = DotnetCoreRuntime(runtime_config=runtime_config, dotnet_root=dotnet_root)
    if properties:
        for key, value in properties.items():
            impl[key] = value

    if temp_dir:
        temp_dir.cleanup()

    return impl


def get_netfx(
    *, name: Optional[str] = None, config_file: Optional[StrOrPath] = None
) -> Runtime:
    from .netfx import NetFx

    impl = NetFx(name=name, config_file=_maybe_path(config_file))
    return impl


def _maybe_path(p: Optional[StrOrPath]) -> Optional[Path]:
    if p is None:
        return None
    else:
        return Path(p)
