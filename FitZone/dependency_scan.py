import ast
import os
import sys

root = r'C:\Users\sobig\OneDrive\Documents\FitZone'
ignore_dirs = {'.venv', '__pycache__'}
imports = set()
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
    for fn in filenames:
        if fn.endswith('.py'):
            path = os.path.join(dirpath, fn)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=path)
            except Exception:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

stdlib = set(sys.stdlib_module_names) if hasattr(sys, 'stdlib_module_names') else {
    'tkinter', 'ttk', 'sqlite3', 'email', 'html', 'xml', 'unittest', 'asyncio',
    'importlib', 'multiprocessing', 'pathlib', 'http', 'urllib', 'json', 'csv',
    'math', 'datetime', 'random', 'statistics', 'io', 'tempfile', 'functools',
    'collections', 'subprocess', 'os', 'sys', 'inspect', 'types', 'time',
    'logging', 're', 'threading', 'queue', 'socket', 'ssl', 'traceback',
    'platform', 'ctypes', 'struct'
}

external = sorted([m for m in imports if m not in stdlib and not m.startswith('gym_')])
print('EXTERNAL_MODULES:')
for name in external:
    print(name)
print('TOTAL_EXTERNAL_MODULES:', len(external))
