#!/usr/bin/env python3
import sh
import click
import glob
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sqlcipher_info = f"{script_dir}/.db_auth-v4.info"
config_file = f"{script_dir}/.config.json"

init_opt = '--init'
ro_opt ='--readonly'

auth = [init_opt, sqlcipher_info]

@click.group()
@click.option('--limit', default=10, help='Rows count')
@click.option('--offset', default=0, help='Start window index')
@click.option('--exc-simple', is_flag=True, help='Exclude addresses like "0x000..."')
@click.option('--show-timestamp', is_flag=True, help='Show raw timestamps instead of formated dates')
@click.option('--full-addr', is_flag=True, help='Show full addresses of the form"0x..."')
@click.option('--print-query', is_flag=True, help='Print query before execution')
@click.pass_context
def cli(ctx, limit, offset, exc_simple, show_timestamp, full_addr, print_query):
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand != 'setup':
        ctx.obj['LIMIT'] = limit
        ctx.obj['OFFSET'] = offset
        ctx.obj['EXCLUDE'] = exc_simple
        ctx.obj['TIMESTAMP'] = show_timestamp
        ctx.obj['FULL_ADDR'] = full_addr
        ctx.obj['PRINT_QUERY'] = print_query

        config = {}
        with open(config_file, "r") as f:
            config = json.load(f)
        if 'db' not in config:
            raise click.ClickException(f"Broken configuration. Check file {config_file}")
        ctx.obj['PARAMS'] = ["--table", ro_opt, config['db'], *auth]

def get_window(ctx):
    return f"LIMIT {ctx.obj['LIMIT']} OFFSET {ctx.obj['OFFSET']}"

def get_where(ctx, owner):
    if ctx.obj['EXCLUDE']:
        return f"WHERE HEX({owner}) NOT LIKE '000%'"
    return ""

def get_order_by(ctx):
    return "ORDER BY timestamp DESC"

def get_query(ctx, columns, table, owner="address"):
    return f"SELECT {columns} FROM {table} {get_where(ctx, owner)} {get_order_by(ctx)} {get_window(ctx)};"

def timestamp(column, ctx, as_=None):
    base = column if ctx.obj['TIMESTAMP'] else f"datetime({column}, 'unixepoch')"
    return f"{base} {f' AS {as_}' if as_ else ''}"

def addr(column, ctx, as_=None):
    base = f"'0x' || HEX({column})" if ctx.obj['FULL_ADDR'] else f"SUBSTR(HEX({column}), 1, 3) || '...' || SUBSTR(HEX({column}), -3, 3)"
    return f"{base}{f' AS {as_}' if as_ else ''}"

def exec_sql(ctx, query):
    params = ctx.obj['PARAMS']
    params.append(query)

    if ctx.obj['PRINT_QUERY']:
        print(f'SQL Query:\n"{query}"\n\n')
    print(sh.sqlcipher(*params))

@cli.command(help="List transfers table")
@click.pass_context
def list_trs(ctx):
    exec_sql(ctx, get_query(ctx, f"multi_transaction_id as MtID, {addr('tx_from_address', ctx, 'from_')}, {addr('tx_to_address', ctx, 'to_')}, {timestamp('timestamp', ctx, 'dt')}, {addr('tx_hash', ctx, 'hash')}, {addr('address', ctx, 'addr')}, {addr('hash', ctx, 'has_id')}", "transfers"))

@cli.command(help="List pending_transactions table")
@click.pass_context
def list_pending(ctx):
    exec_sql(ctx, get_query(ctx, f"multi_transaction_id AS MtID, {addr('from_address', ctx, 'from_')}, {addr('to_address', ctx, 'to_')}, {timestamp('timestamp', ctx, 'dt')}, {addr('hash', ctx, 'hash')}, type, status, auto_delete AS del, network_id AS chain", "pending_transactions"))

@cli.command(help="List multi_transactions table")
@click.pass_context
def list_mt(ctx):
    exec_sql(ctx, get_query(ctx, f"ROWID AS MtID, {addr('from_address', ctx, 'from_')}, {addr('to_address', ctx, 'to_')}, {timestamp('timestamp', ctx, 'dt')}, type", "multi_transactions", "from_address"))

@cli.command(help="Execute query")
@click.argument('query', nargs=1, type=click.UNPROCESSED)
@click.pass_context
def exec(ctx, query):
    exec_sql(ctx, query)

@cli.command(help="Generate config and authentication file")
@click.password_option()
@click.argument('db', nargs=1, type=click.Path(exists=True), required=False)
def setup(password, db):
    if db is None:
        print("Searching for DB file...")
        files = glob.glob(f"{script_dir}/../status-desktop/Status/data/*-wallet.db")
        if len(files) == 0:
            raise click.ClickException("No DB file found")
        else:
            db = files[0]
            print(f"Found {db}")

    import sys
    sys.path.append(f"{script_dir}/../status-desktop/scripts/common")
    import PasswordFunctions

    hashed_pass = PasswordFunctions.hash_password(password, old_desktop=False)
    info_content = f'''
    PRAGMA key = "{hashed_pass}";
    PRAGMA cipher_page_size = 8192;
    PRAGMA kdf_iter = 256000;
    PRAGMA cipher_hmac_algorithm = HMAC_SHA1;
    PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA1;
    PRAGMA foreign_keys = ON;
    '''

    with open(sqlcipher_info, 'w') as f:
        f.write(info_content)

    config = {"db": db}
    with open(config_file, "w") as f:
        json.dump(config, f)

if __name__ == '__main__':
    cli()

