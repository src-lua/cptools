import os
import subprocess

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def get_repo_root():
    """Find the git root of the current working directory."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return os.getcwd()

PLATFORM_DIRS = ['Trainings', 'Codeforces', 'vJudge', 'AtCoder', 'Yosupo', 'CSES', 'Other']
