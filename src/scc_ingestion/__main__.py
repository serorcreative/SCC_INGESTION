"""Permet ``python -m scc_ingestion``."""

from __future__ import annotations

import sys

from scc_ingestion.cli import main

if __name__ == "__main__":
    sys.exit(main())
