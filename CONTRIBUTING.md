# Contributing to CPTools

Thank you for your interest in contributing to CPTools! We welcome contributions from everyone. This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.6+
- `g++` compiler
- Git

### Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/src-lua/cptools.git
    cd cptools
    ```

2. **Install in development mode:**

    ```bash
    ./install.sh
    ```

    This will install the tool and make your local changes available immediately.

3. **Test your installation:**

    ```bash
    cptools --help
    ```

## How to Contribute

### 1. Find or Propose an Issue

- **Find an existing issue:** Check the [issue tracker](https://github.com/your-username/cptools/issues) for bugs or features to work on. Look for issues tagged `good first issue` if you're new.
- **Propose a new feature:** If you have an idea, please [open an issue](https://github.com/your-username/cptools/issues/new) to discuss it first.

### 2. Make Your Changes

1. **Create a new branch:**

    ```bash
    git checkout -b feature/my-new-feature
    ```

2. **Write your code.** Follow the guidelines below when making changes.

3. **Test your changes:**
    - Run automated tests: `pytest`
    - Manually test your changes to ensure they work as expected.

### 3. Submit a Pull Request

1. **Commit your changes** with a clear message:

    ```bash
    git commit -m "feat: Add new command for hashing"
    ```

    We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

2. **Push to your branch:**

    ```bash
    git push origin feature/my-new-feature
    ```

3. **Open a Pull Request** on GitHub.

## Development Guidelines

### Adding a New Command

If you're adding a new command, follow this checklist:

- [ ] Create a new file `commands/<name>.py`.
- [ ] Implement `get_parser()` and `run()` functions.
- [ ] Register the command in `lib/__init__.py` by adding it to `get_command_modules()`.
- [ ] Add generated files to `.gitignore` and `commands/init.py` if needed.
- [ ] Add tests for the new command in `tests/test_cmd_<name>.py`.

For a detailed example, look at existing commands like `commands/hash.py`.

### Adding Commands to Autocomplete

The shell completion system (`commands/completion.py`) automatically detects all commands and their flags by introspecting command modules. However, **you need to manually configure file/directory completion behavior** for new commands.

#### File Completion Commands

If your command accepts `.cpp` files as positional arguments (like `add`, `rm`, `mark`, `open`, `test`, `bundle`), add it to the `FILE_COMMANDS` list at the top of `commands/completion.py`:

```python
# At the top of commands/completion.py:
FILE_COMMANDS = ['add', 'rm', 'mark', 'open', 'test', 'bundle', 'your-new-command']
```

This enables:

- Bash: Completes with `.cpp` files when not typing a flag
- Zsh: Uses `_files -g "*.cpp"` for intelligent file completion

#### Directory Completion Commands

If your command accepts directories as positional arguments (like `update`, `new`), add it to the `DIR_COMMANDS` list at the top of `commands/completion.py`:

```python
# At the top of commands/completion.py:
DIR_COMMANDS = ['update', 'new', 'your-new-command']
```

This enables:

- Bash: Completes with directories when not typing a flag
- Zsh: Uses `_files -/` for directory-only completion

#### Flag-Only Commands

Commands that only accept flags (no file/directory arguments) require **no manual configuration**. The completion system automatically extracts all flags from your command's `get_parser()` function.

#### Testing Completion

After modifying `completion.py`:

1. Reinstall completion:

   ```bash
   cptools completion --install
   ```

2. Restart your shell or run:

   ```bash
   source ~/.bashrc  # or ~/.zshrc
   ```

3. Test by typing:

   ```bash
   cptools your-new-command <TAB>
   ```

#### How It Works

The completion system works by:

1. **Auto-discovery**: Calls `get_command_modules()` to find all commands
2. **Flag extraction**: Uses `get_parser()` to introspect each command's flags
3. **Template generation**: Injects command/flag data into bash/zsh completion templates
4. **Context-aware completion**: Uses the `file_commands` and `dir_commands` lists to provide intelligent positional argument completion

### Flag Naming Conventions

To ensure consistency across all commands, follow these flag naming standards:

#### General Rules

1. **Boolean Flags:**
   - Always provide both short (`-x`) and long (`--flag-name`) forms when possible
   - Use lowercase single letters for short forms
   - Use kebab-case for long forms (words separated by hyphens)

2. **Common Flag Conventions:**
   - `-a, --all`: Batch operations on all items/directories
   - `-r, --recursive`: Recursive operations
   - `-o, --output FILE`: Output to a file
   - `-i, --in-place`: Modify files in place
   - `-f, --fetch`: Fetch or download data

3. **Negation Flags:**
   - Use `--no-*` format (e.g., `--no-git`, `--no-out`)
   - Never omit the hyphen (e.g., `--nogit` is incorrect)

#### Examples

**Good:**

```python
parser.add_argument('-a', '--all', action='store_true', help='Process all items')
parser.add_argument('-r', '--recursive', action='store_true', dest='r', help='Recursive mode')
parser.add_argument('-o', '--output', metavar='FILE', dest='o', help='Output file')
parser.add_argument('--no-git', action='store_true', dest='no_git', help='Skip git')
```

**Bad:**

```python
parser.add_argument('--all', action='store_true')  # Missing short form
parser.add_argument('-r', action='store_true')  # Missing long form
parser.add_argument('--nogit', action='store_true')  # Should be --no-git
```

#### dest Parameter

When providing both short and long forms, use the `dest` parameter to maintain backward compatibility with existing code:

```python
# This ensures args.r works even though we now have --recursive
parser.add_argument('-r', '--recursive', dest='r', action='store_true')
```

### Code Style

- Follow **PEP 8** conventions.
- Use clear, meaningful variable names.
- Keep functions small and focused.

### Output: STDERR vs. STDOUT

A critical rule for this project is to separate logging from data output.

- **Use `sys.stderr` for:** logs, status messages, progress indicators, errors, and any colored or formatted text.
- **Use `sys.stdout` (the default for `print()`) for:** raw data that can be redirected or piped to another command.

**Good Example:**

```python
import sys
from lib.io import error, success

# Log to stderr
print("Starting process...", file=sys.stderr)

# Output data to stdout
print("This is the result.")

# Use helpers for colored output to stderr
success("Process completed successfully!")
error("Something went wrong.")
```

## Code of Conduct

Please be respectful and constructive in all your interactions.

---

Thank you for helping make competitive programming more efficient for everyone!
