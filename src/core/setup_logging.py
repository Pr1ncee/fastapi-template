import logging
import os
import sys


def setup_logging() -> None:
    logging.basicConfig(
        stream=sys.stderr,
        level=os.environ.get("LOGLEVEL", logging.INFO),
        format="[%(asctime)s %(levelname)-5s] %(message)s [%(filename)s:%(lineno)d]",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
