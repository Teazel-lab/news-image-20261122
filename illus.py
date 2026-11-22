"""Illustration registry: ILLUS maps a story id to a function (w, h) -> inline <svg> string.

Merges ILLUS_A (illus_a.py) and ILLUS_B (illus_b.py); either module may be missing.
"""

ILLUS = {}

try:
    from illus_a import ILLUS_A
    ILLUS.update(ILLUS_A)
except ImportError:
    pass

try:
    from illus_b import ILLUS_B
    ILLUS.update(ILLUS_B)
except ImportError:
    pass
