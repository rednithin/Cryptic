ended = False
try:
    from binance.websockets import BinanceSocketManager
    from binance.client import Client
    import json
    from collections import deque
    import pandas as pd
    import argparse
    from pprint import pprint
    # import toml
    import datetime
    import signal

    parser = argparse.ArgumentParser(description='Parser for Live trading')

    parser.add_argument('-e', '--exchange', help="Exchange name", required=True)
    parser.add_argument('-p', '--pair', help="Pair name", required=True)
    parser.add_argument('-i', '--interval',
                        help="Tick interval duration", required=True)
    parser.add_argument('-s', '--strategy',
                        help="Strategy to be used", required=True)
    parser.add_argument('-w', '--warmup',
                        help="Warmup to be used", required=True)

    args = parser.parse_args()
    stack = deque()

    trades = deque()
    first_price = None
    

    def binance_message(msg, args, config):
        global first_price, ended
        if ended:
            return
        d = {
            'Time': msg['k']['t'],
            'Open': msg['k']['o'],
            'High': msg['k']['h'],
            'Low': msg['k']['l'],
            'Close': msg['k']['c'],
            'Volume': msg['k']['v'],
        }
        # pprint(d)
        # print(first_price)
        if len(stack) == 2 and first_price == None:
            first_price = float(stack[0]["Close"])

        if not len(stack) or stack[-1]['Time'] != d['Time']:
            stack.append(d)
            df = pd.DataFrame(list(stack)[:-1])

            module = __import__(
                f'strategies.{args.strategy}', fromlist=['MyStrat'])
            Strat = getattr(module, 'MyStrat')
            try:
                strat = Strat(df, args.warmup, user_config=config)
                tup = strat.backtest(prempt=True)
                if not len(trades):
                    if tup[0] == 'BUY':
                        trades.append(tup)
                        print(datetime.datetime.now(), tup[0], tup[1])
                elif tup[0] != trades[-1][0]:
                    trades.append(tup)
                    print(datetime.datetime.now(), tup[0], tup[1])
                # pprint(df)
                # pprint(trades)
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
        conn_key = bm.start_kline_socket(args.pair, lambda x: binance_message(x, args, config), interval=Client.KLINE_INTERVAL_1MINUTE)
        bm.start()
        while True:           
            signal.pause()
except:
    amount = 10
    start_amount = amount
    tup = ('SELL', float(stack[-1]["Close"]))
    if len(trades) % 2 != 0:
        trades.append(tup)
        print(datetime.datetime.now(), tup[0], tup[1])
    for i in range(0, len(trades), 2):
        a = float(trades[i][1])
        b = float(trades[i + 1][1])
        # print(a, b)
        change = 1 + (b - a) / a
        amount *= change
    ended = True
    multiplier = 1 + (tup[1] - first_price) / first_price
    print('\n\nStart amount: ', start_amount)
    print('Buy and Hold: ', start_amount * multiplier)
    print('Final Amount: ', amount)
    input('\n\nKeep Pressing KeyboardInterrupt to close...')
