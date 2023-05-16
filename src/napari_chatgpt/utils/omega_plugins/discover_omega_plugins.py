import importlib


### https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/


def discover_omega_tools(group: str = 'omega.tools'):
    """
    This function discovers plugins

    Parameters
    ----------
    group

    Returns
    -------
    List of tool classes


    """
    import sys
    if sys.version_info < (3, 10):
        from importlib_metadata import entry_points
    else:
        from importlib.metadata import entry_points

    discovered_tools = entry_points(group=group)

    list_of_classes = []
    for entry_point in discovered_tools:
        module_name, class_name = entry_point.module, entry_point.attr
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        list_of_classes.append(class_)

    return list_of_classes
