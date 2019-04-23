from process_data import get_data
from strategies.i_wanna_be_rich import IWannaBeRich
import numpy as np
import random

settings = {
    "filepath": "./data/binance3.csv",
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
[RSI]
n = 10
low = 0.4
high = 0.6
persistence = 1

[BBANDS]
n = 17
nbdevdn = 0.8999999999999999
nbdevup = 1.2999999999999998

[MACD]
n_fast = 12
n_slow = 26
down = -1.0
up = 1.0
persistence = 1
'''

strat = IWannaBeRich(df, user_config=config)

# strat.visualize()
bestResult = strat.backtest(visualize=True)
bestConfig = config

try:
    while True:
        RSI = random.choice(np.arange(10, 20, 1))
        RSI_low = random.choice(np.arange(0, .5, .1))
        RSI_high = random.choice(np.arange(.5, 1, .1))
        RSI_persistence = random.choice(np.arange(1, 5, 1))

        MACD_fast = random.choice(np.arange(10, 16, 1))
        MACD_slow = random.choice(np.arange(23, 30, 1))
        MACD_down = random.choice(np.arange(0, 4, .2))
        MACD_up = random.choice(np.arange(0, 4, .2))
        MACD_persistence = random.choice(np.arange(1, 5, 1))

        BBANDS = random.choice(np.arange(15, 25, 1))
        BBANDS_up = random.choice(np.arange(0.5, 2.5, .2))
        BBANDS_dn = random.choice(np.arange(0.5, 2.5, .2))
        fconfig = f'''
[RSI]
n = {RSI}
low = {RSI_low}
high = {RSI_high}
persistence = {RSI_persistence}

[BBANDS]
n = {BBANDS}
nbdevdn = {BBANDS_up}
nbdevup = {BBANDS_dn}

[MACD]
n_fast = {MACD_fast}
n_slow = {MACD_slow}
down = -{MACD_down}
up = {MACD_up}
persistence = {MACD_persistence}
'''
        strat = IWannaBeRich(df, user_config=fconfig)
        result = strat.backtest()
        print(f"********BEST RESULT: {bestResult}")
        if (result > bestResult):
            print('********************FOUND BEST**********************')
            bestConfig = fconfig
            bestResult = result

except KeyboardInterrupt:
    print('LOL')
    print(bestConfig)
