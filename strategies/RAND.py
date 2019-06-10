import numpy as np
from pprint import pprint
import matplotlib.pyplot as plt
from numba import jit
import toml
import pandas as pd
import sys
from random import random
sys.path.append("..")
from indicators import MA
from Strategy import Strategy


class MyStrat(Strategy):
    def __init__(self, df, warmup, user_config='', default_config_file='./strategies/RAND/default.toml'):
        self.warmup = int(warmup)
        self.load_config(user_config, default_config_file=default_config_file)
        self.add_indicators(df)
        self.advice = ''

    def load_config(self, user_config, default_config_file='./strategies/RAND/default.toml'):
        # Load Config
        default_config = {}
        with open(default_config_file) as f:
            default_config = toml.loads(f.read())

        self.config = {**default_config, **toml.loads(user_config)}

    def add_indicators(self, df):
        # Add Indicators and store df

        self.df = df.dropna().reset_index(drop=True)
        if not len(self.df):
            raise Exception('Need more data')

    @jit
    def step(self, tup):
        # print(self.config)
        if random() < self.config['RAND']["buy_probability"]:
            self.advice = 'BUY'
        else:
            self.advice = 'SELL'

    def backtest(self, prempt=False, visualize=False):
        self.advice = ''
        self.actions = []
        for i in range(len(self.df)):
            tup = self.df[i:i + 1].reset_index(drop=True)
            self.step(tup)
            if prempt and i == len(self.df) - 1:
                return (self.advice, tup.at[0, 'Close'])
            if i < self.warmup:
                continue
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
        pass
