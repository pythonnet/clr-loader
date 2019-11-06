class ClrError(Exception):
    def __init__(self, hresult, name=None, message=None, comment=None):
        self.hresult = hresult
        self.name = name
        self.message = message
        self.comment = comment

    def __str__(self):
        if self.message:
            return f"{hex(self.hresult)}: {self.name} => {self.message}"
        elif self.name:
            return f"{hex(self.hresult)}: {self.name}"
        else:
            return f"{hex(self.hresult)}"

    def __repr__(self):
        return f"<ClrError {str(self)}>"


def check_result(err_code):
    if err_code < 0:
        hresult = err_code & 0xFFFFFFFF

        error = get_coreclr_error(hresult)
        if not error:
            error = get_hostfxr_error(hresult)

        if not error:
            error = ClrError(hresult)

        raise error


from .coreclr_errors import get_coreclr_error
from .hostfxr_errors import get_hostfxr_error
