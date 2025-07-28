def consolidate_imports(code):
    """
    Consolidate and deduplicate import statements at the top of a Python code string.
    
    Parameters:
        code (str): Python source code as a string.
    
    Returns:
        str: The code with unique, sorted import statements grouped at the top, followed by the remaining code.
    """

    # Split the code into lines and identify unique import statements
    lines = code.split("\n")

    # Use a set to store unique import statements
    unique_imports = set()

    # Track the end of the import block
    import_block_end = 0

    # Identify and store unique import statements
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith("import ") or stripped_line.startswith("from "):
            unique_imports.add(line)
            import_block_end = i
        elif stripped_line:  # Non-empty line that's not an import statement
            break

    # Reconstruct the code
    consolidated_code = (
        "\n".join(sorted(unique_imports))
        + "\n\n"
        + "\n".join(lines[import_block_end + 1 :])
    )
    return consolidated_code
