#!/usr/bin/env python3
"""Launcher script for meta CLI that ensures correct path setup."""

import sys
import os
import importlib
import importlib.util

# Get the src directory (this file is in src/)
_src_dir = os.path.dirname(os.path.abspath(__file__))
# Ensure src is in path FIRST to override any conflicting meta packages
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# Remove any conflicting meta packages from sys.modules
# This ensures we import our meta package, not a conflicting one
if 'meta' in sys.modules:
    # Remove meta and all its submodules
    modules_to_remove = [
        k for k in list(sys.modules.keys()) if k.startswith('meta')
    ]
    for mod in modules_to_remove:
        del sys.modules[mod]

# Invalidate import caches to force Python to re-scan
importlib.invalidate_caches()

# Initialize the meta package properly by importing __init__.py first
_meta_init_path = os.path.join(_src_dir, 'meta', '__init__.py')
if os.path.exists(_meta_init_path):
    # Load meta package
    spec = importlib.util.spec_from_file_location('meta', _meta_init_path)
    meta_pkg = importlib.util.module_from_spec(spec)
    sys.modules['meta'] = meta_pkg
    spec.loader.exec_module(meta_pkg)

    # Now load cli module
    _cli_path = os.path.join(_src_dir, 'meta', 'cli.py')
    cli_spec = importlib.util.spec_from_file_location('meta.cli', _cli_path)
    cli_module = importlib.util.module_from_spec(cli_spec)
    sys.modules['meta.cli'] = cli_module
    cli_spec.loader.exec_module(cli_module)
    main = cli_module.main
else:
    # Fallback to normal import
    from meta.cli import main

if __name__ == "__main__":
    sys.exit(main())
