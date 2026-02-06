def consolidate_imports(code):
    """
    Consolidate import statements in a given Python code string.
    Parameters
    ----------
    code:   str
        The Python code as a string in which to consolidate import statements.

    Returns
    -------
    str
        The Python code with consolidated import statements.

    """

    # Split the code into lines
    lines = code.split("\n")

    # Use a set to store unique import statements
    unique_imports = set()

    # List to store non-import lines
    non_import_lines = []

    # Track whether we've seen the first non-import, non-blank, non-comment line
    past_import_section = False

    # Identify and store unique import statements
    for line in lines:
        stripped_line = line.strip()

        if past_import_section:
            # Once past the import section, keep all lines as-is
            non_import_lines.append(line)
        elif stripped_line.startswith("import ") or stripped_line.startswith("from "):
            # This is an import statement
            unique_imports.add(line)
        elif stripped_line == "" or stripped_line.startswith("#"):
            # Blank lines and comments in the import section are skipped
            # (they'll be replaced by the consolidated imports)
            pass
        else:
            # First non-import, non-blank, non-comment line marks end of import section
            past_import_section = True
            non_import_lines.append(line)

    # Reconstruct the code with sorted imports at the top
    consolidated_code = "\n".join(sorted(unique_imports))
    if unique_imports and non_import_lines:
        consolidated_code += "\n\n"
    consolidated_code += "\n".join(non_import_lines)

    return consolidated_code
