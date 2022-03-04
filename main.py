import logging
from datetime import datetime
from os import makedirs
from os.path import exists, getmtime

import requests

logging.basicConfig(level=logging.INFO)


def get_last_modified(file: str) -> datetime:
    try:
        return datetime.fromtimestamp(getmtime(file))
    except OSError:
        return datetime.min


def check_updates() -> tuple[bool, bool]:
    if not exists('external'):
        logging.warning('Creating missing folder')
        makedirs('external')
    printings = get_last_modified('external/AllPrintings.sqlite')
    prices = get_last_modified('external/AllPrices.json')
    meta = requests.get('https://mtgjson.com/api/v5/Meta.json').json()
    printings_date = datetime.fromisoformat(meta['data']['date'])
    prices_date = datetime.fromisoformat(meta['meta']['date'])
    printings = printings < printings_date
    prices = prices < prices_date
    if printings or prices:
        logging.info('Update found!')
    else:
        logging.info('No updates found')
    return printings, prices


def update_printings():
    logging.info('Downloading printings...')
    response = requests.get('https://mtgjson.com/api/v5/AllPrintings.sqlite', stream=True)
    try:
        response.raise_for_status()
        with open('external/AllPrintings.sqlite', 'wb') as output:
            for chunk in response.iter_content(chunk_size=8192 * 8):
                output.write(chunk)
    except Exception as e:
        logging.error(f'Unable to download updated printings [{e.__repr__()}]')


def update_prices():
    logging.info('Downloading prices...')
    response = requests.get('https://mtgjson.com/api/v5/AllPrices.json', stream=True)
    try:
        response.raise_for_status()
        with open('external/AllPrices.json', 'wb') as output:
            for chunk in response.iter_content(chunk_size=8192 * 8):
                output.write(chunk)
    except Exception as e:
        logging.error(f'Unable to download updated printings [{e.__repr__()}]')
        return
    # TODO convert to sqlite
    # logger.info('Processing prices...')


def main():
    logging.info('Checking for updates...')
    printings, prices = check_updates()
    if printings:
        update_printings()
    if prices:
        update_prices()


if __name__ == '__main__':
    main()
