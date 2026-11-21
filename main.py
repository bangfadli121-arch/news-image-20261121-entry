#!/usr/bin/env python3
"""Grader entry point: copy entry.png into $MAKEFUN_OUTPUT_DIR.

Standard library only. No rendering happens here; draw.py builds the
image, this script just delivers the finished file to the grader.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print(dst)


if __name__ == "__main__":
    main()
