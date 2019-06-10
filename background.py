import pandas as pd
import numpy as np
from binance.client import Client
import toml
from copy import deepcopy
from random import choice


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


def hyper_param_optimize(payload):
    hyper = toml.loads(payload["config"])

    module = __import__(
        f'strategies.{payload["strategy"]}', fromlist=['MyStrat'])
    Strat = getattr(module, 'MyStrat')

    dfs = []
    for filename in payload["filenames"]:
        dfs.append(pd.read_csv(f'data/{filename}'))

    if hyper["MISC"]["opt"] == 1:
        bestScore = 0
        bestConfig = ''
        for _ in range(hyper["MISC"]["tries"]):
            # Parsing to get config
            config = deepcopy(hyper)
            for h in hyper:
                if h != 'MISC':
                    for k in hyper[h]:
                        if isinstance(hyper[h][k], list) and len(hyper[h][k]) == 3 and not isinstance(hyper[h][k][0], str):
                            config[h][k] = choice(
                                np.arange(*hyper[h][k]).tolist())
                        elif isinstance(hyper[h][k], list):
                            config[h][k] = choice(hyper[h][k])
                        else:
                            raise Exception('Parsing Error')
            summ = 0

            # print(toml.dumps(config))
            # input()
            # continue

            for df in dfs:
                strat = Strat(df, payload["warmup"],
                              user_config=toml.dumps(config))
                result, _ = strat.backtest()
                summ += result
            print(f'**********CURRENT BEST***********\n{bestScore}')
            if summ > bestScore:
                bestScore = summ
                bestConfig = config
                finalConfig = deepcopy(bestConfig)
                del finalConfig["MISC"]
                with open(f"strategies/{payload['strategy']}/{payload['savefile']}.toml", 'w') as f:
                    f.write(toml.dumps(finalConfig))
    else:
        raise Exception('Undefined Optimizer')
