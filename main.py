from importlib.abc import Loader
from importlib.machinery import ModuleSpec
import sys
import importlib.util
import os
import typing


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("No module name provided")

    module_name = sys.argv[1]
    module_path = os.path.join(sys.path[0], "src", "scripts", f"{module_name}.py")
    not_import_message = f"Failed to import {module_name} from {module_path}"

    if not os.path.exists(module_path):
        print("No module name provided")

    spec = importlib.util.spec_from_file_location(module_name, module_path)

    if not spec or not spec.loader:
        print(not_import_message)

    spec = typing.cast(ModuleSpec, spec)
    module = importlib.util.module_from_spec(spec)
    loader = typing.cast(Loader, spec.loader)

    try:
        loader.exec_module(module)
    except (ImportError, FileNotFoundError, RuntimeError) as e:
        print(not_import_message)
        print(f"Error: {e}")
