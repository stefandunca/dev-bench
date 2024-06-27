#!/usr/bin/env python3
import base64
import string
import sys
from io import BytesIO
import sh
import click
import glob
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
default_wallet_config_file = f"{script_dir}/.main-config.json"
default_app_config_file = f"{script_dir}/.main-app-config.json"
app_commands = ['accounts']

init_opt = '--init'
ro_opt = '--readonly'


@click.group()
@click.option('--limit', default=10, help='Rows count')
@click.option('--offset', default=0, help='Start window index')
@click.option('--exc-simple', is_flag=True, help='Exclude addresses like "0x000..."')
@click.option('--show-timestamp', is_flag=True, help='Show raw timestamps instead of formated dates')
@click.option('--full-addr', is_flag=True, help='Show full addresses of the form"0x..."')
@click.option('--no-elide', is_flag=True, help='Do not elide long columns')
@click.option('--print-query', is_flag=True, help='Print query before execution')
@click.option('--table/--no-table', is_flag=True, default=True, help='Table formatting')
@click.option('--json', "json_out", is_flag=True, default=False, help='JSON output')
@click.option('--md', "markdown_out", is_flag=True, default=False, help='JSON output')
@click.option('--write/--read-only', is_flag=True, default=False, help='Writable DB')
@click.option('--config', default=None, help='Config file')
@click.option('--explain', is_flag=True, help='Explain query')
@click.option('--explain-plan', is_flag=True, help='Explain query plan')
@click.option('--auth-info', default=f"{script_dir}/.db_auth-v4.info", help='SQLCipher setup file')
@click.pass_context
def cli(ctx, limit, offset, exc_simple, show_timestamp, full_addr, no_elide, print_query, table, write, json_out, markdown_out, config, explain, explain_plan, auth_info):
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand != 'setup':
        ctx.obj['LIMIT'] = limit
        ctx.obj['OFFSET'] = offset
        ctx.obj['EXCLUDE'] = exc_simple
        ctx.obj['TIMESTAMP'] = show_timestamp
        ctx.obj['FULL_ADDR'] = full_addr
        ctx.obj['NO_ELIDE'] = no_elide
        ctx.obj['PRINT_QUERY'] = print_query
        ctx.obj['EXPLAIN'] = explain
        ctx.obj['EXPLAIN_PLAN'] = explain_plan

        config_file = ""
        if config is None:
            if ctx.invoked_subcommand in app_commands:
                config = default_app_config_file
            else:
                config = default_wallet_config_file
        if config:
            config_file = os.path.normpath(os.path.join(script_dir, config))
        ctx.obj['CONFIG_FILE'] = config_file

        config_obj = {}
        with open(config_file, "r") as f:
            config_obj = json.load(f)
        if 'db' not in config_obj:
            raise click.ClickException(
                f"Broken configuration. Check file {config_file}")
        ctx.obj['CONFIG_OBJ'] = config_obj
        auth = [init_opt, auth_info]
        ctx.obj['PARAMS'] = ([ro_opt] if not write else []
                             ) + [config_obj['db'], *auth]
        ctx.obj['PRETTY'] = table
        ctx.obj['JSON_OUT'] = json_out
        ctx.obj['MARKDOWN_OUT'] = markdown_out


def get_window(ctx):
    return f"LIMIT {ctx.obj['LIMIT']} OFFSET {ctx.obj['OFFSET']}"


def get_where_trs(ctx, owner):
    if ctx.obj['EXCLUDE']:
        return f"WHERE HEX({owner}) NOT LIKE '000%'"
    return ""


def get_order_by(column):
    return f"ORDER BY {column} DESC" if column else ""


def get_select_trs(ctx, columns, table, owner="address", order_column="timestamp"):
    return f"SELECT {columns} FROM {table} {get_where_trs(ctx, owner)} {get_order_by(order_column)} {get_window(ctx)};"


def timestamp(column, ctx, as_=None):
    base = column if ctx.obj['TIMESTAMP'] else f"datetime({column}, 'unixepoch')"
    return f"{base} {f' AS {as_}' if as_ else ''}"


def column(column, as_=None):
    return f"{column} {f' AS {as_}' if as_ else ''}"


def elide_column(column, ctx, as_=None, might_be_null=True, length=3):
    base = ""
    if ctx.obj['NO_ELIDE']:
        base = column
    else:
        base = f"SUBSTR({column}, 1, {length}) || '...' || SUBSTR({column}, -{length}, {length})"
    if might_be_null:
        base = f"CASE WHEN {column} IS NULL THEN 'NULL' ELSE {base} END"
    return f"{base}{f' AS {as_ if as_ else column}'}"


def addr(column, ctx, as_=None, might_be_null=False):
    base = f"'0x' || HEX({column})" if ctx.obj['FULL_ADDR'] else f"SUBSTR(HEX({column}), 1, 3) || '...' || SUBSTR(HEX({column}), -3, 3)"
    if might_be_null:
        base = f"CASE WHEN {column} IS NULL THEN 'NULL' ELSE {base} END"
    return f"{base}{f' AS {as_}' if as_ else ''}"


def exec_sql(ctx, query, pretty_overwrite=None):
    params = ctx.obj['PARAMS']

    if (ctx.obj['JSON_OUT']):
        params.append('--ascii')
    elif (ctx.obj['MARKDOWN_OUT']):
        params.append('--markdown')
    elif pretty_overwrite is None:
        if (ctx.obj['PRETTY']):
            params.append('--table')

    if ctx.obj['EXPLAIN_PLAN']:
        query = f"explain query plan {query}"
    elif ctx.obj['EXPLAIN']:
        query = f"explain {query}"

    params.append(query)

    if ctx.obj['PRINT_QUERY']:
        print(f'SQL Query:\n"{query}"\n-----------------\n')

    run_extra = {'_out': click.get_text_stream(
        'stdout'), '_err': click.get_text_stream('stderr')}
    sh.sqlcipher(*params, **run_extra)


@cli.command(help="List wallet connect sessions")
@click.option('-a', '--all', is_flag=True, default=False, help='Show all columns')
@click.option('-i', '--info-only', is_flag=True, default=False, help='Show only app info')
@click.option('-d', '--dapps-only', is_flag=True, default=False, help='Show only dapps list')
@click.pass_context
def wc(ctx, all, info_only, dapps_only):
    main_columns = []

    if dapps_only:
        columns = [column("dapps.name", "name"), column("dapps.url", "url"), elide_column(
            "dapps.icon_url", ctx, "icon"), column("(count(sessions.topic) - sum(sessions.disconnected))", "active_ses"), column("count(sessions.topic)", "ses")]
    else:
        if not info_only:
            main_columns = ["dapps.name AS name", timestamp(
                'sessions.expiry', ctx, 'dt'), "sessions.disconnected AS disc", elide_column("sessions.pairing_topic", ctx, "pairing")]
        extra_columns = []
        if all or info_only:
            extra_columns = [column("sessions.session_json", "json"), column(
                "dapp_url", "url"), column("dapps.icon_url", "icon"), "test_chains AS test"]
        columns = [elide_column("sessions.topic", ctx, "topic")
                   ] + main_columns + extra_columns

    query_str = f"""SELECT {", ".join(columns)} FROM wallet_connect_dapps AS dapps
                    {"JOIN" if dapps_only else "LEFT JOIN"} wallet_connect_sessions
                        AS sessions ON dapps.url = sessions.dapp_url
                        {"GROUP BY dapps.url" if dapps_only else ""}
                    {get_order_by("expiry")}
                    {get_window(ctx)};
                """

    exec_sql(ctx, query_str)


@cli.command(help="List transfers table")
@click.option('-e', '--extended', is_flag=True, default=False, help='Show more columns')
@click.pass_context
def list_trs(ctx, extended):
    columns = ["multi_transaction_id as MtID",
              f"{addr('tx_from_address', ctx, 'from_')}",
              f"{addr('tx_to_address', ctx, 'to_')}",
              f"{timestamp('timestamp', ctx, 'dt')}",
              f"{addr('tx_hash', ctx, 'hash')}",
              f"{addr('address', ctx, 'addr')}",
              f"{addr('hash', ctx, 'has_id')}"]
    if extended:
        columns += ["tx_type"]
    columns_str = ", ".join(columns)
    exec_sql(ctx, get_select_trs(ctx, columns_str, "transfers"))


@cli.command(help="List pending_transactions table")
@click.pass_context
def list_pending(ctx):
    exec_sql(ctx, get_select_trs(
        ctx, f"multi_transaction_id AS MtID, {addr('from_address', ctx, 'from_')}, {addr('to_address', ctx, 'to_')}, {timestamp('timestamp', ctx, 'dt')}, {addr('hash', ctx, 'hash')}, type, status, auto_delete AS del, network_id AS chain", "pending_transactions"))


@cli.command(help="List multi_transactions table")
@click.pass_context
def list_mt(ctx):
    exec_sql(ctx, get_select_trs(
        ctx, f"ROWID AS MtID, {addr('from_address', ctx, 'from_')}, {addr('to_address', ctx, 'to_')}, {timestamp('timestamp', ctx, 'dt')}, type", "multi_transactions", "from_address"))


@cli.command(help="List wallet accounts")
@click.pass_context
def accounts(ctx):
    exec_sql(
        ctx, f"SELECT acc.name, {addr('address', ctx, 'addr')}, keypairs.name as kp_name FROM keypairs_accounts as acc LEFT JOIN keypairs ON keypairs.key_uid=acc.key_uid WHERE operable='fully' AND acc.removed=0 AND chat=0 ORDER BY position ASC;")


@cli.command(help="Join transfers and multi_transactions tables")
@click.option('--join-mt', is_flag=True, default=False, help='LEFT JOIN with multi_transactions table (show only MT entries)')
@click.pass_context
def list_transfers(ctx, join_mt):
    join_clause = ""
    if join_mt:
        join_clause = """
            LEFT JOIN
                multi_transactions ON multi_transactions.ROWID = transfers.multi_transaction_id
            GROUP BY
                transfers.multi_transaction_id
            ORDER BY
                MIN(transfers.timestamp) DESC
        """
    else:
        join_clause = "ORDER BY transfers.timestamp DESC"

    exec_sql(ctx, f"""
        SELECT
            CASE WHEN transfers.multi_transaction_id = 0 THEN 'None' ELSE transfers.multi_transaction_id END as MTID,
            {addr('multi_transactions.from_address', ctx, 'from_', True) if join_mt else addr('transfers.tx_from_address', ctx, 'from_', True)},
            {addr('multi_transactions.to_address', ctx, 'to_', True) if join_mt else addr('transfers.tx_to_address', ctx, 'to_', True)},
            {timestamp('multi_transactions.timestamp', ctx, 'dt') if join_mt else timestamp('transfers.timestamp', ctx, 'dt')},
            {addr('transfers.tx_hash', ctx, 'tx_hash', True)},
            {addr('multi_transactions.from_asset', ctx, 'fromTk', True) if join_mt else 'transfers.type as type'},
            {(addr('multi_transactions.to_asset', ctx, 'toTk', True) + ",") if join_mt else ""}
            {'COUNT(transfers.multi_transaction_id) AS trs,' if join_mt else ''}
            {addr('transfers.address', ctx, 'owner')},
            network_id AS chain
        FROM
            transfers
        {join_clause}
        {get_window(ctx)};""")


@cli.command(help="Execute query")
@click.argument('query', nargs=1, type=click.UNPROCESSED)
@click.pass_context
def exec(ctx, query):
    exec_sql(ctx, query)


@cli.command(help="Count rows")
@click.argument('table-name', nargs=1, type=click.UNPROCESSED)
@click.option('--distinct-column', default=None, help='Count distinct values of column')
@click.pass_context
def count(ctx, table_name, distinct_column):
    distinct = f"COUNT(DISTINCT({distinct_column}))" if distinct_column else None
    exec_sql(
        ctx, f"SELECT {'COUNT(*)' if distinct is None else distinct} FROM {table_name};", pretty_overwrite=False)


@cli.command(help="Show columns")
@click.argument('table-name', nargs=1, type=click.UNPROCESSED)
@click.option('--create-table', is_flag=True, help='Focus on columns')
@click.pass_context
def table_info(ctx, table_name, create_table):
    if create_table:
        exec_sql(
            ctx, f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    else:
        exec_sql(ctx, f"PRAGMA table_info({table_name});")


@cli.command(help="List indexes")
@click.argument('table-name', nargs=1, type=click.UNPROCESSED)
@click.pass_context
def indexes(ctx, table_name):
    exec_sql(ctx, f"PRAGMA index_list({table_name});")


@cli.command(help="Index info")
@click.argument('index-name', nargs=1, type=click.UNPROCESSED)
@click.pass_context
def index(ctx, index_name):
    exec_sql(ctx, f"PRAGMA index_info({index_name});")


@cli.command(help="Generate config and authentication file")
@click.password_option()
@click.argument('db', nargs=1, type=click.Path(exists=True), required=False)
@click.pass_context
def setup(ctx, password, db):
    if db is None:
        print("Searching for DB file...")
        files = glob.glob(
            f"{script_dir}/../status-desktop/Status/data/*-wallet.db")
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
    out_config_file = ctx.obj['CONFIG_FILE']
    with open(out_config_file, "w") as f:
        json.dump(config, f)

# TODO:
# - Check the total size of some columns: `SELECT type, SUM(LENGTH(tx)), SUM(LENGTH(receipt)), SUM(LENGTH(log)) FROM transfers`
# - Check the biggest entries: `SELECT type, LENGTH(tx), LENGTH(receipt), LENGTH(log) FROM transfers WHERE tx NOT NULL AND type='erc20' ORDER BY LENGTH(receipt) DESC LIMIT 10;`


if __name__ == '__main__':
    cli()
