from process_data import get_data
from strategies.ma import MyStrat
import numpy as np
import random

settings = {
    "filepath": "./data/binance5.csv",
    "columns": [
        'Open Time',
        'Open',
        'High',
        'Low',
        'Close',
        'Volume',
        'Close Time',
        'Quote Asset Volume',
        'Number Of Trades',
        'Taker Buy Base Asset Volume',
        'Taker Buy Quote Asset Volume',
        'Ignore'
    ],
    "features": [
        # 'Open Time',
        'Open',
        'High',
        'Low',
        'Close',
        'Volume',
        # 'Close Time',
        # 'Quote Asset Volume',
        # 'Number Of Trades',
        # 'Taker Buy Base Asset Volume',
        # 'Taker Buy Quote Asset Volume',
        # 'Ignore'
    ]
}

TIME_STEP = 1
df = get_data(settings["filepath"], settings["features"])

config = '''
[MA]
fast = 5
medium = 15
slow = 75
buy_persistence = 1
sell_persistence = 1
'''

strat = MyStrat(df, user_config=config)

# strat.visualize()
bestResult, _ = strat.backtest(visualize=False)
bestConfig = config

try:
    while True:
        MA_fast = random.choice(np.arange(5, 12, 1))
        MA_medium = random.choice(np.arange(15, 55, 1))
        MA_slow = random.choice(np.arange(75, 120, 1))
        MA_buy_persistence = random.choice(np.arange(1, 6, 1))
        MA_sell_persistence = random.choice(np.arange(1, 6, 1))

        fconfig = f'''
[MA]
fast = {MA_fast}
medium = {MA_medium}
slow = {MA_slow}
buy_persistence = {MA_buy_persistence}
sell_persistence = {MA_sell_persistence}
'''
        strat = MyStrat(df, user_config=fconfig)
        result, _ = strat.backtest()
        print(f"********BEST RESULT: {bestResult}")
        if (result > bestResult):
            print('********************FOUND BEST**********************')
            bestConfig = fconfig
            bestResult = result

except KeyboardInterrupt:
    print('LOL')
    print(bestConfig)
