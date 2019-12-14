from os.path import basename
from .ffi import ffi


__all__ = ["get_mono", "get_netfx", "get_coreclr"]


class ClrFunction:
    def __init__(self, runtime, assembly, typename, func_name):
        self._assembly = assembly
        self._class = typename
        self._name = func_name

        self._callable = runtime.get_callable(assembly, typename, func_name)

    def __call__(self, buffer):
        buf_arr = ffi.from_buffer("char[]", buffer)
        return self._callable(ffi.cast("void*", buf_arr), len(buf_arr))

    def __repr__(self):
        return f"<ClrFunction {self._class}.{self._name} in {basename(self._assembly)}>"


class Assembly:
    def __init__(self, runtime, path):
        self._runtime = runtime
        self._path = path

    def get_function(self, name, func=None):
        if func is None:
            name, func = name.rsplit(".", 1)

        return ClrFunction(self._runtime, self._path, name, func)

    def __getitem__(self, name):
        return self.get_function(name)

    def __repr__(self):
        return f"<Assembly {self._path} in {self._runtime}>"


class Runtime:
    def __init__(self, impl):
        self._impl = impl

    def get_assembly(self, path):
        return Assembly(self._impl, path)

    def __getitem__(self, path):
        return self.get_assembly(path)


def get_mono(domain=None):
    from .mono import Mono

    impl = Mono(domain=domain)
    return Runtime(impl)


def get_coreclr(runtime_config, dotnet_root=None):
    from .hostfxr import HostFxr

    impl = HostFxr(runtime_config=runtime_config, dotnet_root=dotnet_root)
    return Runtime(impl)


def get_netfx(name=None, config_file=None):
    from .netfx import NetFx

    impl = NetFx(name=name, config_file=config_file)
    return Runtime(impl)
