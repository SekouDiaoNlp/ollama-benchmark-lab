import ast
import os

def get_imports(filepath):
    with open(filepath, "r") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return set()
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports

py_files = []
for root, _, files in os.walk("benchmark"):
    for f in files:
        if f.endswith(".py"):
            py_files.append(os.path.join(root, f))
py_files.append("autollama/cli.py")

all_imports = set()
for f in py_files:
    all_imports.update(get_imports(f))

# Find benchmark files not imported
for f in os.listdir("benchmark"):
    if f.endswith(".py") and f != "__init__.py":
        mod_name = "benchmark." + f[:-3]
        if mod_name not in all_imports:
            print(f"Suspect dead top-level file: benchmark/{f}")
