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
- [ ] Register the command in the `__init__.py` on commands folder.
- [ ] Add generated files to `.gitignore` and `commands/init.py` if needed.
- [ ] Add tests for the new command in `tests/test_cmd_<name>.py`.

For a detailed example, look at existing commands like `commands/hash.py`.

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
