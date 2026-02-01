#!/usr/bin/env python3
"""
Hash lines of a C++ file with context awareness.

Usage:
    cptools hash <problem>

Generates a 3-character hash for each line based on its context
(accumulated code from enclosing blocks). Useful for detecting
structural changes in code.
"""
import os
import sys
import subprocess
import tempfile

from .common import Colors

# The C++ hasher script
HASHER_SOURCE = r"""#include <bits/stdc++.h>

using namespace std;

string getHash(string s){
	ofstream("z.cpp") << s;
	system("g++ -E -P -dD -fpreprocessed ./z.cpp | tr -d '[:space:]' | md5sum > sh");
	ifstream("sh") >> s;
	return s.substr(0, 3);
}
int main(){
	string l, t;
	stack<string> st({""});
	while(getline(cin, l)){
        t = l;
		for(auto c : l)
			if(c == '{') st.push(""); else
			if(c == '}') t = st.top()+l, st.pop();
		cout << getHash(t) + " " + l << endl;
		st.top() += t;
	}
}
"""

def get_or_compile_hasher():
    """Get the hasher binary path, compiling it if necessary."""
    # Store in ~/.cache/cptools/
    cache_dir = os.path.expanduser("~/.cache/cptools")
    os.makedirs(cache_dir, exist_ok=True)

    hasher_bin = os.path.join(cache_dir, "hasher")
    hasher_src = os.path.join(cache_dir, "hasher.cpp")

    # Check if binary exists and is newer than source
    needs_compile = not os.path.exists(hasher_bin)

    if not needs_compile and os.path.exists(hasher_src):
        # Check if source changed
        with open(hasher_src, 'r') as f:
            if f.read() != HASHER_SOURCE:
                needs_compile = True

    if needs_compile or not os.path.exists(hasher_src):
        # Write source
        with open(hasher_src, 'w') as f:
            f.write(HASHER_SOURCE)

        # Compile
        result = subprocess.run(
            ['g++', '-O2', '-std=c++17', hasher_src, '-o', hasher_bin],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"{Colors.FAIL}Error compiling hasher:{Colors.ENDC}")
            print(result.stderr)
            sys.exit(1)

    return hasher_bin

def hash_file(filepath, filename, save_to_file=False):
    """Hash a C++ file and print results."""
    if not os.path.exists(filepath):
        print(f"{Colors.FAIL}Error: {filepath} not found{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)

    # Print status to stderr
    print(f"{Colors.HEADER}--- Hashing File ---{Colors.ENDC}\n", file=sys.stderr)
    print(f"  {Colors.BOLD}{filename}{Colors.ENDC}", file=sys.stderr)
    print(file=sys.stderr)

    hasher = get_or_compile_hasher()

    # Run hasher with file as input
    with open(filepath, 'r') as f:
        try:
            result = subprocess.run(
                [hasher],
                stdin=f,
                capture_output=True,
                text=True,
                check=True
            )

            # If saving to file
            if save_to_file:
                # Remove extension and add .hashed (A.cpp -> A.hashed)
                base_name = os.path.splitext(filepath)[0]
                output_file = base_name + '.hashed'
                output_name = os.path.splitext(filename)[0] + '.hashed'
                with open(output_file, 'w') as out:
                    out.write(result.stdout)
                print(f"{Colors.GREEN}✓ Hash saved to {output_name}{Colors.ENDC}", file=sys.stderr)
            else:
                # Output goes to stdout (can be redirected)
                print(result.stdout, end='')
                print(f"\n{Colors.GREEN}✓ Hash generated successfully{Colors.ENDC}", file=sys.stderr)

        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}Error running hasher:{Colors.ENDC}", file=sys.stderr)
            print(e.stderr, file=sys.stderr)
            sys.exit(1)
        finally:
            # Clean up temp files created by hasher
            for temp in ['z.cpp', 'sh']:
                if os.path.exists(temp):
                    os.remove(temp)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print(f"{Colors.BOLD}Usage:{Colors.ENDC} cptools hash <problem> [-s|--save]")
        print(f"\nGenerates a 3-character hash for each line of a C++ file.")
        print(f"The hash is context-aware (considers enclosing blocks).")
        print(f"\n{Colors.BOLD}Options:{Colors.ENDC}")
        print(f"  -s, --save    Save output to <problem>.hashed")
        print(f"\n{Colors.BOLD}Examples:{Colors.ENDC}")
        print(f"  cptools hash A           # Print to stdout")
        print(f"  cptools hash A -s        # Save to A.hashed")
        print(f"  cptools hash A > out.txt # Redirect to file")
        sys.exit(0 if len(sys.argv) > 1 else 1)

    # Parse arguments
    save_to_file = False
    problem = None

    for arg in sys.argv[1:]:
        if arg in ['-s', '--save']:
            save_to_file = True
        elif not arg.startswith('-'):
            problem = arg

    if not problem:
        print(f"{Colors.FAIL}Error: No problem specified{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)

    directory = os.getcwd()

    # Support both "A" and "A.cpp"
    if problem.endswith('.cpp'):
        filename = problem
    else:
        filename = f"{problem}.cpp"

    filepath = os.path.join(directory, filename)

    hash_file(filepath, filename, save_to_file)

if __name__ == "__main__":
    main()
