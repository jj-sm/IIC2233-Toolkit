import sys
import os
from pathlib import Path
from pathspec import PathSpec
import re
import argparse

# It only checks for the following rules:
# - Line too long (max 100 characters)
# - Spaces as indentation (4 spaces)
# - Spaces after commas
# - Avoiding the use of `import *`
# - Use of `snake_case` for variables and functions, and `CamelCase` for classes
#
# >[!NOTE] Not PEP8 but also checked:
# > - Avoiding the use of `;` in the code
# > - Not more than +400 lines of code per `.py` file

def load_gitignore_spec(directory: str) -> PathSpec:
    gitignore_path = Path(directory) / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            lines = f.readlines()
        return PathSpec.from_lines("gitwildmatch", lines)
    return PathSpec([])  # Return empty spec if no .gitignore

def get_files(directory: str) -> list:
    check_path = Path(directory).resolve()
    spec = load_gitignore_spec(str(check_path))

    if not check_path.exists():
        print("Directory or file does not exist")
        sys.exit()
    elif check_path.is_file():
        return [check_path] if check_path.suffix == ".py" and not spec.match_file(check_path.relative_to(check_path.parent)) else []
    elif check_path.is_dir():
        files = []
        for root, _, files_in_dir in os.walk(check_path):
            for file in files_in_dir:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(check_path)
                if file_path.suffix == ".py" and not spec.match_file(str(rel_path)):
                    files.append(file_path)
        if not files:
            print("No Python files found in the directory or its subdirectories (excluding .gitignore)")
            sys.exit()
        return files
    else:
        print("Provided path is neither a file nor a directory")
        sys.exit()


def check_for_long_lines(file: str):
    with open(file, "r") as f:
        lines = []
        for line in f:
            if len(line) > 100:
                lines.append(line)
        if len(lines) > 1:
            return True, lines
        else:
            return False, lines

def check_for_spaces_indentation(file: str):
    inconsistent_lines = []

    try:
        with open(file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                stripped = line.lstrip()
                if stripped and not stripped.startswith("#"):
                    match = re.match(r"^(\s+)", line)
                    if match:
                        spaces = match.group(1)
                        if len(spaces) % 4 != 0 or "\t" in spaces:
                            inconsistent_lines.append(line_num)

        if len(inconsistent_lines) > 0:
            return (True, inconsistent_lines)
        else:
            return (False, [])

    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit()

def check_for_commas(file_path):
    issue_lines = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                stripped = line.split("#", 1)[0]

                if re.search(r",[^ \n]", stripped):
                    issue_lines.append(line_num)

    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit()

    if len(issue_lines) > 0:
        return True, issue_lines
    else:
        return False, []

def import_method(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        issue_lines = []
        for line in f:
            if "import *" in line:
                issue_lines.append(line)

        if len(issue_lines) > 0:
            return True, issue_lines
        else:
            return False, []

def check_naming(file_path: str):
    issue_lines = []

    snake_case_pattern = r"^[a-z_][a-z0-9_]*$"
    camel_case_pattern = r"^[A-Z][a-zA-Z0-9]*$"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                stripped = line.split("#", 1)[0]

                # Check for variables and functions
                if re.search(r"\b[a-z_][a-z0-9_]*\b", stripped):
                    for word in re.findall(r"\b[a-z_][a-z0-9_]*\b", stripped):
                        if not re.match(snake_case_pattern, word) and word != word.lower():
                            issue_lines.append(line_num)

                # Check for classes
                if re.search(r"\bclass\s+([A-Za-z0-9_]+)\b", stripped):
                    match = re.search(r"\bclass\s+([A-Za-z0-9_]+)\b", stripped)
                    if match and not re.match(camel_case_pattern, match.group(1)):
                        issue_lines.append(line_num)

    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit()

    if len(issue_lines) > 0:
        return True, issue_lines
    else:
        return False, []

def check_semicolons(file_path: str):
    issue_lines = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                stripped = line.split("#", 1)[0]  # Ignore comments

                if ";" in stripped:
                    issue_lines.append(line_num)

    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit()

    if len(issue_lines) > 0:
        return True, issue_lines
    else:
        return False, []

def check_file_length(file_path: str):
    max_lines = 400
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            file_length = len(lines)

            if file_length > max_lines:
                return True, file_length
            else:
                return False, file_length

    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit()

def check_pep8(files: list, output_dir: str) -> None:
    log_output = []
    for file in files:
        log = []

        # Run Tests
        check_long_lines_bool, check_long_lines_list = check_for_long_lines(file)
        check_spaces_bool, check_spaces_list = check_for_spaces_indentation(file)
        check_commas_bool, check_commas_list = check_for_commas(file)
        import_method_bool, import_method_list = import_method(file)
        check_naming_bool, check_naming_list = check_naming(file)
        check_semicolons_bool, check_semicolons_list = check_semicolons(file)
        check_file_length_bool, check_file_length_list = check_file_length(file)

        # Append Errors or OK messages
        if check_long_lines_bool:
            log.append(f"[FAIL] Long lines: {check_long_lines_list}")
        else:
            log.append("[=OK=] - Long lines check passed")

        if check_spaces_bool:
            log.append(f"[FAIL] - Inconsistent indentation: {check_spaces_list}")
        else:
            log.append("[=OK=] - Indentation check passed")

        if check_commas_bool:
            log.append(f"[FAIL] - Missing space after commas: {check_commas_list}")
        else:
            log.append("[=OK=] - Comma spacing check passed")

        if import_method_bool:
            log.append(f"[FAIL] - Use of 'import *' detected: {import_method_list}")
        else:
            log.append("[=OK=] - 'import *' check passed")

        if check_naming_bool:
            log.append(f"[FAIL] - Naming convention issues: {check_naming_list}")
        else:
            log.append("[=OK=] - Naming conventions check passed")

        if check_semicolons_bool:
            log.append(f"[FAIL] - Semicolons detected: {check_semicolons_list}")
        else:
            log.append("[=OK=] - Semicolon check passed")

        if check_file_length_bool:
            log.append(f"[FAIL] - File too long (>400 lines): {check_file_length_list}")
        else:
            log.append("[=OK=] - File length check passed")

        log_output.append(f"File checked: {file}\n" + "\n".join(log) + "\n")
        log_output.append('\n')

    if output_dir:
        output_path = Path(output_dir) / "pep8_check_log.txt"
        with open(output_path, "w") as log_file:
            log_file.writelines(log_output)
        print(f"Log saved to {output_path}")
    else:
        print("\n".join(log_output))

def main():
    parser = argparse.ArgumentParser(description="Check PEP8 style for Python files.")
    parser.add_argument("directory", help="Directory or file to check")
    parser.add_argument("output", nargs="?", help="Directory to save log (optional, print to console if not provided)")

    args = parser.parse_args()

    files = get_files(args.directory)
    check_pep8(files, args.output)

if __name__ == "__main__":
    main()
