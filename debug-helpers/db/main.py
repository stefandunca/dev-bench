from dbhelpers import *
from helpers import *

from datetime import datetime as dt
from dataclasses import dataclass, field
import argparse

import balance_history
import transactions

sub_commands = {
    'balance-history': balance_history,
    'transactions': transactions,
}

# Parse program arguments
parser = argparse.ArgumentParser(description='Balance history statistics')
parser.add_argument('--file', type=str, help='Path to the database file', required=True)
parser.add_argument('--pass', type=str, help='Password to the database file', required=True, dest='password')
parser.add_argument('--hash-password-uppercase', action='store_true', help='Has the password uppercase for old desktop version data', dest='hash_uppercase')

subparsers = parser.add_subparsers(help=f'sub-command help')
for cmd, handler in sub_commands.items():
    sub_parser = subparsers.add_parser(cmd, help=f'{cmd} help')
    handler.setup_cmd_args(sub_parser)

args = parser.parse_args()

if args.file:
    file_path = args.file

if args.password:
    hex_pass = hash_password(args.password, args.hash_uppercase)

# Process the database
db = open_db(file_path, hex_pass)
if not db:
    print(f'Failed to open database [{file_path}]')
    exit(1)

print(args)
handler = sub_commands.get(args.subparser_name, None)
if handler:
    handler.process(args, db)
else:
    # print help
    parser.print_help()
    exit(1)
