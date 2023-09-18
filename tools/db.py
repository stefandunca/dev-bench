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
@click.option('--table/--no-table', is_flag=True, default=True, help='Table formatting')
@click.pass_context
def cli(ctx, limit, offset, exc_simple, show_timestamp, full_addr, print_query, table):
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
        ctx.obj['PARAMS'] = [ro_opt, config['db'], *auth]
        ctx.obj['PRETTY'] = table

def get_window(ctx):
    return f"LIMIT {ctx.obj['LIMIT']} OFFSET {ctx.obj['OFFSET']}"

def get_where(ctx, owner):
    if ctx.obj['EXCLUDE']:
        return f"WHERE HEX({owner}) NOT LIKE '000%'"
    return ""

def get_order_by(ctx):
    return "ORDER BY timestamp DESC"

def get_select(ctx, columns, table, owner="address"):
    return f"SELECT {columns} FROM {table} {get_where(ctx, owner)} {get_order_by(ctx)} {get_window(ctx)};"

def timestamp(column, ctx, as_=None):
    base = column if ctx.obj['TIMESTAMP'] else f"datetime({column}, 'unixepoch')"
    return f"{base} {f' AS {as_}' if as_ else ''}"

def addr(column, ctx, as_=None, might_be_null=False):
    base = f"'0x' || HEX({column})" if ctx.obj['FULL_ADDR'] else f"SUBSTR(HEX({column}), 1, 3) || '...' || SUBSTR(HEX({column}), -3, 3)"
    if might_be_null:
        base = f"CASE WHEN {column} IS NULL THEN 'NULL' ELSE {base} END"
    return f"{base}{f' AS {as_}' if as_ else ''}"


from io import BytesIO
import sys
import string
import base64

def exec_sql(ctx, query, pretty_overwrite=None):
    params = ctx.obj['PARAMS']

    if (ctx.obj['PRETTY'] if pretty_overwrite is None else pretty_overwrite):
        params.append('--table')

    params.append(query)


    if ctx.obj['PRINT_QUERY']:
        print(f'SQL Query:\n"{query}"\n\n')

    run_extra = {'_out': click.get_text_stream('stdout'), '_err': click.get_text_stream('stderr')}
    sh.sqlcipher(*params, **run_extra)

@cli.command(help="List transfers table")
@click.pass_context
def list_trs(ctx):
    exec_sql(ctx, get_select(ctx, f"multi_transaction_id as MtID, {addr('tx_from_address', ctx, 'from_')}, {addr('tx_to_address', ctx, 'to_')}, {timestamp('timestamp', ctx, 'dt')}, {addr('tx_hash', ctx, 'hash')}, {addr('address', ctx, 'addr')}, {addr('hash', ctx, 'has_id')}", "transfers"))

@cli.command(help="List pending_transactions table")
@click.pass_context
def list_pending(ctx):
    exec_sql(ctx, get_select(ctx, f"multi_transaction_id AS MtID, {addr('from_address', ctx, 'from_')}, {addr('to_address', ctx, 'to_')}, {timestamp('timestamp', ctx, 'dt')}, {addr('hash', ctx, 'hash')}, type, status, auto_delete AS del, network_id AS chain", "pending_transactions"))

@cli.command(help="List multi_transactions table")
@click.pass_context
def list_mt(ctx):
    exec_sql(ctx, get_select(ctx, f"ROWID AS MtID, {addr('from_address', ctx, 'from_')}, {addr('to_address', ctx, 'to_')}, {timestamp('timestamp', ctx, 'dt')}, type", "multi_transactions", "from_address"))

@cli.command(help="Join transfers and multi_transactions tables")
@click.pass_context
def list_transfers(ctx):
    exec_sql(ctx, f"""
        SELECT
            {addr('multi_transactions.from_asset', ctx, 'fromTk', True)},
            {addr('multi_transactions.to_asset', ctx, 'toTk', True)},
            {addr('multi_transactions.from_address', ctx, 'from_', True)},
            {addr('multi_transactions.to_address', ctx, 'to_', True)},
            CASE WHEN transfers.multi_transaction_id = 0 THEN 'None' ELSE transfers.multi_transaction_id END as MTID,
            {timestamp('multi_transactions.timestamp', ctx, 'dt')},
            COUNT(transfers.multi_transaction_id) AS trs,
            SUBSTR(HEX(tx_hash), 0, 7) AS tx_hash,
            {addr('transfers.tx_hash', ctx, 'tx_hash', True)}
        FROM
            transfers
        LEFT JOIN
            multi_transactions ON multi_transactions.ROWID = transfers.multi_transaction_id
        GROUP BY
            transfers.multi_transaction_id
        ORDER BY
            MIN(transfers.timestamp) DESC
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
    exec_sql(ctx, f"SELECT {'COUNT(*)' if distinct is None else distinct} FROM {table_name};", pretty_overwrite=False)

@cli.command(help="Show columns")
@click.argument('table-name', nargs=1, type=click.UNPROCESSED)
@click.option('--create-table', is_flag=True, help='Focus on columns')
@click.pass_context
def table_info(ctx, table_name, create_table):
    if create_table:
        exec_sql(ctx, f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
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

# TODO:
# - Check the total length of some columns: `SELECT type, SUM(LENGTH(tx)), SUM(LENGTH(receipt)), SUM(LENGTH(log)) FROM transfers`
# - Check the biggest entries: `SELECT type, LENGTH(tx), LENGTH(receipt), LENGTH(log) FROM transfers WHERE tx NOT NULL AND type='erc20' ORDER BY LENGTH(receipt) DESC LIMIT 10;`

# TODO: move to filter.py
@cli.command(help="Testing")
@click.pass_context
def dev(ctx):
    exec_sql(ctx, f"""
        WITH filter_conditions AS (
        SELECT
            1 AS startFilterDisabled,
            0 AS startTimestamp,
            1 AS endFilterDisabled,
            0 AS endTimestamp,
            1 AS filterActivityTypeAll,
            0 AS filterActivityTypeSend,
            0 AS filterActivityTypeReceive,
            0 AS filterActivityTypeContractDeployment,
            0 AS filterActivityTypeMint,
            0 AS mTTypeSend,
            1 AS fromTrType,
            2 AS toTrType,
            1 AS filterAllAddresses,
            1 AS filterAllToAddresses,
            1 AS filterAllActivityStatus,
            0 AS filterStatusCompleted,
            0 AS filterStatusFailed,
            0 AS filterStatusFinalized,
            0 AS filterStatusPending,
            0 AS statusFailed,
            2 AS statusSuccess,
            1 AS statusPending,
            1 AS includeAllTokenTypeAssets,
            1 AS includeAllNetworks,
            'Pending' AS pendingStatus,
            '0000000000000000000000000000000000000000' AS zeroAddress
        ),
        filter_addresses(address) AS (
            SELECT
                *
            FROM
                (
                    VALUES
                        ('E2D622C817878DA5143BBE06866CA8E35273BA8A'),('9B1045F94B21CF7D8BE9911DA8F8B5E9E1C543A3'),('BD54A96C0AE19A220C8E1234F54C940DFAB34639'),('5D7905390B77A937AE8C444AA8BF7FA9A6A7DBA0'),('0000000000000000000000000000000000000001')
                )
        ),
        filter_to_addresses(address) AS (
            VALUES
                (NULL)
        ),
        assets_token_codes(token_code) AS (
            VALUES
                (NULL)
        ),
        assets_erc20(chain_id, token_address) AS (
            VALUES
                (NULL, NULL)
        ),
        filter_networks(network_id) AS (
            VALUES
                (NULL)
        ),
        tr_status AS (
            SELECT
                multi_transaction_id,
                MIN(status) AS min_status,
                COUNT(*) AS count,
                network_id
            FROM
                transfers
            WHERE
                transfers.loaded == 1
                AND transfers.multi_transaction_id != 0
            GROUP BY
                transfers.multi_transaction_id
        ),
        tr_network_ids AS (
            SELECT
                multi_transaction_id
            FROM
                transfers
            WHERE
                transfers.loaded == 1
                AND transfers.multi_transaction_id != 0
                AND network_id IN filter_networks
            GROUP BY
                transfers.multi_transaction_id
        ),
        pending_status AS (
            SELECT
                multi_transaction_id,
                COUNT(*) AS count,
                network_id
            FROM
                pending_transactions,
                filter_conditions
            WHERE
                pending_transactions.multi_transaction_id != 0
                AND pending_transactions.status = pendingStatus
            GROUP BY
                pending_transactions.multi_transaction_id
        ),
        pending_network_ids AS (
            SELECT
                multi_transaction_id
            FROM
                pending_transactions,
                filter_conditions
            WHERE
                pending_transactions.multi_transaction_id != 0
                AND pending_transactions.status = pendingStatus
                AND pending_transactions.network_id IN filter_networks
            GROUP BY
                pending_transactions.multi_transaction_id
        )
        SELECT
            {addr('transfers.hash', ctx, 'transfer_hash', True)},
            NULL AS pending_hash,
            transfers.network_id AS network_id,
            0 AS multi_tx_id,
            {timestamp('transfers.timestamp', ctx, 'timestamp')},
            NULL AS mt_type,
            CASE
                WHEN from_join.address IS NOT NULL
                AND to_join.address IS NULL THEN fromTrType
                WHEN to_join.address IS NOT NULL
                AND from_join.address IS NULL THEN toTrType
                WHEN from_join.address IS NOT NULL
                AND to_join.address IS NOT NULL THEN CASE
                    WHEN transfers.address = transfers.tx_from_address THEN fromTrType
                    ELSE toTrType
                END
                ELSE NULL
            END as tr_type,
            {addr('transfers.tx_from_address', ctx, 'from_address', True)},
            {addr('transfers.tx_to_address', ctx, 'to_address', True)},
            {addr('transfers.address', ctx, 'owner_address', True)},
            transfers.amount_padded128hex AS tr_amount,
            NULL AS mt_from_amount,
            NULL AS mt_to_amount,
            CASE
                WHEN transfers.status IS 1 THEN statusSuccess
                ELSE statusFailed
            END AS agg_status,
            1 AS agg_count,
            {addr('transfers.token_address', ctx, 'token_address', True)},
            {addr('transfers.token_id', ctx, 'token_id', True)},
            NULL AS token_code,
            NULL AS from_token_code,
            NULL AS to_token_code,
            NULL AS out_network_id,
            NULL AS in_network_id,
            transfers.type AS type,
            {addr('transfers.contract_address', ctx, 'contract_address', True)}
        FROM
            transfers,
            filter_conditions
            LEFT JOIN filter_addresses from_join ON HEX(transfers.address) = from_join.address
            LEFT JOIN filter_addresses to_join ON HEX(transfers.tx_to_address) = to_join.address
        WHERE
            transfers.loaded == 1
            AND transfers.multi_transaction_id = 0
            AND (
                (
                    startFilterDisabled
                    OR transfers.timestamp >= startTimestamp
                )
                AND (
                    endFilterDisabled
                    OR transfers.timestamp <= endTimestamp
                )
            )
            AND (
                -- Check description at the top of the file why code below is duplicated
                filterActivityTypeAll
                OR (
                    filterActivityTypeSend
                    AND tr_type = fromTrType
                    AND NOT (
                        tr_type = fromTrType
                        and transfers.tx_to_address IS NULL
                        AND transfers.type = 'eth'
                        AND transfers.contract_address IS NOT NULL
                        AND HEX(transfers.contract_address) != zeroAddress
                    )
                )
                OR (
                    filterActivityTypeReceive
                    AND tr_type = toTrType
                    AND NOT (
                        tr_type = toTrType
                        AND transfers.type = 'erc721'
                        AND (
                            transfers.tx_from_address IS NULL
                            OR HEX(transfers.tx_from_address) = zeroAddress
                        )
                    )
                )
                OR (
                    filterActivityTypeContractDeployment
                    AND tr_type = fromTrType
                    AND transfers.tx_to_address IS NULL
                    AND transfers.type = 'eth'
                    AND transfers.contract_address IS NOT NULL
                    AND HEX(transfers.contract_address) != zeroAddress
                    AND (
                        filterAllAddresses
                        OR (HEX(transfers.address) IN filter_addresses)
                    )
                )
                OR (
                    filterActivityTypeMint
                    AND tr_type = toTrType
                    AND transfers.type = 'erc721'
                    AND (
                        transfers.tx_from_address IS NULL
                        OR HEX(transfers.tx_from_address) = zeroAddress
                    )
                    AND (
                        filterAllAddresses
                        OR (HEX(transfers.address) IN filter_addresses)
                    )
                )
            )
            AND (
                filterAllAddresses
                OR (HEX(owner_address) IN filter_addresses)
            )
            AND (
                filterAllToAddresses
                OR (
                    HEX(transfers.tx_to_address) IN filter_to_addresses
                )
            )
            AND (
                includeAllTokenTypeAssets
                OR (
                    transfers.type = 'eth'
                    AND ('ETH' IN assets_token_codes)
                )
                OR (
                    transfers.type = 'erc20'
                    AND (
                        (
                            transfers.network_id,
                            HEX(transfers.token_address)
                        ) IN assets_erc20
                    )
                )
            )
            AND (
                includeAllNetworks
                OR (transfers.network_id IN filter_networks)
            )
            AND (
                filterAllActivityStatus
                OR (
                    (
                        filterStatusCompleted
                        OR filterStatusFinalized
                    )
                    AND transfers.status = 1
                )
                OR (
                    filterStatusFailed
                    AND transfers.status = 0
                )
            )
        UNION
        ALL
        SELECT
            NULL AS transfer_hash,
            {addr('pending_transactions.hash', ctx, 'pending_hash', True)},
            pending_transactions.network_id AS network_id,
            0 AS multi_tx_id,
            {timestamp('pending_transactions.timestamp', ctx, 'timestamp')},
            NULL AS mt_type,
            CASE
                WHEN from_join.address IS NOT NULL
                AND to_join.address IS NULL THEN fromTrType
                WHEN to_join.address IS NOT NULL
                AND from_join.address IS NULL THEN toTrType
                WHEN from_join.address IS NOT NULL
                AND to_join.address IS NOT NULL THEN CASE
                    WHEN from_join.address < to_join.address THEN fromTrType
                    ELSE toTrType
                END
                ELSE NULL
            END as tr_type,
            {addr('pending_transactions.from_address', ctx, 'from_address', True)},
            {addr('pending_transactions.to_address', ctx, 'to_address', True)},
            NULL AS owner_address,
            {addr('pending_transactions.value', ctx, 'tr_amount', True)},
            NULL AS mt_from_amount,
            NULL AS mt_to_amount,
            statusPending AS agg_status,
            1 AS agg_count,
            NULL AS token_address,
            NULL AS token_id,
            pending_transactions.symbol AS token_code,
            NULL AS from_token_code,
            NULL AS to_token_code,
            NULL AS out_network_id,
            NULL AS in_network_id,
            pending_transactions.type AS type,
            NULL as contract_address
        FROM
            pending_transactions,
            filter_conditions
            LEFT JOIN filter_addresses from_join ON HEX(pending_transactions.from_address) = from_join.address
            LEFT JOIN filter_addresses to_join ON HEX(pending_transactions.to_address) = to_join.address
        WHERE
            pending_transactions.multi_transaction_id = 0
            AND pending_transactions.status = pendingStatus
            AND (
                filterAllActivityStatus
                OR filterStatusPending
            )
            AND (
                (
                    startFilterDisabled
                    OR timestamp >= startTimestamp
                )
                AND (
                    endFilterDisabled
                    OR timestamp <= endTimestamp
                )
            )
            AND (
                filterActivityTypeAll
                OR filterActivityTypeSend
            )
            AND (
                filterAllAddresses
                OR (
                    HEX(pending_transactions.from_address) IN filter_addresses
                )
                OR (
                    HEX(pending_transactions.to_address) IN filter_addresses
                )
            )
            AND (
                filterAllToAddresses
                OR (
                    HEX(pending_transactions.to_address) IN filter_to_addresses
                )
            )
            AND (
                includeAllTokenTypeAssets
                OR (
                    UPPER(pending_transactions.symbol) IN assets_token_codes
                )
            )
            AND (
                includeAllNetworks
                OR (
                    pending_transactions.network_id IN filter_networks
                )
            )
        UNION
        ALL
        SELECT
            NULL AS transfer_hash,
            NULL AS pending_hash,
            NULL AS network_id,
            multi_transactions.ROWID AS multi_tx_id,
            {timestamp('multi_transactions.timestamp', ctx, 'timestamp')},
            multi_transactions.type AS mt_type,
            NULL as tr_type,
            {addr('multi_transactions.from_address', ctx, 'from_address', True)},
            {addr('multi_transactions.to_address', ctx, 'to_address', True)},
            {addr('multi_transactions.from_address', ctx, 'owner_address', True)},
            NULL AS tr_amount,
            {addr('multi_transactions.from_amount', ctx, 'mt_from_amount', True)},
            {addr('multi_transactions.to_amount', ctx, 'mt_to_amount', True)},
            CASE
                WHEN tr_status.min_status = 1
                AND COALESCE(pending_status.count, 0) = 0 THEN statusSuccess
                WHEN tr_status.min_status = 0 THEN statusFailed
                ELSE statusPending
            END AS agg_status,
            COALESCE(tr_status.count, 0) + COALESCE(pending_status.count, 0) AS agg_count,
            NULL AS token_address,
            NULL AS token_id,
            NULL AS token_code,
            multi_transactions.from_asset AS from_token_code,
            multi_transactions.to_asset AS to_token_code,
            multi_transactions.from_network_id AS out_network_id,
            multi_transactions.to_network_id AS in_network_id,
            NULL AS type,
            NULL as contract_address
        FROM
            multi_transactions,
            filter_conditions
            LEFT JOIN tr_status ON multi_transactions.ROWID = tr_status.multi_transaction_id
            LEFT JOIN pending_status ON multi_transactions.ROWID = pending_status.multi_transaction_id
        WHERE
            (
                (
                    startFilterDisabled
                    OR multi_transactions.timestamp >= startTimestamp
                )
                AND (
                    endFilterDisabled
                    OR multi_transactions.timestamp <= endTimestamp
                )
            )
            AND (
                filterActivityTypeAll
                OR (multi_transactions.type IN ())
            )
            AND (
                filterAllAddresses
                OR (
                    -- Send multi-transaction types are exclusively for outbound transfers. The receiving end will have a corresponding entry as "owner_address" in the transfers table.
                    mt_type = mTTypeSend
                    AND HEX(owner_address) IN filter_addresses
                )
                OR (
                    mt_type != mTTypeSend
                    AND (
                        HEX(multi_transactions.from_address) IN filter_addresses
                        OR HEX(multi_transactions.to_address) IN filter_addresses
                    )
                )
            )
            AND (
                filterAllToAddresses
                OR (
                    HEX(multi_transactions.to_address) IN filter_to_addresses
                )
            )
            AND (
                includeAllTokenTypeAssets
                OR (
                    multi_transactions.from_asset != ''
                    AND (
                        UPPER(multi_transactions.from_asset) IN assets_token_codes
                    )
                )
                OR (
                    multi_transactions.to_asset != ''
                    AND (
                        UPPER(multi_transactions.to_asset) IN assets_token_codes
                    )
                )
            )
            AND (
                filterAllActivityStatus
                OR (
                    (
                        filterStatusCompleted
                        OR filterStatusFinalized
                    )
                    AND agg_status = statusSuccess
                )
                OR (
                    filterStatusFailed
                    AND agg_status = statusFailed
                )
                OR (
                    filterStatusPending
                    AND agg_status = statusPending
                )
            )
            AND (
                includeAllNetworks
                OR (
                    multi_transactions.from_network_id IN filter_networks
                )
                OR (
                    multi_transactions.to_network_id IN filter_networks
                )
                OR (
                    COALESCE(multi_transactions.from_network_id, 0) = 0
                    AND COALESCE(multi_transactions.to_network_id, 0) = 0
                    AND (
                        EXISTS (
                            SELECT
                                1
                            FROM
                                tr_network_ids
                            WHERE
                                multi_transactions.ROWID = tr_network_ids.multi_transaction_id
                        )
                        OR EXISTS (
                            SELECT
                                1
                            FROM
                                pending_network_ids
                            WHERE
                                multi_transactions.ROWID = pending_network_ids.multi_transaction_id
                        )
                    )
                )
            )
        ORDER BY
            timestamp DESC
        {get_window(ctx)};""")

if __name__ == '__main__':
    cli()
