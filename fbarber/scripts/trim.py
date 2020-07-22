'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
'''

import argparse
from fbarber.const import __version__
import sys


def init_parser(subparsers: argparse._SubParsersAction
                ) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        __name__.split('.')[-1], description='''
Trim FASTX file.
''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="Trim a FASTX file..")

    parser.add_argument('input', type=str, metavar='in.fastx[.gz]',
                        help='''Path to the czi file to convert.''')

    parser.add_argument(
        '--pattern', type=str,
        help="""""", default=None)

    parser.add_argument(
        '--version', action='version', version=f'{sys.argv[0]} {__version__}')

    # advanced = parser.add_argument_group("advanced arguments")

    parser.set_defaults(parse=parse_arguments, run=run)

    return parser


def parse_arguments(args: argparse.Namespace) -> argparse.Namespace:
    return args


def run(args: argparse.Namespace) -> None:
    print("Running...")
    print("Done.")
