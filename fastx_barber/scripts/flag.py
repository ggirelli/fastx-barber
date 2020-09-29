"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import argparse
from fastx_barber import scripts
from fastx_barber.scripts import arguments as ap
import sys


def default_parser(*args) -> None:
    print("fbarber flag -h for usage details.")
    sys.exit()


def init_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        __name__.split(".")[-1],
        description="""FASTX flag tools.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="FASTX flag tools.",
    )
    parser.set_defaults(parse=default_parser)
    parser = ap.add_version_option(parser)

    sub_subparsers = parser.add_subparsers(
        title="sub-commands",
        help="Access the help page for a sub-command with: sub-command -h",
    )

    scripts.flag_extract.init_parser(sub_subparsers)
    scripts.flag_filter.init_parser(sub_subparsers)
    scripts.flag_regex.init_parser(sub_subparsers)
    scripts.flag_split.init_parser(sub_subparsers)
    scripts.flag_stats.init_parser(sub_subparsers)

    return parser
