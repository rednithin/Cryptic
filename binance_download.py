import pandas as pd
import numpy as np
from binance.client import Client


def download_dataset(filename, columns, pair="BTCUSDT", interval=Client.KLINE_INTERVAL_1HOUR, start_date="13 March, 2019", end_date="12 April, 2019"):

    client = Client("", "")
    dataset = client.get_historical_klines(
        pair, Client.KLINE_INTERVAL_1HOUR, start_date, end_date)

    time_diff = set()
    for i in range(len(dataset) - 1):
        time_diff.add(int(dataset[i + 1][0]) - int(dataset[i][0]))

    print(f"Time Difference Set: {time_diff}")
    assert len(time_diff) == 1
    print(f"Dataset Length: {len(dataset)}")
    print(columns)
    dataset = pd.DataFrame(data=np.array(dataset), columns=columns[0])
    print(dataset)
    dataset.to_csv(filename, index=False)


columns = [
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

# download_dataset('./data/binance3.csv', columns, pair="BTCUSDT", interval=Client.KLINE_INTERVAL_30MINUTE,
#                  start_date="1 January, 2019", end_date="1 February, 2019")

# download_dataset('./data/binance4.csv', columns, pair="BTCUSDT", interval=Client.KLINE_INTERVAL_1HOUR,
#                  start_date="1 January, 2019", end_date="1 February, 2019")

# download_dataset('./data/binance5.csv', columns, pair="BNBBTC", interval=Client.KLINE_INTERVAL_1HOUR,
#                  start_date="13 March, 2019", end_date="19 April, 2019")

download_dataset('./data/binance6.csv', columns, pair="BNBBTC", interval=Client.KLINE_INTERVAL_1HOUR,
                 start_date="1 December, 2018", end_date="10 March, 2019")
