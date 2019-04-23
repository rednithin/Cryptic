import pandas as pd
import numpy as np
from binance.client import Client


def binance(filename, columns, pair="BTCUSDT", interval=Client.KLINE_INTERVAL_1HOUR, start_date="13 March, 2019", end_date="12 April, 2019", *args, **kwargs):

    client = Client("", "")
    dataset = client.get_historical_klines(
        pair, interval, start_date, end_date)

    time_diff = set()
    for i in range(len(dataset) - 1):
        time_diff.add(int(dataset[i + 1][0]) - int(dataset[i][0]))

    print(f"Time Difference Set: {time_diff}")
    assert len(time_diff) == 1
    print(f"Dataset Length: {len(dataset)}")
    print(columns)
    dataset = pd.DataFrame(data=np.array(dataset), columns=columns[0])
    print(dataset)
    dataset.to_csv("./data/" + filename + ".csv", index=False)
