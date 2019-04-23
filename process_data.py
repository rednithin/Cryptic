from indicators import *
import pandas as pd


def get_data(filepath, features):
    df = pd.read_csv(filepath)
    df = df[features]

    return df


def add_indicators(df):
    open = df['Open']
    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume']

    # Relative Candles
    # df['Bar_HO'] = high - open
    # df['Bar_HL'] = high - low
    # df['Bar_HC'] = high - close
    # df['Bar_CO'] = close - open
    # df['Bar_CL'] = close - low
    # df['Bar_OL'] = open - low
    # df['Bar_MOV'] = close - close.shift(1)

    # #  Adjacent Candles
    # df['Adj_Open'] = open / close
    # df['Adj_High'] = high / close
    # df['Adj_Low'] = low / close

    df = MA(df, 5)
    df = MA(df, 15)
    df = MA(df, 75)
    df = MA(df, 7)
    df = MA(df, 25)
    df = MA(df, 99)

    # # Simple Moving Averages
    # df = SMA(df, 5)
    # df = SMA(df, 10)
    # df = SMA(df, 20)
    # df = SMA(df, 120)

    # # Exponential Moving Averages
    # df = EMA(df, 12)
    # df = EMA(df, 26)

    # Technical Indicators
    # df = OBV(df, 14)
    # df = MOM(df, 30)
    df = RSI(df, 14)
    # df = MFI(df, 14)
    df = CCI(df, 14)
    # # df = ATR(df, 14)
    # df = STDDEV(df, 5)
    df = MACD(df, 12, 26)
    df = BBANDS(df, 20)
    # df = STO(df, 10)
    # df = STOK(df)

    return df
