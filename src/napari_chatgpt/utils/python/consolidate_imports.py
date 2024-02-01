def consolidate_imports(code):
    lines = code.split('\n')
    unique_imports = set()
    import_block_end = 0

    # Identify and store unique import statements
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith('import ') or stripped_line.startswith('from '):
            unique_imports.add(line)
            import_block_end = i
        elif stripped_line:  # Non-empty line that's not an import statement
            break

    # Reconstruct the code
    consolidated_code = '\n'.join(sorted(unique_imports)) + '\n\n' + '\n'.join(lines[import_block_end+1:])
    return consolidated_code