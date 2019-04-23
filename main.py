from binance_download import download_dataset
from process_data import get_data, add_indicators
from agent import DQNTrader
from sklearn import preprocessing
from collections import deque
import numpy as np
import random
import time
from neural_networks import nn
import matplotlib.pyplot as plt

print('HELLO')

settings = {
    "filepath": "./data/binance6.csv",
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

# download_dataset(settings["filepath"], settings["columns"])
TIME_STEP = 1
df = get_data(settings["filepath"], settings["features"])
df = add_indicators(df)
df['Future'] = df['Close'].shift(-TIME_STEP)

# df = df[130: - TIME_STEP].reset_index(drop=True)
df = df.dropna().reset_index(drop=True)
# x = list(range(len(df)))
# plt.plot(x, df['Close'].values)
# plt.plot(x, df['BB_lower_20'].values)
# plt.plot(x, df['BB_middle_20'].values)
# plt.plot(x, df['BB_upper_20'].values)
# plt.show()
print(df)
print(df.columns)

# df = df[-1000:].reset_index(drop=True)
assert df.isnull().values.any() == False
# print(df)

# agent = DQNTrader(df, batch_size=256, n_episodes=1000)
# # agent.fit()
# agent.test(1)

WINDOW_LENGTH = 30
EPOCHS = 100
BATCH_SIZE = 64
NAME = f"{WINDOW_LENGTH}-SEQ-{TIME_STEP}-PRED-{int(time.time())}"


def classify(current, next):
    if float(next) > float(current):
        return 0
    else:
        return 1


df['BuySell'] = list(map(classify, df['Close'], df['Future']))
df = df.drop(['Future'], axis=1)

print(df)

train = df[:int(len(df) * .95)].reset_index(drop=True)
validation = df[-int(len(df) * .05):].reset_index(drop=True)


def preprocess_df(df):
    for col in df.columns:
        if col in ['Open', 'High', 'Low', 'Close', 'Volume'] or col.startswith("BBANDS") or col.startswith("MA_"):
            df[col] = df[col].pct_change()
            df.dropna(inplace=True)
            df[col] = preprocessing.scale(df[col].values)
        elif col not in ['BuySell']:
            df[[col]] = preprocessing.StandardScaler().fit_transform(df[[col]])
            df.dropna(inplace=True)

    df.dropna(inplace=True)
    sequential_data = []
    sequence = deque(maxlen=WINDOW_LENGTH)

    for i in df.values:
        sequence.append([n for n in i[:-1]])
        if(len(sequence) == WINDOW_LENGTH):
            sequential_data.append([np.array(sequence), i[-1]])

    buys = []
    sells = []

    for seq, target in sequential_data:
        if target == 0:
            buys.append([seq, target])
        elif target == 1:
            sells.append([seq, target])

    random.shuffle(buys)
    random.shuffle(sells)

    lower = min(len(buys), len(sells))
    buys = buys[: lower]
    sells = sells[: lower]

    sequential_data = buys + sells

    random.shuffle(sequential_data)

    X = []
    Y = []

    for seq, target in sequential_data:
        X.append(seq)
        Y.append(target)

    return np.array(X), np.array(Y, dtype='int')


train_x, train_y = preprocess_df(train)
validation_x, validation_y = preprocess_df(validation)

assert (train_y == 0).sum() == (train_y == 1).sum()
assert (validation_y == 0).sum() == (validation_y == 1).sum()

# print(train_x)
# input()

# print(train_y)
# input()

# print(validation_x)
# input()

# print(validation_y)
# input()

model, tensorboard, checkpoint = nn(train_x.shape, NAME)

history = model.fit(
    train_x, train_y,
    batch_size=BATCH_SIZE,
    epochs=EPOCHS,
    validation_data=(validation_x, validation_y),
    callbacks=[tensorboard, checkpoint]
)
