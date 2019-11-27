from .clr_error import ClrError
from .coreclr_errors import get_coreclr_error
from .hostfxr_errors import get_hostfxr_error


def check_result(err_code):
    if err_code < 0:
        hresult = err_code & 0xFFFFFFFF

        error = get_coreclr_error(hresult)
        if not error:
            error = get_hostfxr_error(hresult)

        if not error:
            error = ClrError(hresult)

        raise error
