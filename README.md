# Python Code Compliance Tools

This repository contains two powerful tools for analyzing Python code quality:

1. **PEP8 Checker** (`checkPEP8.py`) - Validates code against essential PEP8 standards
2. **Library Checker** (`checkLibs.py`) - Enforces import restrictions and detects dangerous patterns

## PEP8 Checker (checkPEP8.py)

### Example Output
```text
File checked: example.py
[=OK=] - Long lines check passed (max 100 chars)
[=OK=] - Indentation check passed (4 spaces)
[FAIL] - Missing space after commas: [16, 24, 31]
[=OK=] - 'import *' check passed
[FAIL] - Naming conventions: [42] (function 'badName' should be snake_case)
[FAIL] - Semicolons detected: [26, 27]
[=OK=] - File length check passed (128 lines)
```

### Usage
```bash
# Basic usage (terminal output)
python3 checkPEP8.py /path/to/project

# Save results to file
python3 checkPEP8.py /path/to/project audit_log.txt

# Check single file
python3 checkPEP8.py module.py
```

## Library Checker (checkLibs.py)

### Example Output
```text
[=OK=] utils/helpers.py: All Good
[FAIL ☠️] scripts/run.py: Uses deadly built-ins: eval (line 42)
[FAIL] core/processing.py: Imported prohibited modules: pandas (line 3), pickle (line 8)
[=OK=] main.py: All Good
```

### Usage
```bash
# Basic scan with custom rules
python3 checkLibs.py /path/to/project lib_audit.txt \
  -allowed "sys os.path datetime" \
  -prohibited "pandas numpy pickle"

# With detailed allowed submodules
python3 checkLibs.py /path/to/project lib_audit.txt \
  -allowed "sys.argv sys.exit os.path" \
  -allowed "PyQt5.QtWidgets datetime" \
  -prohibited "pandas numpy re"
```

## Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/your-repo/python-code-audit.git
cd python-code-audit
```

2. Set up convenient aliases (add to ~/.zshrc or ~/.bashrc):
```bash
# For PEP8 checking
alias pep8check="python3 /path/to/checkPEP8.py"

# For library validation
alias libcheck="python3 /path/to/checkLibs.py"
```

3. Reload your shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

## Key Features

### PEP8 Checker
- Line length validation (configurable)
- Indentation checking
- Import statement analysis
- Naming convention enforcement
- Syntax style checks

### Library Checker
- Configurable allow/prohibit lists
- Dangerous built-in detection (eval, exec)
- .gitignore aware scanning
- Cross-platform support
- Detailed reporting with line numbers

## Requirements
Only Python standard libraries are used:
```
- sys
- os
- pathlib
- re
- argparse
- ast
- pathspec
- colorama
```

## Contribution

Feel free to submit issues or pull requests for:
- Additional PEP8 rules
- Improved error messages
- Performance optimizations
- New features

Maintained by [jj-sm](https://github.com/jj-sm/) 🐍
