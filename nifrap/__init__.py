"""NIFRAP v2.0 - Network Intelligence Framework & Reconnaissance Automation Platform.

A unified framework for live packet sniffing, automatic HTTP/HTTPS detection,
targeted web scraping, and multi-format reporting.
"""

import warnings

# Suppress benign third-party library version warnings
warnings.filterwarnings("ignore", message=".*RequestsDependencyWarning.*")
warnings.filterwarnings("ignore", message=".*font file could not be loaded.*")

__version__ = "2.0.0"
__author__ = "NIFRAP Team"
