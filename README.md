# PEP8
This repository aims to check whether a folder (with its subfiles) or project complies with *some of PEP8's rules. Mainly the ones evaluated in some coding courses.

Example output:
```text
File checked: test.py
[=OK=] - Long lines check passed
[=OK=] - Indentation check passed
[FAIL] - Missing space after commas: [16]
[=OK=] - 'import *' check passed
[=OK=] - Naming conventions check passed
[FAIL] - Semicolons detected: [26, 27]
[=OK=] - File length check passed
```

## How to use it

1. Clone the repository somewhere on your computer
2. Open the terminal where you downloaded the repository
3. Run the following command:

- on zhs (macOS, Linux, UNIX) *also Windows:

>[!NOTE] 
> Remember to use the correct `python` call. It can be `python`, `python3`, `py`, `py3`, etc.

Save log on txt:
```bash
python3 <path to checkPEP8.py> <path to folder or file> <optional: log file.txt saving directory>
```

Log on terminal:
```bash
python3 <path to checkPEP8.py> <path to folder or file> <optional: log file.txt saving directory>
```

### (Optional) If you want to run it directly from the terminal:
1. Save the `checkPEP8.py` file in a fixed directory (anywhere you want) but where you are not likely to move. Preferrably on the .../bin/pyscripts? directory.
2. Open the terminal and run the following commands (macOS, Linux, UNIX):

```bash
nano ~/.zshrc
```

Go to the end of the file:

```bash
alias checkPEP8="python3 <<PATH TO THE FILE>>/checkPEP8.py"
``` 

Save and exit the file. Then run:

```bash
source ~/.zshrc
```

And it will be ready to go!

```bash
checkPEP8 <path_to_folder_or_file>
```


## What does it check for?
It only checks for the following rules:
- Line too long (max 100 characters)
- Spaces as indentation (4 spaces)
- Spaces after commas
- Avoiding the use of `import *`
- Use of `snake_case` for variables and functions, and `CamelCase` for classes

>[!NOTE] 
> Not PEP8 but also checked:
> - Avoiding the use of `;` in the code
> - Not more the +400 lines of code per `.py` file

## Libs Used
- sys
- os
- pathlib 
- re
- argparse

All are built-in libraries. 

Made by: [jj-sm](https://github.com/jj-sm/) 🐍