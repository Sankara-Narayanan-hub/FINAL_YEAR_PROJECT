#!/usr/bin/env python3
"""
Root main.py entry point for FINAL_YEAR_PROJECT.
Automatically routes execution to Object_permanence/src/main.py with relative paths resolved.
"""

import os
import sys

# Convert any relative path arguments to absolute paths before changing directory
for i in range(1, len(sys.argv)):
    prev_arg = sys.argv[i - 1]
    if prev_arg in ("--input", "--input_dir", "--output", "--config"):
        curr_val = sys.argv[i]
        if not os.path.isabs(curr_val) and os.path.exists(curr_val):
            sys.argv[i] = os.path.abspath(curr_val)

# Change working directory to Object_permanence so relative paths (data/, config/, outputs/) resolve correctly
root_dir = os.path.dirname(os.path.abspath(__file__))
sub_dir = os.path.join(root_dir, "Object_permanence")

if os.path.exists(sub_dir):
    os.chdir(sub_dir)
    sys.path.insert(0, sub_dir)
else:
    sys.path.insert(0, root_dir)

from src.main import main

if __name__ == "__main__":
    main()
