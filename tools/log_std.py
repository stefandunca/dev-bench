import sys
import logging
import time
from logging.handlers import RotatingFileHandler
import select
import argparse

# usage pattern `command 2>&1 >/dev/null | python3 log_std.py test.log --max_size_mb 1`
#
def create_rotating_log(path: str, max_bytes: int, backup_count: int):
    """
    Creates a rotating log
    """
    logger = logging.getLogger("Log stdin")
    logger.setLevel(logging.DEBUG)

    handler = RotatingFileHandler(path, maxBytes=max_bytes,
                                  backupCount=backup_count)
    handler.terminator = ""
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Log-rotate standard input and errors to a file')
    parser.add_argument('file', default='log.out', type=str, help='Path to the output file')
    parser.add_argument('--backup_count', default=5, type=int, help='Number of backups to keep')
    parser.add_argument('--max_size_mb', default=10, type=float, help='Maximum size of the log file in MB')
    args = parser.parse_args()

    # process argument path
    file_path = args.file
    backup_count = args.backup_count
    max_bytes = args.max_size_mb * 1024 * 1024

    logger =create_rotating_log(file_path, max_bytes, backup_count)

    # TODO: helper function to decorate separation lines
    logger.info(f'\n\n-----------------------------------------------------------------------\nStart logging; Max file size {args.max_size_mb}; Backup count: {backup_count}; Time {time.strftime("%H:%M:%S %d-%m-%Y")}\n-----------------------------------------------------------------------\n\n')

    # loop forever
    line = ""
    while True:
        try:
            line = ""
            if select.select([sys.stdin, ], [], [], 0.01)[0]:
                line = sys.stdin.readline()
            if select.select([sys.stderr, ], [], [], 0.01)[0]:
                line = sys.stderr.readline()
            if len(line) > 0:
                logger.info(line)
        except KeyboardInterrupt:
            logger.info("\n\n-----------------------------------------------------------------------\nStopped logging. Keyboard interrupt.\n-----------------------------------------------------------------------\n\n")
            break
        except Exception as e:
            logger.info(f'\n\n-----------------------------------------------------------------------\nStopped logging. Exception: "{e}"; line: "{line}"\n-----------------------------------------------------------------------\n\n')
            break