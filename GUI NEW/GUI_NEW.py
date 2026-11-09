#!/usr/bin/env python
"""GUI_NEW.py - Startup entry point for Visual Studio and legacy runners.

Launches NIFRAP 2.0 (Modern Network Sniffer & Automated Web Intelligence Platform).
Legacy v1 implementation is preserved in GUI_NEW_v1_legacy.py.
"""

import sys
from pathlib import Path

# Add project root to sys.path so 'nifrap' package can be imported from any working directory
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from nifrap.gui.app import run

if __name__ == "__main__":
    run()
