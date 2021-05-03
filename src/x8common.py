import logging
from pprint import pprint
from pprint import pformat
from datetime import datetime

# create logger with 'spam_application'
logger = logging.getLogger()


import argparse
import configparser

config = configparser.ConfigParser()


def debug_pprint(ds):

    if( logger.level == logging.DEBUG):
        logger.debug(pformat(ds))

#pp = pprint.PrettyPrinter(indent=4)

#logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
#timestring = time.strftime("%Y_%m_%d_%H_%M_%S")

def init_argparse(add_extra_arg = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Get the proxy list."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version 1.0.0"
    )

    parser.add_argument(
        "-log", 
        "--log", 
        default="debug",
        help=(
            "Provide logging level. "
            "Example --log debug', default='warning'"),
    )

    if add_extra_arg:
        add_extra_arg(parser)

    args = parser.parse_args()

    # Process some standard arguments:
    # log level
    levels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warn': logging.WARNING,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }
    level = levels.get(args.log.lower())

    if level is None:
        raise ValueError(
            f"log level given: {options.log}"
            f" -- must be one of: {' | '.join(levels.keys())}")
    else:
        logger.setLevel(level)

    #config file

    if(hasattr(args, 'config') and args.config):
        config.read(args.config)
    else:
        config.read('x8config.ini')

    logger.info(config.sections())

    return args

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


