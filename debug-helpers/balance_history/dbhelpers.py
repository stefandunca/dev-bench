import sqlcipher3

import sha3

def open_db(file_path, password):
    db = sqlcipher3.connect(file_path)

    db.execute(f'PRAGMA key = "{password}"')
    db.execute('PRAGMA cipher_page_size = 1024')
    db.execute('PRAGMA kdf_iter = 256000')
    db.execute('PRAGMA cipher_hmac_algorithm = HMAC_SHA1')
    db.execute('PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA1')

    return db

def hash_password(password, old_desktop=True):
    hasher = sha3.keccak_256()
    hasher.update(password.encode())
    hash = hasher.hexdigest().upper() if old_desktop else hasher.hexdigest().lower()
    return '0x' + hash
