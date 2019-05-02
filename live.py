from binance.websockets import BinanceSocketManager
from binance.client import Client
import json
from collections import deque
import pandas as pd
import argparse
from pprint import pprint
# import toml


parser = argparse.ArgumentParser(description='Parser for Live trading')

parser.add_argument('-e', '--exchange', help="Exchange name", required=True)
parser.add_argument('-p', '--pair', help="Pair name", required=True)
parser.add_argument('-i', '--interval',
                    help="Tick interval duration", required=True)
parser.add_argument('-s', '--strategy',
                    help="Strategy to be used", required=True)

args = parser.parse_args()
stack = deque()

trades = deque()


def binance_message(msg, args, config):
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
            f'strategies.{args.strategy}', fromlist=['MyStrat'])
        Strat = getattr(module, 'MyStrat')
        try:
            strat = Strat(df, user_config=config)
            tup = strat.backtest(prempt=True)
            print(tup)
            if not len(trades):
                if tup[0] == 'BUY':
                    trades.append(tup)
            elif tup[0] != trades[-1][0]:
                trades.append(tup)
            pprint(df)
            pprint(trades)
        except:
            pass

    else:
        stack.pop()
        stack.append(d)


if args.exchange == 'Binance':
    if args.interval == "1m":
        args.interval = Client.KLINE_INTERVAL_1MINUTE
    elif args.interval == "3m":
        args.interval = Client.KLINE_INTERVAL_3MINUTE
    elif args.interval == "5m":
        args.interval = Client.KLINE_INTERVAL_5MINUTE
    elif args.interval == "15m":
        args.interval = Client.KLINE_INTERVAL_15MINUTE
    elif args.interval == "30m":
        args.interval = Client.KLINE_INTERVAL_30MINUTE
    elif args.interval == "1h":
        args.interval = Client.KLINE_INTERVAL_1HOUR
    elif args.interval == "2h":
        args.interval = Client.KLINE_INTERVAL_2HOUR
    elif args.interval == "4h":
        args.interval = Client.KLINE_INTERVAL_4HOUR
    elif args.interval == "6h":
        args.interval = Client.KLINE_INTERVAL_6HOUR
    elif args.interval == "8h":
        args.interval = Client.KLINE_INTERVAL_8HOUR
    else:
        raise Exception('Invalid Interval')

    client = Client('', '')

    config = ''
    with open(f'temp.toml') as f:
        config = f.read()

    print(config)

    bm = BinanceSocketManager(client)
    conn_key = bm.start_kline_socket(
        'BNBBTC', lambda x: binance_message(x, args, config), interval=Client.KLINE_INTERVAL_1MINUTE)
    bm.start()
