from typing import Dict, Optional

from .wrappers import Runtime

__all__ = ["get_mono", "get_netfx", "get_coreclr"]


def get_mono(
    domain: Optional[str] = None,
    config_file: Optional[str] = None,
    path: Optional[str] = None,
    gc: Optional[str] = None,
) -> Runtime:
    from .mono import Mono

    impl = Mono(domain=domain, config_file=config_file, path=path, gc=gc)
    return Runtime(impl)


def get_coreclr(
    runtime_config: str, dotnet_root: Optional[str] = None,
    properties: Optional[Dict[str, str]] = None
) -> Runtime:
    from .hostfxr import DotnetCoreRuntime

    impl = DotnetCoreRuntime(runtime_config=runtime_config, dotnet_root=dotnet_root)
    if properties:
        for key, value in properties:
            impl[key] = value

    return Runtime(impl)


def get_netfx(name: Optional[str] = None, config_file: Optional[str] = None) -> Runtime:
    from .netfx import NetFx

    impl = NetFx(name=name, config_file=config_file)
    return Runtime(impl)
