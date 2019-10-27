def check_result(err_code):
    if err_code < 0:
        raise RuntimeError(hex(err_code & 0xFFFFFFFF))

