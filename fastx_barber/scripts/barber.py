"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber.const import __version__
from fastx_barber.scripts import arguments as ap
from fastx_barber import scripts
import sys


def default_parser(*args) -> None:
    print("fbarber -h for usage details.")
    sys.exit()


def main():
    parser = argparse.ArgumentParser(
        description=f"""
Version:    {__version__}
Author:     Gabriele Girelli
Docs:       http://ggirelli.github.io/fastx-barber
Code:       http://github.com/ggirelli/fastx-barber

FASTX barber tools.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.set_defaults(parse=default_parser)
    parser = ap.add_version_option(parser)

    subparsers = parser.add_subparsers(
        title="sub-commands",
        help="Access the help page for a sub-command with: sub-command -h",
    )

    scripts.find_seq.init_parser(subparsers)
    scripts.flag.init_parser(subparsers)
    scripts.match.init_parser(subparsers)
    scripts.trim.init_parser(subparsers)

    args = parser.parse_args()
    args = args.parse(args)
    args.run(args)
