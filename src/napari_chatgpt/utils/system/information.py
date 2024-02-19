import platform
import sys


def system_info(add_python_info: bool = False):
    """
    Returns a string with information about the system: machine, operating system (all details), version of Python, etc.
    """

    # Get the system information:
    info = {
        "Machine": platform.machine()+f" ({platform.processor()} {platform.architecture()[0]})",
        "Version": platform.version().split(':')[0],
        "Platform": platform.platform(),
        "System": platform.system()
    }

    # Add additional Python information if requested:
    if add_python_info:
        info |= {
            "Python Version": sys.version,
            "Python Compiler": platform.python_compiler(),
            "Python Implementation": platform.python_implementation(),
            "Python Build": platform.python_build()
        }

    # Create a string with the information:
    info_str = "```system_info\n"
    info_str += "\n".join([f"{key}: {value}" for key, value in info.items()])
    info_str += "\n```\n"

    return info_str