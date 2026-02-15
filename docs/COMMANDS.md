# Command Reference

Complete reference for all cptools commands.

> **Note:** All commands can be invoked using either `cptools` or the shorter alias `cpt`.
> For example: `cptools test A` is equivalent to `cpt test A`.

## Table of Contents

- [Contest Management](#contest-management)
  - [new](#cptools-new-url)
  - [init](#cptools-init-directory)
  - [update](#cptools-update-directory)
  - [status](#cptools-status-directory)
- [Problem Management](#problem-management)
  - [add](#cptools-add-nameurl-directory)
  - [rm](#cptools-rm-problem-directory)
  - [mark](#cptools-mark-problem-status-directory)
  - [open](#cptools-open-problem-directory)
  - [add_header](#cptools-add_header-file-options)
- [Testing & Validation](#testing--validation)
  - [test](#cptools-test-problem-directory)
  - [fetch](#cptools-fetch-problem-directory)
  - [stress](#cptools-stress-solution-brute-gen---checker-checker)
- [Build & Deploy](#build--deploy)
  - [bundle](#cptools-bundle-problem-directory)
  - [clean](#cptools-clean-directory)
  - [commit](#cptools-commit-directory)
- [Utilities](#utilities)
  - [config](#cptools-config)
  - [completion](#cptools-completion-options)
  - [hash](#cptools-hash-problem-options)

---

## Contest Management

### `cptools new [url]`

Create a new contest directory with solution files.

**Usage:**

```bash
cptools new [url]
```

**Arguments:**

- `url` (optional): Contest URL from supported platforms

**Examples:**

```bash
cpt new https://codeforces.com/contest/1234
cpt new https://atcoder.jp/contests/abc300
cpt new https://codeforces.com/group/yc7Yxny414/contest/123456
cpt new  # interactive mode - prompts for platform and contest info
```

**Behavior:**

- Auto-detects platform from URL
- Fetches problem names via platform API when available
- Prompts for contest name (defaults to contest ID or current date for trainings)
- Prompts for problem range if API fetch fails
- Creates `.cpp` files with cptools headers and template code
- Organizes contests in appropriate platform directory
- For Codeforces group contests, uses configured `default_group_id`
- Automatically generates `info.md` after creation
- Skips files that already exist (won't overwrite)
- Interactive mode (no URL): prompts for platform, contest ID, and problem range

**Supported Platforms:**

- **Codeforces**: Regular contests, gym, problemset, group/training contests
- **AtCoder**: Contests and problemset
- **CSES**: CSES Problem Set
- **Yosupo**: Library Checker (algorithm library)
- **SPOJ**: Sphere Online Judge
- **vJudge**: Virtual judge platform
- **Other**: Manual setup for custom/unsupported platforms

---

### `cptools init [directory]`

Initialize a new competitive programming repository.

**Usage:**

```bash
cptools init [directory]
```

**Arguments:**

- `directory` (optional): Path to initialize (default: current directory)

**Options:**

- `--no-git`: Skip `git init`

**Examples:**

```bash
cpt init             # initialize current directory
cpt init ~/contests  # initialize in specific path
cpt init --no-git    # initialize without git
```

**Behavior:**

Creates the following structure:

```text
.
├── Trainings/             # Codeforces group contests
├── Codeforces/
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

Also creates:

- `.gitignore` with common patterns (compiled binaries, test files, etc.)
- Runs `git init` unless `--no-git` is specified
- Ensures config file exists at `~/.config/cptools/config.json`

**Note:** Subdirectories like `Codeforces/Gym/` and `Codeforces/Problemset/` are created automatically when needed by the `new` or `add` commands.

---

### `cptools update [directory]`

Generate or update `info.md` for contest directories.

**Usage:**

```bash
cptools update [directory] [options]
```

**Arguments:**

- `directory` (optional): Specific contest directory (default: current)

**Options:**

- `-a, --all`: Update all contests recursively

**Examples:**

```bash
cpt update              # update current directory
cpt update -a           # update all contests
cpt update --all        # same as -a
cpt update Codeforces/1234
```

**Behavior:**

- Scans `.cpp` files in directory
- Reads cptools headers to extract problem info and status
- Generates or updates `info.md` with problem list, status, and statistics
- Shows AC/WA/TLE/etc. counts
- With `-a/--all`: recursively updates all contest directories in the repository
- Automatically runs after `rm` command
- Skips files without cptools headers

---

### `cptools status [directory]`

Show contest progress summary.

**Usage:**

```bash
cptools status [directory] [options]
```

**Arguments:**

- `directory` (optional): Contest directory (default: current)

**Options:**

- `--grid`: Force grid/compact display mode
- `--wide`: Force wide/normal display mode

**Examples:**

```bash
cpt status
cpt status /path/to/contest
cpt status --grid       # force compact grid view
cpt status --wide       # force wide table view
```

**Behavior:**

Displays a colored table with:

- Problem names
- Status (AC, WA, TLE, MLE, RE, WIP, ~)
- Summary statistics
- Automatically detects terminal width and switches between grid (compact) and wide (table) display modes
- Prompts to add headers to files without cptools metadata

---

## Problem Management

### `cptools add <name|url> [directory]`

Add a solution file. Accepts a problem name (local) or a URL (isolated problem).

**Usage:**

```bash
cptools add <name|url> [directory] [options]
```

**Arguments:**

- `name|url`: Problem identifier or URL
- `directory` (optional): Target directory (for name-based add)

**Options:**

- `-f, --fetch`: Fetch test cases automatically (only when adding via URL)

**Examples:**

```bash
# Local problems (in contest directory)
cpt add A            # creates A.cpp in current dir
cpt add B-brute      # creates B-brute.cpp
cpt add dp_a         # creates dp_a.cpp

# Isolated problems - creates in Platform/Problemset/
cpt add https://codeforces.com/problemset/problem/1234/A
cpt add https://codeforces.com/contest/1999/problem/G2
cpt add https://atcoder.jp/contests/abc300/tasks/abc300_a

# Fetch test cases automatically when adding
cpt add https://codeforces.com/problemset/problem/1234/A -f
cpt add https://codeforces.com/contest/1999/problem/G2 --fetch
```

**Behavior:**

- Creates `.cpp` file with cptools metadata header and template code
- For local problems: creates file in specified/current directory
- For URLs: automatically organizes in `Platform/Problemset/` directory
- Fetches problem name from URL when possible (requires valid URL)
- Uses configured author name from `config.json`
- Includes timestamp in header
- Won't overwrite existing files
- With `-f/--fetch` flag (URL only): automatically fetches sample test cases after creating the file

---

### `cptools rm <problem>... [directory]`

Remove problem files and their associated test cases.

**Usage:**

```bash
cptools rm <problem>... [directory]
```

**Arguments:**

- `problem`: Problem ID(s) to remove (supports ranges)
- `directory` (optional): Target directory (default: current)

**Examples:**

```bash
cpt rm A                        # remove A from current directory
cpt rm KQUERY.cpp               # remove KQUERY (extension stripped)
cpt rm dp_a dp_b                # remove multiple problems
cpt rm A B /path/to/contest     # remove A and B from specific directory
cpt rm A~E                      # remove A, B, C, D, E
cpt rm A~C /path/to/contest     # remove range from specific directory
```

**Behavior:**

- Removes `.cpp` source file
- Removes all sample test files (`problem_*.in`, `problem_*.out`)
- Removes compiled binary (hidden dot file like `.A`)
- Removes `.hashed` file if exists
- Shows confirmation prompt when removing >3 problems
- Supports range notation (A~E) to remove multiple problems
- Strips `.cpp` extension from arguments if provided
- Automatically updates `info.md` after removal
- Removes `info.md` if no problems remain in directory

---

### `cptools mark <problem> [status] [directory]`

Update problem status in the file header.

**Usage:**

```bash
cptools mark <problem> [status] [directory]
```

**Arguments:**

- `problem`: Problem ID or range
- `status` (optional): Status code (default: AC)
- `directory` (optional): Target directory

**Status Codes:**

- `AC` - Accepted
- `WA` - Wrong Answer
- `TLE` - Time Limit Exceeded
- `MLE` - Memory Limit Exceeded
- `RE` - Runtime Error
- `WIP` - Work in Progress
- `~` - Pending/Not attempted

**Examples:**

```bash
cpt mark A           # mark as AC (default)
cpt mark B WA
cpt mark C TLE
cpt mark A~E AC      # mark range A through E
```

**Behavior:**

- Updates the `Status:` field in the file's cptools header
- Supports range notation (A~E) to mark multiple problems at once
- Preserves other header information (author, problem name, link, etc.)
- If status is omitted, defaults to `AC`
- Automatically updates `info.md` if it exists

---

### `cptools open <problem> [directory]`

Open the problem's URL in the browser.

**Usage:**

```bash
cptools open <problem> [directory]
```

**Arguments:**

- `problem`: Problem ID
- `directory` (optional): Target directory

**Examples:**

```bash
cpt open A           # reads Link from A.cpp header, opens with xdg-open
cpt open B /path/to/contest
```

**Behavior:**

- Reads the `Link:` field from the problem's cptools header
- Opens URL with system default browser (`xdg-open` on Linux)
- Shows error if link not found or header is missing
- Requires the problem file to have a valid cptools header with Link field

---

### `cptools add_header <file> [options]`

Add a cptools header to an existing C++ file that doesn't have one.

**Usage:**

```bash
cptools add_header <file> [options]
```

**Arguments:**

- `file`: Path to `.cpp` file

**Options:**

- `-l, --link LINK`: Problem URL
- `-n, --name NAME`: Problem name
- `-s, --status STATUS`: Initial status (default: ~)
- `-f, --force`: Overwrite existing header

**Examples:**

```bash
cpt add_header A.cpp
cpt add_header solution.cpp --name "Two Sum" --link "https://..."
cpt add_header old.cpp --force
```

**Behavior:**

- Adds cptools metadata header to the top of an existing C++ file
- Preserves all original file contents below the header
- Uses configured author name from `config.json`
- Generates current timestamp
- Can overwrite existing header with `--force` flag
- Useful for adopting legacy code or external solutions into cptools workflow
- The header includes: Author, Problem, Link, Status, and Created timestamp

---

## Testing & Validation

### `cptools test <problem> [directory]`

Compile and test a solution.

**Usage:**

```bash
cptools test <problem> [directory]
```

**Arguments:**

- `problem`: Problem ID
- `directory` (optional): Target directory

**Options:**

- `--add`: Add custom test case (input + expected output)
- `--no-out`: With `--add`, skip expected output (input only)
- `-i, --interactive`: Force interactive mode even if samples exist

**Examples:**

```bash
cpt test A                  # runs against fetched samples if available
cpt test A < input.txt      # pipe custom input
cpt test A                  # interactive stdin if no samples
cpt test A --add            # add custom test case (input + expected output)
cpt test A --add --no-out   # add custom test case (input only)
cpt test A --interactive    # run interactively even if samples exist
cpt test A -i               # short form of --interactive
```

**Behavior:**

- Compiles with configured compiler and flags
- If sample files exist (from `cpt fetch`), tests against each one
- With `--interactive` flag, runs in interactive mode regardless of samples
- Reports PASS/FAIL with diff for failures
- Displays execution time and memory usage (RSS/VM) for each test
- Memory tracking uses aggressive sampling to catch startup allocations
- With `--add`, prompts for input (and optionally output) via stdin
- Saves custom tests as next available index (e.g., `A_3.in`/`A_3.out`)
- Shows compilation errors if build fails
- Test timeout: 10 seconds per test case

---

### `cptools fetch <problem> [directory]`

Fetch sample test cases from the problem page.

**Usage:**

```bash
cptools fetch <problem> [directory]
```

**Arguments:**

- `problem`: Problem ID or range
- `directory` (optional): Target directory

**Examples:**

```bash
cpt fetch A          # fetch samples for problem A
cpt fetch A~E        # fetch for all problems A through E
```

**Behavior:**

- Reads the `Link:` field from problem header to determine URL
- Fetches sample inputs and outputs from the problem page
- Saves as `A_1.in`, `A_1.out`, `A_2.in`, `A_2.out`, etc.
- Numbering starts from 1 for each problem
- Supports range notation (A~E) to fetch for multiple problems
- Requires browser cookies for authentication (reads from browser)
- Uses cookie cache to avoid repeated browser access (configurable in `config.json`)
- Cookie cache expires after `cookie_cache_max_age_hours` (default: 24 hours)
- Set `cookie_cache_max_age_hours: -1` to never expire cookies
- Auto-detects browser or uses `preferred_browser` from config

**Supported Platforms:**

- **Codeforces**: Contest, gym, problemset, group contests
- **AtCoder**: Contests and problemset

**Note:** CSES, Yosupo, SPOJ, and vJudge are also supported for the `new` and `add` commands, but may not support automatic sample fetching.

---

### `cptools stress <solution> <brute> <gen> [--checker <checker>]`

Stress test: compare solution vs brute force with random inputs.

**Usage:**

```bash
cptools stress <solution> <brute> <gen> [--checker <checker>]
```

**Arguments:**

- `solution`: Main solution file
- `brute`: Brute force solution file
- `gen`: Test case generator file
- `--checker` (optional): Custom checker program

**Examples:**

```bash
cpt stress A A-brute gen
cpt stress A A-brute gen --checker checker
```

**Behavior:**

- Compiles all three programs (solution, brute, generator)
- Runs generator with iteration number as argument: `./gen 1`, `./gen 2`, ...
- Feeds generated input to both solution and brute force
- Compares outputs byte-by-byte (default, without checker)
- With `--checker`: runs `./checker input_file solution_output brute_output`
- Stops on first mismatch
- Shows iteration number, input, and both outputs on failure
- Runs indefinitely until mismatch or manual stop (Ctrl+C)
- Reports progress every iteration

**Generator Requirements:**

- Must be a C++ file (`.cpp`)
- Accepts iteration number as first command-line argument (argv[1])
- Outputs test case to stdout
- Should produce varied, random test cases based on iteration number seed
- Example: `gen.cpp` that takes iteration `i` and generates random test

**Checker Requirements (optional):**

- Must be a C++ file (`.cpp`)
- Accepts three command-line arguments:
  1. `input_file`: Path to generated input file
  2. `solution_output`: Path to solution's output file
  3. `brute_output`: Path to brute force's output file
- Exit code 0 = outputs match (correct)
- Non-zero exit code = outputs differ (mismatch found)
- Useful for problems with multiple correct outputs

---

## Build & Deploy

### `cptools bundle <problem> [directory]`

Expand local includes and copy the source code to the clipboard.

**Usage:**

```bash
cptools bundle <problem> [directory]
```

**Arguments:**

- `problem`: Problem ID
- `directory` (optional): Target directory

**Options:**

- `-o <file>`: Save bundled code to file
- `-i`: Modify original file in-place

**Examples:**

```bash
cpt bundle A            # copies bundled code to clipboard
cpt bundle A -o a.cpp   # saves bundled code to 'a.cpp'
cpt bundle A -i         # modifies A.cpp in-place
```

**Behavior:**

- Recursively inlines local header files (e.g., `#include "lib/segtree.hpp"`)
- Only processes headers included with double quotes (`""`), not angle brackets (`<>`)
- Resolves include paths using `-I` flags from `compiler_flags` in config.json
- Expands into a single compilation unit suitable for submission
- Deduplicates system headers (`#include <...>`) - keeps only first occurrence
- Deduplicates `using namespace std;` statements
- Removes `#pragma once` directives from included files
- Strips block comments (`/* ... */`) from included library files
- Preserves the cptools header comment block
- Default behavior: copies bundled code to system clipboard
- Falls back to stdout if clipboard unavailable
- With `-o FILE`: saves to specified output file
- With `-i`: overwrites original file in-place (use with caution)

---

### `cptools clean [directory]`

Remove compiled binaries and build artifacts.

**Usage:**

```bash
cptools clean [directory] [options]
```

**Arguments:**

- `directory` (optional): Specific directory (default: current)

**Options:**

- `-r, --recursive`: Recursive clean (subdirectories)
- `-a, --all`: Clean all platform directories in the repo

**Examples:**

```bash
cpt clean            # clean current directory (non-recursive)
cpt clean -r         # clean current directory recursively
cpt clean --recursive # same as -r
cpt clean -a         # clean all platform directories (recursive)
cpt clean --all      # same as -a
```

**Behavior:**

- Removes compiled binaries (hidden executables like `.A`, `.B`, etc.)
- Removes `.hashed` files generated by the hash command
- Default: cleans only current directory (non-recursive)
- With `-r/--recursive`: scans and cleans all subdirectories
- With `-a/--all`: cleans all platform directories (Trainings/, Codeforces/, AtCoder/, vJudge/, Other/, Yosupo/)
- Reports number of files removed
- Safe operation - only removes build artifacts, never source files

---

### `cptools commit [directory]`

Commit and push changes for a specific contest or directory.

**Usage:**

```bash
cptools commit [directory] [options]
```

**Arguments:**

- `directory` (optional): Directory to commit (default: current)

**Options:**

- `-a, --all`: Commit all changed contests in the repository

**Examples:**

```bash
cpt commit              # commits changes in the current directory
cpt commit .            # same as above
cpt commit vJudge/191B  # commits a specific directory
cpt commit -a           # commit all changed contests
cpt commit --all        # same as -a
```

**Behavior:**

- Runs `git add <directory>` to stage changes
- Generates commit message based on directory path and contest info
- Runs `git commit` with auto-generated message
- Runs `git push` to remote repository
- With `-a/--all`: commits all changed contests in the repository
- Shows git output for verification
- Requires the directory to be part of a git repository

**Commit Message Format:**

- For contests: `solve: [Platform]/[Contest]` (e.g., `solve: Codeforces/1234`)
- For specific problems: includes problem identifier
- Message is auto-generated based on directory structure

---

## Utilities

### `cptools config`

Edit configuration file.

**Usage:**

```bash
cptools config
```

**Behavior:**

- Opens `~/.config/cptools/config.json` in default editor (`$EDITOR` or `vim`)
- Creates default config file if it doesn't exist
- Config file is in JSON format
- Changes take effect immediately (no restart needed)

**Configuration Options:**

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

**Fields:**

- `author`: Your name, used in file headers (e.g., "John Doe")
- `default_group_id`: Default Codeforces group ID for training contests
- `compiler`: C++ compiler command (e.g., `g++`, `clang++`, `g++-11`)
- `compiler_flags`: Array of compiler flags for building solutions
  - Include optimization flags like `-O2`
  - Include standard version like `-std=c++17` or `-std=c++20`
  - Add include paths with `-I` for bundling custom libraries (supports `~` expansion)
  - Example: `["-O2", "-std=c++20", "-Wall", "-I~/my-cp-library"]`
- `cookie_cache_enabled`: Enable/disable browser cookie caching (default: `true`)
  - Set to `false` to always read fresh cookies from browser
- `cookie_cache_max_age_hours`: Cookie cache duration in hours (default: 24)
  - Set to `-1` to never expire (only refresh on authentication failure)
  - Recommended: 24-48 hours for active use
- `preferred_browser`: Browser for authentication
  - `null`: Auto-detect installed browser (Firefox, Chrome, Edge, etc.)
  - `"firefox"`, `"chrome"`, `"edge"`, etc.: Use specific browser

---

### `cptools completion [options]`

Generate or install shell completion.

**Usage:**

```bash
cptools completion [options]
```

**Options:**

- `--install`: Install completion for your current shell (auto-detected)
- `--shell SHELL`: Output completion script for specific shell (bash or zsh)

**Examples:**

```bash
cptools completion --install        # auto-detect and install
cptools completion --shell bash     # output bash completion script
cptools completion --shell zsh      # output zsh completion script
```

**Behavior:**

- Auto-detects shell (bash or zsh)
- Generates completion script
- With `--install`: installs to `~/.config/cptools/completion.{bash,zsh}`
- Adds source line to `~/.bashrc` or `~/.zshrc`
- Restart your shell or run `source ~/.bashrc` (or `~/.zshrc`) after installation

**Completion Features:**

- **Command completion**: Tab-completes all cptools subcommands
- **Flag completion**: Context-aware flag suggestions for each command
- **File completion**: Auto-completes `.cpp` files for commands like `add`, `rm`, `mark`, `open`, `test`, `bundle`
- **Directory completion**: Completes directories for commands like `update`, `new`

---

### `cptools hash <problem> [options]`

Hash lines of a C++ file with context awareness.

**Usage:**

```bash
cptools hash <problem> [options]
```

**Arguments:**

- `problem`: Problem file

**Options:**

- `-s, --save`: Save output to `.hashed` file instead of stdout

**Examples:**

```bash
cpt hash A        # output to stdout
cpt hash A -s     # save to A.hashed
```

**Behavior:**

- Generates a context-aware hash for each line of C++ code
- Each line gets a 3-character hash based on its context and surrounding code
- Useful for comparing code structure while ignoring variable names
- Compiles hasher from template on first use
- Caches hasher binary in `~/.cache/cptools/hasher`
- Default: outputs to stdout
- With `-s/--save`: saves to `<problem>.hashed` file

**How it Works:**

- Analyzes code structure and patterns
- Similar code structures produce similar hashes
- Independent of variable/function names
- Considers context (surrounding lines and nesting)

**Use Cases:**

- Code comparison and diff visualization
- Plagiarism detection (identify structurally similar code)
- Identifying structural similarities between different solutions
- Debugging and code analysis
- Finding duplicate code patterns

---

## See Also

- [README.md](../README.md) - Quick start guide
- [Advanced Usage Examples](../README.md#advanced-usage-examples) - Workflow examples
