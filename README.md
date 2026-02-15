# cptools

CLI toolkit for managing competitive programming contests and solutions.

Supports Codeforces, AtCoder, CSES, Yosupo, SPOJ, vJudge, and custom judges.

**Extensible:** Want to add support for another platform? See [docs/ADDING_JUDGES.md](docs/ADDING_JUDGES.md) for a complete guide on adding new judges.

> **⚠️ Beta Software**: cptools is currently in beta (pre-1.0). Breaking changes may occur between versions. Check the commit history or issues for recent changes.

## Dependencies

CPTools requires:

- **Python 3.10+**
- **g++** (or another C++ compiler)
- **git**
- **browser-cookie3** (Python package - installed automatically)

The installation script will automatically install Python dependencies using `pip`.

**For developers**, additional test dependencies are available:

```bash
pip install -e ".[dev]"  # Installs pytest and pytest-cov
```

## Installation

```bash
git clone <repo-url>
cd cptools
./install.sh
```

This script will:

- Check Python version (3.10+ required)
- Create symlinks `cptools` and `cpt` in `~/.local/bin`
- Install Python dependencies automatically
- Configure your shell's PATH

**Note:** On modern Ubuntu/Debian systems (23.04+), pip is restricted by PEP 668. The installer will guide you through creating a virtual environment if needed.

After installing, run `cptools config` to set your author name.

## Shell Completion

cptools provides intelligent tab completion for bash and zsh shells.

### Setup

```bash
cptools completion --install
```

This will:

- Auto-detect your shell (bash or zsh)
- Generate a completion script
- Install it to `~/.config/cptools/completion.{bash,zsh}`
- Add a source line to your `~/.bashrc` or `~/.zshrc`

After installation, restart your terminal or run `source ~/.bashrc` (or `~/.zshrc`).

### Features

- **Command completion**: Tab-completes all cptools subcommands
- **Flag completion**: Context-aware flag suggestions for each command
- **File completion**: Automatically completes `.cpp` files for commands like `add`, `rm`, `mark`, `open`, `test`, `bundle`
- **Directory completion**: Completes directories for commands like `update`, `new`

### Manual Installation

To generate a completion script for a specific shell without installing:

```bash
cptools completion --shell bash   # Output bash completion script
cptools completion --shell zsh    # Output zsh completion script
```

## Configuration

```bash
cptools config
```

Opens `~/.config/cptools/config.json` in your editor. Default configuration:

```json
{
    "author": "Dev",
    "default_group_id": "yc7Yxny414",
    "compiler": "g++",
    "compiler_flags": ["-O2", "-std=c++17"],
    "cookie_cache_enabled": true,
    "cookie_cache_max_age_hours": 24,
    "preferred_browser": null
}
```

### Configuration Options

- **`author`**: Your name, used in file headers
- **`default_group_id`**: Default Codeforces group ID for training contests
- **`compiler`**: C++ compiler command (e.g., `g++`, `clang++`)
- **`compiler_flags`**: Array of compiler flags for building solutions. Note: Add `-I<path>` flags here to support bundling custom libraries.
- **`cookie_cache_enabled`**: Enable/disable browser cookie caching for competitive programming sites (default: `true`)
- **`cookie_cache_max_age_hours`**: How long to cache cookies in hours. Set to `-1` to never expire (only refresh on auth failure)
- **`preferred_browser`**: Browser to use for authentication. Set to `null` for auto-detection, or specify `"firefox"`, `"chrome"`, etc.

## Commands

cptools provides commands for the complete competitive programming workflow.

**Quick Reference:**

| Command | Description |
| ------- | ----------- |
| `new` | Create a new contest |
| `init` | Initialize repository |
| `update` | Update info.md |
| `status` | Show contest progress |
| `add` | Add a solution file |
| `rm` | Remove problem files |
| `mark` | Update problem status |
| `open` | Open problem in browser |
| `add_header` | Add metadata header to file |
| `test` | Compile and test solution |
| `fetch` | Fetch sample test cases |
| `stress` | Stress test with brute force |
| `bundle` | Bundle includes for submission |
| `clean` | Remove binaries |
| `commit` | Commit and push changes |
| `config` | Edit configuration |
| `completion` | Generate shell completion |
| `hash` | Generate context-aware hash |

For detailed documentation of all commands, see **[docs/COMMANDS.md](docs/COMMANDS.md)**.

### Common Usage

```bash
# Create and setup contest
cpt new https://codeforces.com/contest/1234
cd Codeforces/1234
cpt fetch A~E

# Work on problems
cpt test A
cpt mark A AC
cpt open B

# Remove unwanted files
cpt rm A-brute

# Submit
cpt bundle A
cpt commit
```

## Advanced Usage Examples

### Complete Contest Workflow

From start to finish:

```bash
# Create contest and fetch all samples
cpt new https://codeforces.com/contest/1234
cd Codeforces/1234
cpt fetch A~E                 # fetch samples for all problems

# Solve problems
cpt test A                    # test solution A
cpt mark A                    # mark as AC
cpt open B                    # open problem B in browser
cpt test B
cpt mark B

# Check progress and commit
cpt status                    # view contest progress
cpt commit                    # commit and push changes
```

### Stress Testing Workflow

Complete setup for finding edge cases:

```bash
# Create necessary files
cpt add A              # main solution
cpt add A-brute        # brute force solution
cpt add gen            # test case generator
cpt add checker        # custom checker (optional)

# Run stress test
cpt stress A A-brute gen --checker checker

# When a failing case is found, add it to test suite
cpt test A --add < failing_case.txt
```

The generator receives iteration number as argument (`./gen 1`, `./gen 2`, ...) and should output a random test case.

### Managing Multiple Solutions

Different approaches for the same problem:

```bash
cpt add A              # first attempt
cpt add A-dp           # dynamic programming approach
cpt add A-greedy       # greedy approach
cpt add A-brute        # brute force for verification

# Test each approach
cpt test A-dp
cpt test A-greedy

# Compare solutions with stress testing
cpt stress A-greedy A-brute gen
```

### Custom Test Cases

Adding your own test cases:

```bash
cpt test A                    # test with official samples
cpt test A --add              # add custom input + expected output
cpt test A --add --no-out     # add input only (manual verification)
cpt test A < edge_case.txt    # test specific case from file
cpt test A --interactive      # run interactively even if samples exist
cpt test A -i                 # short form of --interactive
```

Custom test cases are saved as `A_3.in`/`A_3.out` (next available index).

### Bundling with Local Libraries

You can bundle your personal library or templates into a single submission file. The bundler resolves headers by looking at paths defined in your `config.json`.

**1. Configure the Include Paths:**
*Add your library paths using the -I flag in the compiler_flags list. Tilde expansion (~) is supported.

```json
// ~/.config/cptools/config.json
{
  "compiler_flags": [
    "-O2",
    "-std=c++17",
    "-I/home/user/my-library",
    "-I~/cp-templates"
  ]
}
```

**2. Use Quotes for Includes:**
The bundler only processes headers included with double quotes (`""`). System headers using angle brackets (`<>`) are ignored and left as-is.

```cpp
#include <vector>           // Ignored (system header)
#include "segtree.hpp"      // Bundled! (Found in -I paths)
#include "graph/dsu.hpp"    // Bundled!
```

**3. Run the Bundle Command:**

```bash
cpt bundle A                  # Copy expanded code to clipboard
cpt bundle A -o submit.cpp    # Save bundled version to file
cpt bundle A -i               # Replace original file in-place
```

### Batch Operations with Ranges

Work with multiple problems at once:

```bash
cpt fetch A~F                 # fetch samples for A, B, C, D, E, F
cpt mark A~C AC               # mark A, B, C as accepted
cpt mark D~E WA               # mark D, E as wrong answer
```

### Isolated Problems (Problemset)

Problems outside contests are organized in `Platform/Problemset/`:

```bash
# Add isolated problems
cpt add https://codeforces.com/problemset/problem/1234/A
# Creates: Codeforces/Problemset/1234A.cpp

cpt add https://atcoder.jp/contests/abc300/tasks/abc300_a
# Creates: AtCoder/Problemset/abc300_a.cpp

# Add and fetch test cases automatically
cpt add https://codeforces.com/problemset/problem/1234/A -f

# Work with them
cd Codeforces/Problemset
cpt test 1234A
cpt mark 1234A AC
```

### Repository Maintenance

Keep your repository clean:

```bash
cpt clean --all               # remove all binaries recursively
cpt update --all              # regenerate info.md for all contests
cpt commit Codeforces/1234    # commit specific contest
```

### Advanced Configuration

Example of customized `~/.config/cptools/config.json`:

```json
{
  "author": "YourName",
  "compiler": "g++",
  "compiler_flags": ["-O2", "-std=c++20", "-Wall", "-Wextra", "-fsanitize=address"],
  "cookie_cache_max_age_hours": -1,
  "preferred_browser": "firefox"
}
```

**Tips:**

- Add `-fsanitize=address` to catch memory errors during testing
- Set `cookie_cache_max_age_hours` to `-1` to never expire (only refresh on auth failure)
- Use `-std=c++20` or `-std=c++17` based on judge requirements

## Directory Structure

Contests are organized by platform:

```text
contests/
├── Trainings/          # Codeforces group contests
│   └── 2024.01.15/
│       ├── A.cpp
│       ├── B.cpp
│       └── info.md
├── Codeforces/
│   ├── 1234/
│   ├── Gym/
│   └── Problemset/
├── AtCoder/
│   └── Problemset/
├── CSES/
├── Yosupo/
├── SPOJ/
├── vJudge/
└── Other/
```

Each `.cpp` file includes a metadata header:

```cpp
/**
 * Author:      Lua
 * Problem:     A - Example Problem
 * Link:        https://codeforces.com/contest/1234/problem/A
 * Status:      AC
 * Created:     15-01-2024 14:30:00
 **/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
