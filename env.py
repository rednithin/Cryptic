import gym
import numpy as np
from random import choice
from functions import *


class TradingEnv(gym.Env):
    def __init__(self, X, drop_column_names=[], window_size=40):
        self.nb_actions = 2
        self.X = X
        self.window_size = window_size
        self.position = self.window_size + 3
        self.drop_column_names = drop_column_names

    # Next state, Reward, Done, _
    def step(self, action):
        next_state = self.X.loc[self.position +
                                2 - self.window_size: self.position + 1]
        reward = 0
        done = False
        if self.position >= len(self.X) - 3:
            done = True

        if action == 0:  # BUY
            a = self.X.at[self.position, 'Close']
            b = self.X.at[self.position + 1, 'Close']
            c = self.X.at[self.position + 2, 'Close']
            if a > b:
                reward += 1
                if c > b:
                    reward += 1
            elif a < b:
                reward -= 1
                if c < b:
                    reward -= 1

        elif action == 1:  # SELL
            a = self.X.at[self.position, 'Close']
            b = self.X.at[self.position + 1, 'Close']
            c = self.X.at[self.position + 2, 'Close']
            if a < b:
                reward += 1
                if c < b:
                    reward += 1
            elif a > b:
                reward -= 1
                if c > b:
                    reward -= 1

        else:
            raise Exception("Invalid Action")

        self.position += choice([1])
        next_state = normalize(next_state)
        next_state = drop_columns(next_state, self.drop_column_names)
        return next_state.values, reward, done, {"price": self.X.at[self.position, 'Close']}

    def reset(self):
        self.position = self.window_size + 3
        next_state = self.X.loc[self.position +
                                2 - self.window_size: self.position + 1]
        next_state = normalize(next_state)
        next_state = drop_columns(next_state, self.drop_column_names)
        return next_state.values, 0, False, {"price": self.X.at[self.position, 'Close']}

    def render(self, mode='human', close=False):
        pass
