import binascii

filter_all_time_flag = 1
filter_weekly_flag = 1 << 3
filter_twice_a_day_flag = 1 << 5

chain_numbers = {
    1: 'Ethereum',
    2: 'Morden',
    3: 'Ropsten',
    4: 'Rinkeby',
    5: 'Goerli',
    10: 'Optimism',
    420: 'Optimism Goerli',
    42161: 'Arbitrum',
    421611: 'Arbitrum Rinkeby',
    421613: 'Arbitrum Goerli',
}

def flag_to_str(flag):
    if flag == filter_all_time_flag:
        return 'All-Time'
    elif flag == filter_weekly_flag:
        return 'Weekly'
    elif flag == filter_twice_a_day_flag:
        return 'Bi-Daily'
    else:
        raise Exception(f'Unknown flag {flag}')

def address_to_hex(address):
    return '0x' + binascii.b2a_hex(address).decode('utf-8').upper()

def chain_to_name(chain):
    return chain_numbers[chain] if chain in chain_numbers else f'Chain {chain}'