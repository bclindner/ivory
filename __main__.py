#!/usr/bin/env python3
"""
Main "executable" for Ivory.

Running this file will start Ivory in watch mode, using the config provided in
config.json.
"""

import logging
import sys
import json
from ivory import Ivory
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    try:
        # set up logging
        logging.basicConfig(stream=sys.stdout)
        with open("config.json") as config_file:
            config = json.load(config_file)
        logging.getLogger().setLevel(config.get('loglevel', logging.INFO))
        # start up ivory in watch mode
        Ivory(**config).watch()
    except OSError as err:
        logger.exception("failed to load config file")
        exit(1)
    except KeyboardInterrupt as err:
        logger.info("interrupt signal detected, exiting")
        exit(1)
