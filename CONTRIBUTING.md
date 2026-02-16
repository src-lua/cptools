# Contributing to CPTools

Thank you for your interest in contributing to CPTools! We welcome contributions from everyone. This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.10+
- `g++` compiler
- Git

### Setup

**Clone the repository:**

```bash
git clone https://github.com/src-lua/cptools.git
cd cptools
```

**Install global development tools (optional):**

These tools work across all your projects, so install them globally:

```bash
pipx install pre-commit
pipx install commitizen
```

Then, inside the `cptools` directory, enable git hooks:

```bash
pre-commit install
```

This configures hooks that run automatically on `git commit`:

- `pytest` before each commit
- Commit message validation using [Conventional Commits](https://www.conventionalcommits.org/) format

**Create a virtual environment and install:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

This installs the project in editable mode with all development dependencies (`pytest`, `pytest-cov`, etc.).

**Install development binary (optional):**

To test the `cptools` command globally alongside the stable PyPI version:

```bash
pipx install -e '.[dev]' --suffix=-dev
```

This creates a `cpt-dev` command using your local development version, while `cpt` (from PyPI) remains untouched. Since it's an editable install, code changes are reflected automatically. Only reinstall with `pipx reinstall cptools-dev` if you modify dependencies or entry points.

**Note:** `pipx` always creates isolated environments, so this command works whether you're inside the venv or not.

**Test your setup:**

```bash
# Verify cptools points to your virtual environment
which cptools
# Should show: /path/to/cptools/.venv/bin/cptools

cptools --help  # Or cpt-dev --help if you installed via pipx
pytest          # Run test suite
```

**Note:** If `which cptools` points to a global installation instead of `.venv`, refresh your shell with `hash -r` or restart it with `exec $SHELL`.

**Optional: Better Unicode support for status command:**

If you experience alignment issues with `cpt status` (misaligned emojis), install `wcwidth`:

```bash
pip install wcwidth
```

This improves emoji width detection in terminals. Not required, but recommended for better display.

**Daily workflow:**

- **Develop:** VS Code uses `.venv` automatically. Run `pytest` to test.
- **Commit:** Ensure `.venv` is active (`source .venv/bin/activate`), then use `git commit` (hooks run automatically) or `cz commit` (guided commit messages).
- **Test binary:** Use `cpt-dev` if installed, or run `cptools` directly from the activated `.venv`.
- **Deactivate:** When done, exit the virtual environment with `deactivate`.

**Note:** Git hooks and global binaries are optional. All pull requests are automatically validated in CI.

## How to Contribute

### 1. Find or Propose an Issue

- **Find an existing issue:** Check the [issue tracker](https://github.com/src-lua/cptools/issues) for bugs or features to work on. Look for issues tagged `good first issue` if you're new.
- **Propose a new feature:** If you have an idea, please [open an issue](https://github.com/src-lua/cptools/issues/new) to discuss it first.

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

    **Important:** Ensure your virtual environment is active before committing:

    ```bash
    source .venv/bin/activate  # Activate the virtual environment
    git commit -m "feat: Add new command for hashing"
    ```

    The pre-commit hooks require local dependencies to run tests. If you need to deactivate the virtual environment later, simply run:

    ```bash
    deactivate
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
- [ ] Add generated files to `.gitignore` and `commands/init.py` if needed.
- [ ] Add tests for the new command in `tests/test_cmd_<name>.py`.

**Note:** Commands are automatically discovered from the `commands/` directory. No manual registration is required! The system will automatically detect any `.py` file in `commands/` that has both `get_parser()` and `run()` functions.

For a detailed example, look at existing commands like `commands/hash.py`.

### Adding New Platforms (Judges)

CPTools supports multiple competitive programming platforms through an extensible judge system. If you want to add support for a new platform:

📖 **See the complete guide:** [docs/ADDING_JUDGES.md](docs/ADDING_JUDGES.md)

The guide covers:

- Architecture overview and base classes
- Step-by-step implementation instructions
- URL parsing and integration
- Testing patterns with examples
- Authentication support
- Complete working examples

We encourage contributions to expand platform support! The judge system is designed to make adding new platforms straightforward.

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
