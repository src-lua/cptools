#!/usr/bin/env python3
"""
Usage: cptools hash <problem> [options]

Hash lines of a C++ file with context awareness.
Generates a 3-character hash for each line based on its context.

Options:
  -s, --save    Save output to .hashed file instead of stdout

Examples:
  cptools hash A
  cptools hash A -s
"""
import os
import sys
import argparse
import subprocess
import tempfile

from lib.io import error, success, header, bold, log

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
            error("Error compiling hasher:")
            print(result.stderr)
            sys.exit(1)

    return hasher_bin

def hash_file(filepath, filename, save_to_file=False):
    """Hash a C++ file and print results."""
    if not os.path.exists(filepath):
        error(f"Error: {filepath} not found")
        sys.exit(1)

    # Print status to stderr
    header("--- Hashing File ---")
    log()
    bold(f"  {filename}")
    log()

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
                success(f"✓ Hash saved to {output_name}")
            else:
                # Output goes to stdout (can be redirected)
                print(result.stdout, end='')
                success("\n✓ Hash generated successfully")

        except subprocess.CalledProcessError as e:
            error("Error running hasher:")
            log(e.stderr)
            sys.exit(1)
        finally:
            # Clean up temp files created by hasher
            for temp in ['z.cpp', 'sh']:
                if os.path.exists(temp):
                    os.remove(temp)

def get_parser():
    """Creates and returns the argparse parser for the hash command."""
    parser = argparse.ArgumentParser(description="Hash lines of a C++ file with context awareness.")
    parser.add_argument('problem', help='Problem file')
    parser.add_argument('-s', '--save', action='store_true', help='Save output to .hashed file instead of stdout')
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()

    problem = args.problem
    save_to_file = args.save

    directory = os.getcwd()

    # Support both "A" and "A.cpp"
    if problem.endswith('.cpp'):
        filename = problem
    else:
        filename = f"{problem}.cpp"

    filepath = os.path.join(directory, filename)

    hash_file(filepath, filename, save_to_file)
