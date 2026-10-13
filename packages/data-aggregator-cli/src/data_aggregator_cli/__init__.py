import logging
import sys

logging.basicConfig(  # ruff: ignore[non-empty-init-module]
  level=logging.DEBUG,
  format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
  handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("aggregator.log")],
)

from .__main__ import main as main  # ruff: ignore[module-import-not-at-top-of-file]
