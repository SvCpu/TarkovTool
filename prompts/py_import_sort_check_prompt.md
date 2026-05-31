Scan all .py files under the src directory.
For each file, analyze the import statements at the beginning.
The required order is:
1. Project-specific modules (imports from src or relative imports)
2. Python standard library modules
3. Third-party packages (installed via pip)

If any file does not follow this order, output the full path of that file.
