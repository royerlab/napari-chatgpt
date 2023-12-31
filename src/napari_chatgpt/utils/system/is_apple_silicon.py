


def is_apple_silicon():
    import platform
    import os

    if platform.system() != 'Darwin':
        return False  # Not OSX, so it can't be M1/M2

    # Use `uname` to get system information
    uname_output = os.uname()

    # Check the machine value in the uname output
    # 'arm64' indicates Apple Silicon (M1/M2)
    if 'arm64' in uname_output.machine:
        return True

    return False

