import ast
import argparse
from pathlib import Path
import os
import subprocess

def get_defined_symbols(py_file: str, include_import: bool, include_underscore: bool) -> list[str]:
    source = Path(py_file).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=py_file)

    defined = []

    for node in tree.body:
        # 函數定義
        if isinstance(node, ast.FunctionDef):
            if include_underscore or not node.name.startswith("_"):
                defined.append(node.name)

        # 類別定義
        elif isinstance(node, ast.ClassDef):
            if include_underscore or not node.name.startswith("_"):
                defined.append(node.name)

        # 變數賦值
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if include_underscore or not target.id.startswith("_"):
                        defined.append(target.id)

        # 匯入語句 (import)
        elif isinstance(node, ast.Import):
            if include_import:
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    if include_underscore or not name.startswith("_"):
                        defined.append(name)

        # 排除 from import
        elif isinstance(node, ast.ImportFrom):
            continue

    return defined

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="解析 Python 檔案定義的符號")
    parser.add_argument("file", help="要解析的 .py 檔案路徑")
    parser.add_argument("-i", action="store_true", help="是否包含 import 的符號")
    parser.add_argument("-_", dest="include_underscore", action="store_true", help="是否包含 _ 開頭的符號")
    args = parser.parse_args()
    symbols = get_defined_symbols(args.file, args.i, args.include_underscore)
    print(symbols)
    if os.name == 'nt':
        subprocess.run("clip", text=True, input=str(symbols))
