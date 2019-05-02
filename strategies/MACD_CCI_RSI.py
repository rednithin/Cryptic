import numpy as np
from pprint import pprint
import matplotlib.pyplot as plt
from numba import jit
from indicators import CCI, RSI, MACD
import toml
import pandas as pd
import sys
sys.path.append("..")


def get_column_name(arr, prefix):
    for column_name in arr:
        if column_name.startswith(prefix):
            return column_name


class MyStrat():
    def __init__(self, df, user_config='', default_config_file='./strategies/MACD_CCI_RSI/default.toml'):
        self.load_config(user_config, default_config_file=default_config_file)
        self.add_indicators(df)
        self.trend = {
            'duration': 0,
            'persisted': False,
            'direction': '',
            'adviced': False
        }
        self.advice = ''

    def load_config(self, user_config, default_config_file='./strategies/MACD_CCI_RSI/default.toml'):
        # Load Config
        default_config = {}
        with open(default_config_file) as f:
            default_config = toml.loads(f.read())

        self.config = {**default_config, **toml.loads(user_config)}

    def add_indicators(self, df):
        # Add Indicators and store df
        df = CCI(df, n=self.config['CCI']['n'])
        df = RSI(df, n=self.config['RSI']['n'])
        df = MACD(
            df,
            n_fast=self.config['MACD']['n_fast'],
            n_slow=self.config['MACD']['n_slow'])
        self.df = df.dropna().reset_index(drop=True)
        if not len(self.df):
            raise Exception('Need more data')
        columns = list(df.columns)
        self.column = {
            "CCI": get_column_name(columns, "CCI_"),
            "RSI": get_column_name(columns, "RSI_"),
            "MACD": get_column_name(columns, "MACD_"),
            "MACDdiff": get_column_name(columns, "MACDdiff_"),
            "MACDsign": get_column_name(columns, "MACDsign_"),
        }

    @jit
    def step(self, tup):
        cci = tup.at[0, self.column["CCI"]]
        rsi = tup.at[0, self.column["RSI"]]
        macd = tup.at[0, self.column["MACD"]]

        # Uptrend
        if (cci > self.config['CCI']['up'] and
            rsi <= self.config['RSI']['low'] and
                macd >= self.config['MACD']['up']):
            if (self.trend['direction'] != 'up'):
                self.trend = {
                    "duration": 0,
                    "persisted": False,
                    "direction": 'up',
                    "adviced": False
                }

            self.trend['duration'] += 1

            if (self.trend['duration'] >= self.config['RSI']['persistence'] and
                self.trend['duration'] >= self.config['CCI']['persistence'] and
                    self.trend['duration'] >= self.config['MACD']['persistence']):
                self.trend['persisted'] = True

            if (self.trend['persisted'] and not self.trend['adviced']):
                self.trend['adviced'] = True
                self.advice = 'BUY'
            else:
                self.advice = ''

        # Downtrend
        elif (cci < self.config['CCI']['down'] and
                rsi >= self.config['RSI']['high'] and
                macd <= self.config['MACD']['down']):
            if (self.trend['direction'] != 'down'):
                self.trend = {
                    "duration": 0,
                    "persisted": False,
                    "direction": 'down',
                    "adviced": False
                }

            self.trend['duration'] += 1

            if (self.trend['duration'] >= self.config['RSI']['persistence'] and
                self.trend['duration'] >= self.config['CCI']['persistence'] and
                    self.trend['duration'] >= self.config['MACD']['persistence']):
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

    def backtest(self, prempt=False, visualize=False):
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
            if prempt and i == len(self.df) - 1:
                return (self.advice, tup.at[0, 'Close'])
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
            a = self.actions[i][2]
            b = self.actions[i + 1][2]
            print(a, b)
            change = 1 + (b - a) / a
            amount *= change

        a = self.df.at[0, 'Close']
        b = self.df.at[len(self.df) - 1, 'Close']
        print(a, b)
        buy_and_hold = initial_amount * (1 + (b - a) / a)

        print(
            f'Initial Amount: {initial_amount} | Final Amount: {amount} | Buy&Hold: {buy_and_hold} |')

        if visualize:
            self.visualize(self.actions)
        y = list(self.df['Close'].values)
        x = list(range(len(self.df)))
        buy_x = [x[0] for x in self.actions if x[1] == 'BUY']
        buy_y = [x[2] for x in self.actions if x[1] == 'BUY']

        sell_x = [x[0] for x in self.actions if x[1] == 'SELL']
        sell_y = [x[2] for x in self.actions if x[1] == 'SELL']

        return amount, {
            "table": [
                {
                    "key": 1,
                    "name": "Initial amount",
                    "value": initial_amount
                },
                {
                    "key": 2,
                    "name": "Final amount",
                    "value": amount
                },
                {
                    "key": 3,
                    "name": "Buy and Hold",
                    "value": buy_and_hold
                }

            ],
            "graph": [{
                "x": x,
                "y": y,
                "type": 'scatter',
                "mode": 'lines+points',
                "marker": {"color": 'silver'}
            },
                {
                "x": buy_x,
                "y": buy_y,
                "mode": 'markers',
                "marker": {
                    "size": [10] * len(buy_x),
                    "opacity": [.5] * len(sell_x),
                    "color": ["green"] * len(buy_x)
                }
            },
                {
                "x": sell_x,
                "y": sell_y,
                "mode": 'markers',
                "marker": {
                    "size": [10] * len(sell_x),
                    "opacity": [.5] * len(sell_x),
                    "color": ["red"] * len(sell_x)
                }
            }
            ]}

    def visualize(self, actions=[]):
        # print(self.df)
        x = list(range(len(self.df)))

        plt.subplot(2, 2, 1)
        plt.title('CCI')
        plt.plot(x, self.df[self.column["CCI"]], label='cci')
        # plt.legend(loc='best')

        plt.subplot(2, 2, 2)
        plt.title('MACD')
        plt.plot(x, self.df[self.column["MACD"]], label='macd')
        plt.plot(x, self.df[self.column["MACDdiff"]], label='macd_diff')
        # plt.legend(loc='best')

        plt.subplot(2, 2, 3)
        plt.title('RSI')
        plt.plot(x, self.df[self.column["RSI"]], label='rsi')
        # plt.legend(loc='best')

        if actions:
            arr = np.array(actions)
            plt.subplot(2, 2, 4)
            plt.title('Buy Sell')
            plt.plot(x, self.df['Close'])
            buy = arr[arr[:, 1] == 'BUY']
            sell = arr[arr[:, 1] == 'SELL']
            # pprint(buy)
            # pprint(sell)
            plt.scatter(buy[:, 0].astype('float'),
                        buy[:, 2].astype('float'), marker='^', c=['red'] * len(buy))
            plt.scatter(sell[:, 0].astype('float'),
                        sell[:, 2].astype('float'), marker='D', c=['magenta'] * len(sell))
        plt.show()
