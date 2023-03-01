from dbhelpers import *
from helpers import *

from datetime import datetime as dt
from dataclasses import dataclass, field
import argparse

# Parse program arguments
parser = argparse.ArgumentParser(description='Balance history statistics')
parser.add_argument('--file', type=str, help='Path to the database file', required=True)
parser.add_argument('--pass', type=str, help='Password to the database file', required=True, dest='password')
parser.add_argument('--filter-count-less-than', type=int, default=0, help='Filter out addresses with less than this count')
parser.add_argument('--filter-block-len-less-than', type=float, default=0, help='Filter out addresses with average block length less than this value')
parser.add_argument('--filter-address', type=str, help='Filter out addresses with less than this block length')
parser.add_argument('--print-address', action='store_true', help='Print the address')
parser.add_argument('--hash-password-uppercase', action='store_true', help='Has the password uppercase for old desktop version data', dest='hash_uppercase')

args = parser.parse_args()

if args.file:
    file_path = args.file

if args.password:
    hex_pass = hash_password(args.password, args.hash_uppercase)

filter_count_less_than: int = args.filter_count_less_than
filter_block_len_less_than: float = args.filter_block_len_less_than

filter_address: str = ""
if args.filter_address:
    filter_address = args.filter_address

print_address: bool = args.print_address

# Globals

target_block_len_seconds = 12

# Process the database

db = open_db(file_path, hex_pass)

chains = [row[0] for row in db.execute('SELECT DISTINCT chain_id FROM balance_history')]
addresses = [row[0] for row in db.execute('SELECT DISTINCT address FROM balance_history')]
currencies = [row[0] for row in db.execute('SELECT DISTINCT currency FROM balance_history;')]

flags = [filter_all_time_flag, filter_weekly_flag, filter_twice_a_day_flag]

@dataclass
class Stats:
    count: int = field()
    first_date: dt = field()
    last_date: dt = field()
    first_block: int = field()
    last_block: int = field()

    def __str__(self):
        return f'{self.count:>5} BLen[{self.avg_block_len_sec():<5.3}s] BC[{self.last_block - self.first_block:>9}] {{{dt.strftime(self.first_date, "%d.%m.%Y")} - {dt.strftime(self.last_date, "%d.%m.%Y")}}} {{{self.first_block:>10} {self.last_block:>10}}}'

    def avg_block_len_sec(self) -> float:
        blocks = self.last_block - self.first_block
        return (self.last_date - self.first_date).total_seconds()/blocks if blocks else 0

data = dict()

cursor = db.execute(f'SELECT Count(*) FROM balance_history')
count_entries = cursor.fetchone()[0]
print(f'Total of [{count_entries}] balance entries in DB')

for chain in chains:
    for currency in currencies:
        for address in addresses:
            for flag in flags:
                identity_query_str = 'FROM balance_history WHERE chain_id = ? AND (bitset & ?) > 0 AND address = ? AND currency = ?'
                identity = (chain, flag, address, currency)
                cursor = db.execute(f'SELECT Count(*) {identity_query_str};', identity)
                count_entries = [row[0] for row in cursor if row[0] > 0]
                if len(count_entries) == 0:
                    continue
                if len(count_entries) > 1:
                    raise Exception('More than one count entry found')

                this_count = count_entries[0]
                if this_count < filter_count_less_than:
                    continue

                # Initialize missing values
                if chain not in data: data[chain] = dict()
                if currency not in data[chain]: data[chain][currency] = dict()
                if address not in data[chain][currency]: data[chain][currency][address] = dict()

                cursor = db.execute(f'SELECT timestamp {identity_query_str} ORDER BY timestamp ASC LIMIT 1;', identity)
                timestamp = [row[0] for row in cursor][0]
                first_date = dt.fromtimestamp(timestamp)
                cursor = db.execute(f'SELECT timestamp {identity_query_str} ORDER BY timestamp DESC LIMIT 1;', identity)
                timestamp = [row[0] for row in cursor][0]
                last_date = dt.fromtimestamp(timestamp)

                cursor = db.execute(f'SELECT block {identity_query_str} ORDER BY timestamp ASC LIMIT 1;', identity)
                first_block = [row[0] for row in cursor][0]
                cursor = db.execute(f'SELECT block {identity_query_str} ORDER BY timestamp DESC LIMIT 1;', identity)
                last_block = [row[0] for row in cursor][0]

                stats = Stats(this_count, first_date, last_date, first_block, last_block)
                data[chain][currency][address][flag] = stats

ident_str = ""
for chain, chain_data in data.items():
    print(f'- {chain_to_name(chain)}')
    for currency, currency_data in chain_data.items():
        print(f'  - {currency}')
        for address, address_data in currency_data.items():
            str_address: str = address_to_hex(address)
            if len(filter_address) > 0 and not str_address.lower().find(filter_address.lower()) > 0:
                continue
            if print_address:
                print(f'    - {str_address}')
            for flag, stats in address_data.items():
                if filter_block_len_less_than == 0 or stats.avg_block_len_sec() <= filter_block_len_less_than:
                    print(f'    {"  " if print_address else "" }- {stats} flag: {flag_to_str(flag)}')
