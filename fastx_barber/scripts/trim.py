"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber import scripts
from fastx_barber.scripts import arguments as ap
import sys


def default_parser(*args) -> None:
    print("fbarber trim -h for usage details.")
    sys.exit()


def init_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        __name__.split(".")[-1],
        description="""FASTX trimming tools.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Trim a FASTX file.",
    )
    parser.set_defaults(parse=default_parser)
    parser = ap.add_version_option(parser)

    sub_subparsers = parser.add_subparsers(
        title="sub-commands",
        help="Access the help page for a sub-command with: sub-command -h",
    )

    scripts.trim_len.init_parser(sub_subparsers)
    scripts.trim_qual.init_parser(sub_subparsers)
    scripts.trim_regex.init_parser(sub_subparsers)

    return parser
