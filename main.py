"""Copy the pre-rendered entry.png (next to this file) to $MAKEFUN_OUTPUT_DIR (default /output)."""
import os
import shutil

src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
os.makedirs(out_dir, exist_ok=True)
dst = os.path.join(out_dir, "entry.png")
shutil.copyfile(src, dst)
print(dst)
