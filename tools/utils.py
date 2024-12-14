import logging
import os


def init_logger():
    logging.basicConfig(
        level=(
            logging.INFO
            if os.getenv("DEBUG", "false").lower() != "true"
            else logging.DEBUG
        ),
        format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
        force=True,
        handlers=[logging.StreamHandler()],
    )
