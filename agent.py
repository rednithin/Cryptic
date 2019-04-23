from collections import deque
from env import TradingEnv
from neural_networks import *

import numpy as np
import pandas as pd
import random

from pprint import pprint


class DQNTrader():
    def __init__(self, data, n_episodes=100, gamma=1.0, epsilon=0.99, epsilon_min=0.01, epsilon_log_decay=0.996, batch_size=64):
        self.memory = deque(maxlen=1500)
        self.window_size = 15
        self.drop_column_names = ['Open', 'High', 'Low', 'Close']
        self.env = TradingEnv(
            data, drop_column_names=self.drop_column_names, window_size=self.window_size)
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_log_decay
        self.n_episodes = n_episodes
        self.batch_size = batch_size
        self.n_inputs = len(data.columns) - len(self.drop_column_names)
        self.n_outputs = 2
        # Init model
        self.model = gru_model(
            self.window_size, self.n_inputs, self.n_outputs)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def choose_action(self, state, epsilon):
        if (np.random.random() <= epsilon):
            return np.random.randint(self.env.nb_actions)
        else:
            # if epsilon == 0:
            #     print(self.model.predict(state))
            return np.argmax(self.model.predict(state))

    def get_epsilon(self, t):
        return max(self.epsilon_min, self.epsilon)

    def preprocess_state(self, state):
        return np.reshape(state, [1, self.window_size, self.n_inputs])

    def replay(self, batch_size):
        x_batch, y_batch = [], []
        minibatch = random.sample(
            self.memory, min(len(self.memory), batch_size))
        for state, action, reward, next_state, done in minibatch:
            y_target = self.model.predict(state)
            y_target[0][action] = reward
            # y_target[0][action] = reward if done else reward + \
            #     self.gamma * np.max(self.model.predict(next_state))
            x_batch.append(state[0])
            y_batch.append(y_target[0])
        # pprint(y_batch)
        self.model.fit(np.array(x_batch), np.array(y_batch), epochs=2,
                       batch_size=len(x_batch), verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def fit(self):
        self.load_weights(f'RL-370.h5')
        for e in range(self.n_episodes):
            next_state, reward, done, _ = self.env.reset()
            state = self.preprocess_state(next_state)
            done = False
            n_steps = 1
            correct = 0
            acc_reward = 0
            acc_preward = 0
            acc_nreward = 0
            while not done:
                # self.env.render()
                action = self.choose_action(state, self.get_epsilon(e))
                next_state, reward, done, _ = self.env.step(action)
                acc_reward += reward
                next_state = self.preprocess_state(next_state)
                self.remember(state, action, reward, next_state, done)
                state = next_state
                if reward >= 0:
                    correct += 1
                    acc_preward += reward
                else:
                    acc_nreward += reward
                n_steps += 1
            if e % 1 == 0 and e != 0:
                print('[Episode {}] - correct: {}, acc_reward: {}, acc_preward: {}, acc_nreward: {} accuracy: {}, epsilon: {}.'.format(
                    e, correct, acc_reward, acc_preward, acc_nreward, correct / n_steps, self.epsilon))
                self.test(1)
            if e % 10 == 0 and e != 0:
                self.save_model(f'RL-{e}.h5')
                self.save_model(f'RL.h5')
            self.replay(self.batch_size)
        return e

    def test(self, n_episodes):
        # self.load_weights('RL-10.h5')
        for episode_num in range(n_episodes):
            done = False
            next_state, reward, done, _ = self.env.reset()
            state = self.preprocess_state(next_state)
            step = 0
            wait_for_buy = True
            bought_price = 0
            amount = 10
            while not done:
                # self.env.render()
                action = self.choose_action(state, 0)
                # print(action)
                next_state, _, done, misc = self.env.step(action)
                if wait_for_buy == True and action == 0:
                    bought_price = misc["price"]
                    print(f'Bought at: {misc["price"]} -> ', end='')
                    wait_for_buy = False
                elif wait_for_buy == False and action == 1:
                    p = 1 + (misc["price"] - bought_price) / bought_price
                    print(f'Sold at: {misc["price"]}')
                    amount *= p
                    wait_for_buy = True
                state = self.preprocess_state(next_state)
                step += 1
            print(f"\nFinal amount: {amount}")

    def save_model(self, filename):
        self.model.save_weights(filename)

    def load_weights(self, filename):
        self.model.load_weights(filename)
