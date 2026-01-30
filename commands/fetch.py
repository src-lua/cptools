#!/usr/bin/env python3
"""
Fetch sample test cases from online judges.

Usage:
    cptools fetch <problem> [directory]
    cptools fetch A~E [directory]

Reads the Link from the problem's .cpp header and fetches sample
inputs/outputs, saving them as A1.in, A1.out, A2.in, A2.out, etc.
Supports Codeforces and AtCoder.
"""
import os
import sys
import re
from urllib.request import urlopen, Request
from urllib.error import URLError

from .common import Colors
from .update_info import read_problem_info

def parse_problems(input_str):
    """Parse problem range (A~E) or list (A B C)."""
    input_str = input_str.upper()
    if '~' in input_str:
        parts = input_str.split('~')
        if len(parts) == 2 and len(parts[0].strip()) == 1 and len(parts[1].strip()) == 1:
            start = ord(parts[0].strip())
            end = ord(parts[1].strip())
            return [chr(i) for i in range(start, end + 1)]
    return input_str.replace(',', ' ').split()

def fetch_html(url):
    """Fetch HTML content from a URL."""
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    req.add_header('Accept-Language', 'en-US,en;q=0.5')
    with urlopen(req, timeout=15) as response:
        return response.read().decode('utf-8')

def parse_codeforces_samples(html):
    """Parse sample tests from a Codeforces problem page."""
    samples = []

    # Find sample test section
    start = html.find('<div class="sample-test">')
    if start == -1:
        return samples

    section = html[start:]

    inputs = re.findall(r'<div class="input">.*?<pre[^>]*>(.*?)</pre>', section, re.DOTALL)
    outputs = re.findall(r'<div class="output">.*?<pre[^>]*>(.*?)</pre>', section, re.DOTALL)

    for inp, out in zip(inputs, outputs):
        inp = clean_sample_text(inp)
        out = clean_sample_text(out)
        samples.append({'input': inp, 'output': out})

    return samples

def parse_atcoder_samples(html):
    """Parse sample tests from an AtCoder problem page."""
    samples = []

    # AtCoder uses <h3>Sample Input 1</h3> followed by <pre>...</pre>
    # Match both English and Japanese headers
    input_pattern = r'(?:Sample Input|入力例)\s*(\d+)\s*</h3>\s*<pre>(.*?)</pre>'
    output_pattern = r'(?:Sample Output|出力例)\s*(\d+)\s*</h3>\s*<pre>(.*?)</pre>'

    inputs = re.findall(input_pattern, html, re.DOTALL)
    outputs = re.findall(output_pattern, html, re.DOTALL)

    input_map = {num: text for num, text in inputs}
    output_map = {num: text for num, text in outputs}

    for num in sorted(input_map.keys()):
        inp = clean_sample_text(input_map[num])
        out = clean_sample_text(output_map.get(num, ''))
        samples.append({'input': inp, 'output': out})

    return samples

def clean_sample_text(text):
    """Clean HTML from sample text."""
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</div>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    text = re.sub(r'\n{2,}', '\n', text)
    text = text.strip()
    return text

def detect_platform(url):
    """Detect which platform a URL belongs to."""
    if 'codeforces.com' in url:
        return 'codeforces'
    elif 'atcoder.jp' in url:
        return 'atcoder'
    elif 'judge.yosupo.jp' in url:
        return 'yosupo'
    return None

def fetch_samples(url):
    """Fetch sample test cases from a problem URL."""
    platform = detect_platform(url)
    if not platform:
        return None, "Unsupported platform"

    if platform == 'yosupo':
        return None, "Yosupo Library Checker auto-fetch not supported"

    try:
        html = fetch_html(url)
    except (URLError, Exception) as e:
        return None, str(e)

    if platform == 'codeforces':
        return parse_codeforces_samples(html), None
    elif platform == 'atcoder':
        return parse_atcoder_samples(html), None

    return None, "Unknown platform"

def save_samples(directory, problem, samples):
    """Save samples as A_1.in, A_1.out, A_2.in, A_2.out, etc."""
    saved = 0
    for i, sample in enumerate(samples, 1):
        in_path = os.path.join(directory, f"{problem}_{i}.in")
        out_path = os.path.join(directory, f"{problem}_{i}.out")

        with open(in_path, 'w') as f:
            f.write(sample['input'] + '\n')

        if sample['output']:
            with open(out_path, 'w') as f:
                f.write(sample['output'] + '\n')

        saved += 1
    return saved

def fetch_problem(problem, directory):
    """Fetch samples for a single problem."""
    filename = f"{problem}.cpp"
    filepath = os.path.join(directory, filename)

    if not os.path.exists(filepath):
        print(f"  {Colors.WARNING}! {filename} not found{Colors.ENDC}")
        return False

    info = read_problem_info(filepath)
    if not info or not info.get('link'):
        print(f"  {Colors.WARNING}! {filename} has no Link{Colors.ENDC}")
        return False

    url = info['link']
    platform = detect_platform(url)
    if not platform:
        print(f"  {Colors.WARNING}! Unsupported platform for {filename}{Colors.ENDC}")
        return False

    samples, error = fetch_samples(url)
    if error:
        print(f"  {Colors.FAIL}! {filename}: {error}{Colors.ENDC}")
        return False

    if not samples:
        print(f"  {Colors.WARNING}! No samples found for {filename}{Colors.ENDC}")
        return False

    count = save_samples(directory, problem, samples)
    print(f"  {Colors.GREEN}+ {problem}: {count} sample(s) saved{Colors.ENDC}")
    return True

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.FAIL}Usage: cptools fetch <problem(s)> [directory]{Colors.ENDC}")
        print(f"  Examples: cptools fetch A, cptools fetch A~E")
        sys.exit(1)

    problem_input = sys.argv[1]

    # Detect if argv[2] is a directory
    if len(sys.argv) > 2 and os.path.isdir(sys.argv[2]):
        directory = sys.argv[2]
    else:
        directory = os.getcwd()

    problems = parse_problems(problem_input)

    print(f"{Colors.HEADER}--- Fetching Samples ---{Colors.ENDC}\n")

    fetched = 0
    for p in problems:
        if fetch_problem(p, directory):
            fetched += 1

    print(f"\n{Colors.BOLD}Fetched {fetched}/{len(problems)} problem(s).{Colors.ENDC}")

if __name__ == "__main__":
    main()
