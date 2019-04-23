from process_data import get_data
from strategies.macd_cci_rsi import MyStrat
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
n = 12
low = 0.4
high = 0.9
persistence = 1


[CCI]
n = 13
up = 0.3
down = -1.8
persistence = 3

[MACD]
n_fast = 12
n_slow = 26
down = -3.2
up = 0.8
persistence = 4
'''

strat = MyStrat(df, user_config=config)

# strat.visualize()
bestResult, _ = strat.backtest(visualize=False)
bestConfig = config

try:
    while True:
        RSI = random.choice(np.arange(10, 20, 1))
        RSI_low = random.choice(np.arange(0, .5, .1))
        RSI_high = random.choice(np.arange(.5, 1, .1))
        RSI_persistence = random.choice(np.arange(1, 6, 1))

        MACD_fast = random.choice(np.arange(10, 16, 1))
        MACD_slow = random.choice(np.arange(23, 30, 1))
        MACD_down = random.choice(np.arange(0, 4, .2))
        MACD_up = random.choice(np.arange(0, 4, .2))
        MACD_persistence = random.choice(np.arange(1, 6, 1))

        CCI = random.choice(np.arange(10, 20, 1))
        CCI_up = random.choice(np.arange(.3, 3, .3))
        CCI_down = random.choice(np.arange(.3, 3, .3))
        CCI_persistence = random.choice(np.arange(1, 6, 1))
        fconfig = f'''
[RSI]
n = {RSI}
low = {RSI_low}
high = {RSI_high}
persistence = {RSI_persistence}


[CCI]
n = {CCI}
up = {CCI_up}
down = -{CCI_down}
persistence = {CCI_persistence}

[MACD]
n_fast = {MACD_fast}
n_slow = {MACD_slow}
down = -{MACD_down}
up = {MACD_up}
persistence = {MACD_persistence}
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
