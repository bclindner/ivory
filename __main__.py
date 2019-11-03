#!/usr/bin/env python3
"""
Main "executable" for Ivory.

Running this file will start Ivory in watch mode, using the config provided in
config.json.
"""

import logging
import sys
import json
import argparse
from ivory import Ivory
from constants import DEFAULT_CONFIG_PATH

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    argparser = argparse.ArgumentParser(
        description="A Mastodon automoderator.")
    argparser.add_argument("--config",
                           dest="configpath",
                           help="Path to the configuration file (default is config.json)",
                           default=DEFAULT_CONFIG_PATH)
    args = argparser.parse_args()
    try:
        # set up logging
        logging.basicConfig(stream=sys.stdout)
        with open(args.configpath) as config_file:
            config = json.load(config_file)
        logging.getLogger().setLevel(config.get('loglevel', logging.INFO))
        # start up ivory in watch mode
        Ivory(config).watch()
    except OSError as err:
        logger.exception("failed to load config file")
        exit(1)
    except KeyboardInterrupt as err:
        logger.info("interrupt signal detected, exiting")
        exit(1)
