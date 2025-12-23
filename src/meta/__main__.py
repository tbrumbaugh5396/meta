"""Entry point wrapper to ensure correct path setup."""
import sys
import os

# Get the src directory (parent of meta package)
_src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Ensure src is in path FIRST to override any conflicting meta packages
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# Now import and run
from meta.cli import main

if __name__ == "__main__":
    sys.exit(main())

