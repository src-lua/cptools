# cptools

CLI toolkit for managing competitive programming contests and solutions.

Supports Codeforces, AtCoder, vJudge, and custom judges.

## Installation

```bash
git clone <repo-url>
cd cptools
./install.sh
```

This creates symlinks `cptools` and `cpt` in `~/.local/bin` and sets up zsh completions.

After installing, run `cptools config` to set your author name.

## Configuration

```bash
cptools config
```

Opens `~/.config/cptools/config.json` in your editor. Default config:

```json
{
    "author": "Lua",
    "default_group_id": "yc7Yxny414",
    "compiler": "g++",
    "compiler_flags": ["-O2", "-std=c++17"]
}
```

## Commands

### `cptools new [url]`

Create a new contest directory with solution files.

```bash
cpt new https://codeforces.com/contest/1234
cpt new https://atcoder.jp/contests/abc300
cpt new  # interactive mode
```

Auto-detects platform from URL, fetches problem names via API, and creates `.cpp` files with headers and template.

### `cptools add <name|url> [directory]`

Add a solution file. Accepts a problem name (local) or a URL (isolated problem).

```bash
cpt add A2           # creates A2.cpp in current dir
cpt add B-brute      # creates B-brute.cpp

# Isolated problems — creates file in Platform/Problemset/:
cpt add https://codeforces.com/problemset/problem/1234/A
cpt add https://codeforces.com/contest/1999/problem/G2
cpt add https://atcoder.jp/contests/abc300/tasks/abc300_a
```

### `cptools mark <problem> [status] [directory]`

Update problem status in the file header.

```bash
cpt mark A           # mark as AC (default)
cpt mark B WA
cpt mark A~E AC      # mark range
```

Statuses: `AC`, `WA`, `TLE`, `MLE`, `RE`, `WIP`, `~` (pending)

### `cptools status [directory]`

Show contest progress summary.

```bash
cpt status
cpt status /path/to/contest
```

### `cptools open <problem> [directory]`

Open the problem's URL in the browser.

```bash
cpt open A           # reads Link from A.cpp header, opens with xdg-open
```

### `cptools test <problem> [directory]`

Compile and test a solution.

```bash
cpt test A                  # runs against fetched samples if available
cpt test A < input.txt      # pipe custom input
cpt test A                  # interactive stdin if no samples
cpt test A --add            # add custom test case (input + expected output)
cpt test A --add --no-out   # add custom test case (input only)
```

If sample files exist (from `cpt fetch`), tests against each one and reports PASS/FAIL. Uses compiler and flags from config.

With `--add`, prompts for input (and optionally output) via stdin, saving as the next available index (e.g., `A_3.in`/`A_3.out`).

### `cptools fetch <problem> [directory]`

Fetch sample test cases from the problem page.

```bash
cpt fetch A          # fetch samples for problem A
cpt fetch A~E        # fetch for all problems A through E
```

Saves as `A_1.in`, `A_1.out`, `A_2.in`, `A_2.out`, etc. Supports Codeforces and AtCoder.

### `cptools stress <solution> <brute> <gen> [--checker <checker>]`

Stress test: compare solution vs brute force with random inputs.

```bash
cpt stress A A-brute gen
cpt stress A A-brute gen --checker checker
```

- `gen` receives the iteration number as argument (`./gen 1`, `./gen 2`, ...)
- Without `--checker`, outputs are compared byte-by-byte
- With `--checker`, runs `./checker input output_sol output_brute`
- Stops on first mismatch, showing input and both outputs

### `cptools clean [-r] [--all | directory]`

Remove compiled binaries and build artifacts.

```bash
cpt clean            # clean current directory (non-recursive)
cpt clean -r         # clean current directory recursively
cpt clean --all      # clean all platform directories (recursive)
```

### `cptools update [--all | directory]`

Generate or update `info.md` for contest directories.

```bash
cpt update           # update current directory
cpt update --all     # update all contests
```

### `cptools init [directory]`

Initialize a new competitive programming repository.

```bash
cpt init             # initialize current directory
cpt init ~/contests  # initialize in specific path
```

Creates platform directories (`Trainings/`, `Codeforces/`, `vJudge/`, `AtCoder/`, `Other/`), `.gitignore`, and runs `git init`. Use `--nogit` to skip `git init`.

### `cptools bundle <problem> [directory]`

Expand local includes and copy the source code to the clipboard.

```bash
cpt bundle A            # copies bundled code to clipboard
cpt bundle A -o a.cpp   # saves bundled code to 'a.cpp'
cpt bundle A -i         # modifies A.cpp in-place
```

Recursively inlines local header files (e.g., #include "lgf-cpLib/seg.hpp") into a single unit.

- Default behavior copies directly to the system clipboard.
- Use `-o <file>` to save the output to a specific file.
- Use `-i` to overwrite the original source file with the bundled content.

### `cptools commit [directory]`

Commit and push changes for a specific contest or directory.

```bash
cpt commit              # commits changes in the current directory
cpt commit .            # same as above
cpt commit vJudge/191B  # commits a specific directory
```

Automates the git workflow: runs `git add <directory>`, `git commit` with an auto-generated message and `git push`.

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
│   └── 1234/
├── Codeforces/Gym/
├── Codeforces/Problemset/
├── vJudge/
├── AtCoder/
├── AtCoder/Problemset/
├── Yosupo/
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
