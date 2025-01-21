import sys
import re
from typing import List


def preprocess(lines) -> List[str]:
    # Trim the program to useful lines
    ls = []
    for line in lines:
        line = line.strip()
        m = re.match(r"^([^;]*)(;.*)?", line)
        g = m.groups()[0]
        if g:
            ls.append(g)
    return ls


def main():
    fname = sys.argv[1]

    with open(fname) as f:
        lines = f.read().splitlines()

    lines = preprocess(lines)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
