from binance.websockets import BinanceSocketManager
from binance.client import Client
import json
from collections import deque
import pandas as pd
import argparse


parser = argparse.ArgumentParser(description='Parser for Live trading')

parser.add_argument('-e', '--exchange', help="Exchange name", required=True)
parser.add_argument('-p', '--pair', help="Pair name", required=True)
parser.add_argument('-i', '--interval',
                    help="Tick interval duration", required=True)
parser.add_argument('-s', '--strategy',
                    help="Strategy to be used", required=True)

args = parser.parse_args()

stack = deque()


def binance_message(msg, args):
    d = {
        'Time': msg['k']['t'],
        'Open': msg['k']['o'],
        'High': msg['k']['h'],
        'Low': msg['k']['l'],
        'Close': msg['k']['c'],
        'Volume': msg['k']['v'],
    }
    if not len(stack) or stack[-1]['Time'] != d['Time']:
        stack.append(d)
        df = pd.DataFrame(list(stack)[:-1])

        module = __import__(
            f'strategies.{args.s}', fromlist=['MyStrat'])
        Strat = getattr(module, 'MyStrat')

        with open(f'strategies/{args.s}.toml') as f:
            pass
    else:
        stack.pop()
        stack.append(d)


if args.e == 'Binance':
    if args.e == "1m":
        args.e = Client.KLINE_INTERVAL_1MINUTE
    elif args.e == "3m":
        args.e = Client.KLINE_INTERVAL_3MINUTE
    elif args.e == "5m":
        args.e = Client.KLINE_INTERVAL_5MINUTE
    elif args.e == "15m":
        args.e = Client.KLINE_INTERVAL_15MINUTE
    elif args.e == "30m":
        args.e = Client.KLINE_INTERVAL_30MINUTE
    elif args.e == "1h":
        args.e = Client.KLINE_INTERVAL_1HOUR
    elif args.e == "2h":
        args.e = Client.KLINE_INTERVAL_2HOUR
    elif args.e == "4h":
        args.e = Client.KLINE_INTERVAL_4HOUR
    elif args.e == "6h":
        args.e = Client.KLINE_INTERVAL_6HOUR
    elif args.e == "8h":
        args.e = Client.KLINE_INTERVAL_8HOUR
    else:
        raise Exception('Invalid Interval')

    client = Client('', '')

    bm = BinanceSocketManager(client)
    conn_key = bm.start_kline_socket(
        'BNBBTC', binance_message, interval=Client.KLINE_INTERVAL_1MINUTE)
    bm.start()
