from typing import Dict, Optional, Sequence

from .wrappers import Runtime
from .util.find import find_libmono, find_dotnet_root

__all__ = ["get_mono", "get_netfx", "get_coreclr"]


def get_mono(
    domain: Optional[str] = None,
    config_file: Optional[str] = None,
    global_config_file: Optional[str] = None,
    libmono: Optional[str] = None,
    sgen: bool = True,
    debug: bool = False,
    jit_options: Optional[Sequence[str]] = None,
) -> Runtime:
    from .mono import Mono

    if libmono is None:
        libmono = find_libmono(sgen)

    impl = Mono(
        domain=domain,
        debug=debug,
        jit_options=jit_options,
        config_file=config_file,
        global_config_file=global_config_file,
        libmono=libmono,
    )
    return Runtime(impl)


def get_coreclr(
    runtime_config: str,
    dotnet_root: Optional[str] = None,
    properties: Optional[Dict[str, str]] = None,
) -> Runtime:
    from .hostfxr import DotnetCoreRuntime

    if dotnet_root is None:
        dotnet_root = find_dotnet_root()

    impl = DotnetCoreRuntime(runtime_config=runtime_config, dotnet_root=dotnet_root)
    if properties:
        for key, value in properties.items():
            impl[key] = value

    return Runtime(impl)


def get_netfx(name: Optional[str] = None, config_file: Optional[str] = None) -> Runtime:
    from .netfx import NetFx

    impl = NetFx(name=name, config_file=config_file)
    return Runtime(impl)
