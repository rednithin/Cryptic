import toml
import pandas as pd
import sys
sys.path.append("..")
from indicators import MA
from numba import jit
import matplotlib.pyplot as plt
from pprint import pprint
import numpy as np


def get_column_name(arr, prefix):
    for column_name in arr:
        if column_name.startswith(prefix):
            return column_name


class MAStrat():
    def __init__(self, df, user_config='', default_config_file='./strategies/ma.toml'):
        self.load_config(user_config, default_config_file=default_config_file)
        self.add_indicators(df)
        self.trend = {
            'duration': 0,
            'persisted': False,
            'direction': '',
            'adviced': False
        }
        self.advice = ''

    def load_config(self, user_config, default_config_file='./strategies/ma.toml'):
        # Load Config
        default_config = {}
        with open(default_config_file) as f:
            default_config = toml.loads(f.read())

        self.config = {**default_config, **toml.loads(user_config)}

    def add_indicators(self, df):
        # Add Indicators and store df
        df = MA(df, n=self.config['MA']['fast'])
        df = MA(df, n=self.config['MA']['medium'])
        df = MA(df, n=self.config['MA']['slow'])

        self.df = df.dropna().reset_index(drop=True)

        columns = list(df.columns)
        self.column = {
            "MAslow": get_column_name(columns, f"MA_{self.config['MA']['slow']}"),
            "MAmedium": get_column_name(columns, f"MA_{self.config['MA']['medium']}"),
            "MAfast": get_column_name(columns, f"MA_{self.config['MA']['fast']}"),
        }

    @jit
    def step(self, tup):
        ma_slow = tup.at[0, self.column["MAslow"]]
        ma_medium = tup.at[0, self.column["MAmedium"]]
        ma_fast = tup.at[0, self.column["MAfast"]]

        # Uptrend
        if (ma_fast > ma_slow):
            if (self.trend['direction'] != 'up'):
                self.trend = {
                    "duration": 0,
                    "persisted": False,
                    "direction": 'up',
                    "adviced": False
                }

            self.trend['duration'] += 1

            if (self.trend['duration'] >= self.config['MA']['buy_persistence']):
                self.trend['persisted'] = True

            if (self.trend['persisted'] and not self.trend['adviced']):
                self.trend['adviced'] = True
                self.advice = 'BUY'
            else:
                self.advice = ''

        # Downtrend
        elif (ma_fast < ma_medium):
            if (self.trend['direction'] != 'down'):
                self.trend = {
                    "duration": 0,
                    "persisted": False,
                    "direction": 'down',
                    "adviced": False
                }

            self.trend['duration'] += 1

            if (self.trend['duration'] >= self.config['MA']['sell_persistence']):
                self.trend['persisted'] = True

            if (self.trend['persisted'] and not self.trend['adviced']):
                self.trend['adviced'] = True
                self.advice = 'SELL'
            else:
                self.advice = ''

        # No Trend
        else:
            self.trend['adviced'] = False
            self.advice = ''

    def backtest(self, visualize=False):
        self.trend = {
            'duration': 0,
            'persisted': False,
            'direction': '',
            'adviced': False
        }
        self.advice = ''
        self.actions = []
        for i in range(len(self.df)):
            tup = self.df[i:i + 1].reset_index(drop=True)
            self.step(tup)
            if self.advice != '':
                if len(self.actions) == 0:
                    if self.advice == 'BUY':
                        self.actions.append(
                            (i, self.advice, tup.at[0, 'Close']))
                elif self.advice != '' and self.advice != self.actions[-1][1]:
                    self.actions.append(
                        (i, self.advice, tup.at[0, 'Close']))
        pprint(self.actions)
        if self.actions and self.actions[-1][1] == 'BUY':
            self.actions.append((len(self.df) - 1, 'SELL',
                                 self.df.at[len(self.df) - 1, 'Close']))
        initial_amount = 10
        amount = initial_amount
        for i in range(0, len(self.actions) - 1, 2):
            a = self.df.at[i, 'Close']
            b = self.df.at[i + 1, 'Close']

            change = 1 + (b - a) / a
            amount *= change

        buy_and_hold = amount * \
            (1 + (self.df.at[len(self.df) - 1, 'Close'] -
                  self.df.at[0, 'Close']) / self.df.at[0, 'Close'])
        print(
            f'Initial Amount: {initial_amount} | Final Amount: {amount} | Buy&Hold: {buy_and_hold} |')

        if visualize:
            self.visualize(self.actions)
        return amount

    def visualize(self, actions=[]):
        # print(self.df)
        x = list(range(len(self.df)))

        plt.title('MA')
        plt.plot(x, self.df['Close'])
        plt.plot(x, self.df[self.column["MAslow"]], label='slow')
        plt.plot(x, self.df[self.column["MAmedium"]], label='medium')
        plt.plot(x, self.df[self.column["MAfast"]], label='fast')
        # plt.legend(loc='best')

        if actions:
            arr = np.array(actions)
            plt.title('Buy Sell')

            buy = arr[arr[:, 1] == 'BUY']
            sell = arr[arr[:, 1] == 'SELL']
            # pprint(buy)
            # pprint(sell)
            plt.scatter(buy[:, 0].astype('float'),
                        buy[:, 2].astype('float'), marker='^', c=['red'] * len(buy))
            plt.scatter(sell[:, 0].astype('float'),
                        sell[:, 2].astype('float'), marker='D', c=['magenta'] * len(sell))
        plt.show()
