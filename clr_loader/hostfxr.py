import os
import shutil
import sys

from .ffi import ffi, load_hostfxr
from .util import check_result

__all__ = ["HostFxr"]


class HostFxr:
    # TODO: Allow generating runtime_config
    def __init__(self, runtime_config, dotnet_root=None):
        self._handle = None

        if not dotnet_root:
            dotnet_root = os.environ.get("DOTNET_ROOT", None)

        if not dotnet_root:
            dotnet_path = shutil.which("dotnet")
            if not dotnet_path:
                raise RuntimeError("Can not determine dotnet root")

            try:
                dotnet_tmp_path = os.readlink(dotnet_path)
                if os.path.isabs(dotnet_tmp_path):
                    dotnet_path = dotnet_tmp_path
                else:
                    dotnet_path = os.path.abspath(os.path.join(os.path.dirname(dotnet_path), dotnet_tmp_path))
            except OSError:
                pass

            dotnet_root = os.path.dirname(dotnet_path)

        self._dll = load_hostfxr(dotnet_root)
        self._dotnet_root = dotnet_root

        self._handle = _get_handle(self._dll, self._dotnet_root, runtime_config)
        self._load_func = _get_load_func(self._dll, self._handle)

    def get_callable(self, assembly_path, typename, function):
        # Append assembly name to typename
        assembly_name, _ = os.path.splitext(os.path.basename(assembly_path))
        typename = f"{typename}, {assembly_name}"

        delegate_ptr = ffi.new("void**")
        res = self._load_func(
            encode(assembly_path),
            encode(typename),
            encode(function),
            ffi.NULL,
            ffi.NULL,
            delegate_ptr,
        )
        check_result(res)
        return ffi.cast("component_entry_point_fn", delegate_ptr[0])

    def shutdown(self):
        if self._handle is not None:
            self._dll.hostfxr_close(self._handle)
            self._handle = None

    def __del__(self):
        self.shutdown()

    @property
    def props(self):
        return HostFxrProps(self)


class HostFxrProps:
    def __init__(self, fxr):
        self._fxr = fxr

    def __getitem__(self, key):
        buf = ffi.new("char_t**")
        res = self._fxr._dll.hostfxr_get_runtime_property_value(
            self._fxr._handle, encode(key), buf
        )
        if res != 0:
            raise KeyError(key)

        return decode(buf[0])

    def __setitem__(self, key, value):
        res = self._fxr._dll.hostfxr_set_runtime_property_value(
            self._fxr._handle, encode(key), encode(value)
        )
        check_result(res)

    def __iter__(self):
        max_size = 100
        size_ptr = ffi.new("size_t*")
        size_ptr[0] = max_size

        keys_ptr = ffi.new("char_t*[]", max_size)
        values_ptr = ffi.new("char_t*[]", max_size)

        res = self._fxr._dll.hostfxr_get_runtime_properties(
            self._fxr._handle, size_ptr, keys_ptr, values_ptr
        )
        check_result(res)

        for i in range(size_ptr[0]):
            yield (decode(keys_ptr[i]), decode(values_ptr[i]))


def _get_handle(dll, dotnet_root, runtime_config):
    params = ffi.new("hostfxr_initialize_parameters*")
    params.size = ffi.sizeof("hostfxr_initialize_parameters")
    # params.host_path = ffi.new("char_t[]", encode(sys.executable))
    params.host_path = ffi.NULL
    dotnet_root_p = ffi.new("char_t[]", encode(dotnet_root))
    params.dotnet_root = dotnet_root_p

    handle_ptr = ffi.new("hostfxr_handle*")

    res = dll.hostfxr_initialize_for_runtime_config(
        encode(runtime_config), params, handle_ptr
    )
    check_result(res)

    return handle_ptr[0]


def _get_load_func(dll, handle):
    delegate_ptr = ffi.new("void**")

    res = dll.hostfxr_get_runtime_delegate(
        handle, dll.hdt_load_assembly_and_get_function_pointer, delegate_ptr
    )
    check_result(res)

    return ffi.cast("load_assembly_and_get_function_pointer_fn", delegate_ptr[0])


if sys.platform == "win32":

    def encode(string):
        return string

    def decode(char_ptr):
        return ffi.string(char_ptr)


else:

    def encode(string):
        return string.encode("utf8")

    def decode(char_ptr):
        return ffi.string(char_ptr).decode("utf8")
