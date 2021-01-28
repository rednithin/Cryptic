import numpy as np
from pprint import pprint
import matplotlib.pyplot as plt

import toml
import pandas as pd
import sys
from collections import deque
from neural_networks import dense_model

sys.path.append("..")
from indicators import MA, SMMA
from Strategy import Strategy


def get_column_name(arr, prefix):
    for column_name in arr:
        if column_name.startswith(prefix):
            return column_name


class MyStrat(Strategy):
    def __init__(self, df, warmup, user_config='', default_config_file='./strategies/SMMA_NN/default.toml'):
        self.warmup = int(warmup)
        self.load_config(user_config, default_config_file=default_config_file)
        self.add_indicators(df)

        self.advice = ''

        self.price_buffer = deque(maxlen=self.config["STRAT"]["max_length"])
        self.model = dense_model(1, self.config)
        self.scale = None

        self.previous_price = 0
        self.previous_action = ''

    def computeScale(self):
        num = float(self.df["High"].max())
        # print("******************HELLLLLLLLLLLLLLLO***********", num)
        if num > 1:
            power = len(str(int(num)))
            return 10 ** power
        else:
            power = 0
            while num < 1:
                print(num)
                num *= 10
                power += 1
            power -= 1
            return 1 / (10 ** power)

    def learn(self):
        pass

    def load_config(self, user_config, default_config_file='./strategies/SMMA_NN/default.toml'):
        # Load Config
        default_config = {}
        with open(default_config_file) as f:
            default_config = toml.loads(f.read())

        self.config = {**default_config, **toml.loads(user_config)}

    def add_indicators(self, df):
        # Add Indicators and store df
        df = SMMA(df, n=self.config['SMMA']['n'])

        self.df = df.dropna().reset_index(drop=True)
        if not len(self.df):
            raise Exception('Need more data')
        columns = list(df.columns)

        self.column = {
            "SMMA": get_column_name(columns, f"SMMA_{self.config['SMMA']['n']}"),
        }

    
    def step(self, tup):
        self.scale = self.computeScale() if not self.scale else self.scale
        # self.scale = 1
        self.price_buffer.append(tup.at[0, self.column["SMMA"]] / self.scale)

        if len(self.price_buffer) > 2:
            x = np.array(list(self.price_buffer)[:-1]).reshape(-1, 1)
            y = np.array(list(self.price_buffer)[1:]).reshape(-1, 1)
            self.model.fit(x, y, epochs=self.config["NN"]["epochs"], validation_data=(
                x, y),)

        prediction = (self.model.predict(
            np.array([self.price_buffer[-1]]))*self.scale)[0, 0]
        current_price = tup.at[0, "Close"]

        # input()
        meanp = (current_price + prediction) / 2

        meanAlpha = (meanp - current_price) / current_price * 100
        # print(self.df)
        # print(prediction, current_price / self.scale,
        #       self.previous_price, self.price_buffer)
        # input()

        signalSell = current_price > self.previous_price or current_price < (
            self.previous_price * self.config["STRAT"]["hodl_threshold"])

        signal = meanp < current_price

        if self.previous_action != 'BUY' and signal == False and meanAlpha > self.config["STRAT"]["threshold_buy"]:
            self.advice = 'BUY'
        elif self.previous_action != 'SELL' and signal == True and meanAlpha < self.config["STRAT"]["threshold_sell"] and signalSell:
            self.advice = 'SELL'
        else:
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
            if self.advice != '':
                self.previous_price = tup.at[0, 'Close']
                self.previous_action = self.advice

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
        # print(self.df)
        x = list(range(len(self.df)))

        plt.title('MA')
        plt.plot(x, self.df['Close'])
        plt.plot(x, self.df[self.column["MAslow"]], label='slow')
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
