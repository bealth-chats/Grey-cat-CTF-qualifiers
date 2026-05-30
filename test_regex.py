import re
import time

ALPHA = r'a-zA-Z'
NUM = r'0-9'
OPS = r'=+\-\/:_\.'
QUOTES = r'\"\''
SPACE = r'\s'
DELIMS = r'\(\)\[\]'

base = f'[{ALPHA}{NUM}{OPS}{QUOTES}{SPACE}{DELIMS}]*?'
group_sq = f'\\[{base}\\]'
group_rd = f'\\({base}\\)'

pattern = re.compile(f'^({base}|{group_sq}|{group_rd})*$')

def test(s):
    start = time.time()
    try:
        pattern.fullmatch(s)
    except Exception as e:
        pass
    print(f"Length: {len(s)}, Time: {time.time() - start}")

test("a" * 20 + "!")
test("a" * 25 + "!")
test("a" * 30 + "!")
