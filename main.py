"""Copy the pre-rendered entry.png next to this script into $MAKEFUN_OUTPUT_DIR (default /output)."""

import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dest)
    print(dest)


if __name__ == "__main__":
    main()
