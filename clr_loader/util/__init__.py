from .clr_error import ClrError
from .coreclr_errors import get_coreclr_error
from .hostfxr_errors import get_hostfxr_error


def check_result(err_code: int) -> None:
    """Check the error code of a .NET hosting API function and raise a
    converted exception.

    :raises ClrError: If the error code is `< 0`
    """

    if err_code < 0:
        hresult = err_code & 0xFFFF_FFFF

        error = get_coreclr_error(hresult)
        if not error:
            error = get_hostfxr_error(hresult)

        if not error:
            error = ClrError(hresult)

        raise error
