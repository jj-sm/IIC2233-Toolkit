import ast
import argparse
import os
from pathlib import Path
from pathspec import PathSpec
from colorama import init, Fore, Style

# === Initialize colorama ===
init(autoreset=True)

# === .gitignore support ===
def load_gitignore_spec(directory: str) -> PathSpec:
    gitignore_path = Path(directory) / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            lines = f.readlines()
        return PathSpec.from_lines("gitwildmatch", lines)
    return PathSpec([])

def get_python_files(directory: Path, spec: PathSpec):
    files = []
    for root, _, filenames in os.walk(directory):
        for name in filenames:
            file_path = Path(root) / name
            rel_path = file_path.relative_to(directory)
            if file_path.suffix == ".py" and not spec.match_file(str(rel_path)):
                files.append(file_path)
    return files

# === AST-Based Import & Built-in Analysis ===
def parse_violations(file_path: Path, allowed: set, prohibited: set, deadly_builtins: set):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError:
            return {
                "syntax_error": True,
                "prohibited_modules": [],
                "deadly_builtins": [],
                "message": f"[FAIL] {file_path}: Syntax error in file"
            }

    found_prohibited = []
    found_deadly = []
    imported_modules = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                imported_modules[alias.asname or alias.name] = mod

                if any(mod == a or mod.startswith(f"{a}.") for a in allowed):
                    continue

                if any(mod == p or mod.startswith(f"{p}.") for p in prohibited):
                    if mod not in allowed:
                        found_prohibited.append((mod.split(".")[0], node.lineno))

        elif isinstance(node, ast.ImportFrom):
            mod = node.module
            if mod is None:
                continue

            for alias in node.names:
                full_name = f"{mod}.{alias.name}"
                imported_modules[alias.asname or alias.name] = full_name

                if any(full_name == a or full_name.startswith(f"{a}.") for a in allowed):
                    continue
                if any(mod == p or mod.startswith(f"{p}.") for p in prohibited):
                    found_prohibited.append((mod.split(".")[0], node.lineno))

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in deadly_builtins:
                found_deadly.append((node.func.id, node.lineno))

    return {
        "syntax_error": False,
        "prohibited_modules": sorted(set(found_prohibited)),
        "deadly_builtins": sorted(set(found_deadly)),
        "message": None
    }

# === Main Logic ===
def main():
    parser = argparse.ArgumentParser(description="Check for allowed/prohibited libraries and functions.")
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument("logfile", help="Output log file")
    parser.add_argument("-allowed", nargs="*", default=[])
    parser.add_argument("-prohibited", nargs="*", default=[])
    args = parser.parse_args()

    deadly_builtins = {"exec", "eval"}

    root_path = Path(args.path).resolve()
    log_path = Path(args.logfile).resolve()

    if not root_path.exists():
        print("Directory does not exist")
        return
    if log_path.is_dir():
        print("Logfile path cannot be a directory")
        return

    spec = load_gitignore_spec(str(root_path))
    py_files = get_python_files(root_path, spec)

    allowed_set = set(args.allowed)
    prohibited_set = set(args.prohibited)

    log_lines = []

    for file in py_files:
        result = parse_violations(file, allowed_set, prohibited_set, deadly_builtins)
        rel_path = file.relative_to(root_path)

        if result["syntax_error"]:
            msg = f"{Fore.RED}[FAIL]{Style.RESET_ALL} {rel_path}: {Fore.YELLOW}Syntax error in file"
            log_lines.append(f"[FAIL] {rel_path}: Syntax error in file")

        elif result["deadly_builtins"]:
            items = [f"{func} (line {line})" for func, line in result["deadly_builtins"]]
            deadly_msg = ", ".join(items)
            msg = f"{Fore.RED}[FAIL ☠️]{Style.RESET_ALL} {rel_path}: Uses deadly built-ins: {Fore.RED}{deadly_msg}"
            log_lines.append(f"[FAIL ☠️] {rel_path}: Uses prohibited built-ins: {deadly_msg}")

        elif result["prohibited_modules"]:
            items = [f"{mod} (line {line})" for mod, line in result["prohibited_modules"]]
            mod_msg = ", ".join(items)
            msg = f"{Fore.RED}[FAIL]{Style.RESET_ALL} {rel_path}: Imported prohibited modules: {Fore.MAGENTA}{mod_msg}"
            log_lines.append(f"[FAIL] {rel_path}: Imported prohibited modules: {mod_msg}")

        else:
            msg = f"{Fore.GREEN}[=OK=]{Style.RESET_ALL} {rel_path}: All Good"
            log_lines.append(f"[=OK=] {rel_path}: All Good")

        print(msg)

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print(f"\n{Fore.CYAN}Check completed. Results saved to: {Fore.YELLOW}{log_path}")

if __name__ == "__main__":
    main()
