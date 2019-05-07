import pandas as pd
import numpy as np


class Columns(object):
    OPEN = 'Open'
    HIGH = 'High'
    LOW = 'Low'
    CLOSE = 'Close'
    VOLUME = 'Volume'
    BASEVOLUME = 'BaseVolume'


indicators = ["MA", "EMA", "MOM", "ROC", "ATR", "BBANDS", "STOK", "STO",
              "ADX", "MACD", "RSI", "TSI", "MFI", "OBV", "CCI", "STDDEV"]


class Settings(object):
    join = True
    col = Columns()


SETTINGS = Settings()


def out(settings, df, result):
    if not settings.join:
        return result
    else:
        df = df.join(result)
        return df


def MA(df, n, price='Close'):
    """
    Moving Average
    """
    name = 'MA_{n}'.format(n=n)
    result = pd.Series(df[price].rolling(n).mean(), name=name)
    return out(SETTINGS, df, result)


def emaHelper(price, n, alphaIn=None):
    """
    Algorithm by Stockchart
    """
    length_of_df = len(price.axes[0])

    initial_sma = price[0:n].mean()

    ema = pd.Series(np.nan, index=range(0, length_of_df))
    ema.iat[n - 1] = initial_sma

    if(not alphaIn):
        alpha = (2.0 / (n + 1.0))
    else:
        alpha = alphaIn

    for i in range(n, length_of_df):
        ema.iat[i] = price.iat[i] * alpha + (1 - alpha) * ema.iat[i - 1]

    return ema


def EMA(df, n, price='Close'):
    """
    Exponential Moving Average
    """
    result = emaHelper(df[price], n)
    result = pd.Series(result, name='EMA_' + str(n))
    return out(SETTINGS, df, result)


def MOM(df, n, price='Close'):
    """
    Momentum
    """
    result = pd.Series(df[price].diff(n), name='Momentum_' + str(n))
    return out(SETTINGS, df, result)


def ROC(df, n, price='Close'):
    """
    Rate of Change
    """
    M = df[price].diff(n - 1)
    N = df[price].shift(n - 1)
    result = pd.Series(M / N, name='ROC_' + str(n))
    return out(SETTINGS, df, result)


def BBANDS(df, n, nbdevup=2, nbdevdn=2, price='Close'):
    """
    Bollinger Bands
    """
    MA = pd.Series(df[price].rolling(n).mean())
    MSD = pd.Series(df[price].rolling(n).std())
    # b1 = 4 * MSD / MA
    # B1 = pd.Series(b1, name='BollingerB_' + str(n))
    # b2 = (df[price] - MA + 2 * MSD) / (4 * MSD)
    # B2 = pd.Series(b2, name='Bollinger%b_' + str(n))

    B1 = pd.Series(MA - (MSD * nbdevdn), name='BBANDS_lower_' + str(n))
    B2 = pd.Series(MA, name='BBANDS_middle_' + str(n))
    B3 = pd.Series(MA + (MSD * nbdevup), name='BBANDS_upper_' + str(n))
    result = pd.DataFrame([B1, B2, B3]).transpose()
    return out(SETTINGS, df, result)


def STOK(df):
    """
    Stochastic oscillator %K
    """
    result = pd.Series((df['Close'] - df['Low'])
                       / (df['High'] - df['Low']), name='SO%k')
    return out(SETTINGS, df, result)


def STO(df, n):
    """
    Stochastic oscillator %D
    """
    SOk = pd.Series((df['Close'] - df['Low'])
                    / (df['High'] - df['Low']), name='SO%k')
    result = pd.Series(SOk.ewm(span=n, min_periods=n
                               - 1).mean(), name='SO%d_' + str(n))
    return out(SETTINGS, df, result)


def SMA(df, timeperiod, key='Close'):
    result = df[key].rolling(timeperiod, min_periods=timeperiod).mean()
    result = pd.Series(result, name='SMA_' + str(timeperiod))
    return out(SETTINGS, df, result)


def ADX(df, n, n_ADX):
    """
    Average Directional Movement Index
    """
    i = 0
    UpI = []
    DoI = []
    while i + 1 <= len(df) - 1:  # df.index[-1]:
        UpMove = df.iat[i + 1,
                        df.columns.get_loc('High')] - df.iat[i, df.columns.get_loc('High')]
        DoMove = df.iat[i, df.columns.get_loc(
            'Low')] - df.iat[i + 1, df.columns.get_loc('Low')]
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else:
            UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else:
            DoD = 0
        DoI.append(DoD)
        i = i + 1
    i = 0
    TR_l = [0]
    while i < len(df) - 1:  # df.index[-1]:
        TR = max(df.iat[i + 1, df.columns.get_loc('High')], df.iat[i, df.columns.get_loc('Close')]) - \
            min(df.iat[i + 1, df.columns.get_loc('Low')],
                df.iat[i, df.columns.get_loc('Close')])
        TR_l.append(TR)
        i = i + 1
    TR_s = pd.Series(TR_l)
    ATR = pd.Series(TR_s.ewm(span=n, min_periods=n).mean())
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    PosDI = pd.Series(UpI.ewm(span=n, min_periods=n - 1).mean() / ATR)
    NegDI = pd.Series(DoI.ewm(span=n, min_periods=n - 1).mean() / ATR)
    temp = abs(PosDI - NegDI) / (PosDI + NegDI)
    result = pd.Series(temp.ewm(span=n_ADX, min_periods=n_ADX
                                - 1).mean(), name='ADX_' + str(n) + '_' + str(n_ADX))
    return out(SETTINGS, df, result)


def MACD(df, n_fast, n_slow, n_sig=9, price='Close'):
    """
    MACD, MACD Signal and MACD difference
    """
    EMAfast = pd.Series(df[price].ewm(
        span=n_fast, min_periods=n_slow - 1).mean())
    EMAslow = pd.Series(df[price].ewm(
        span=n_slow, min_periods=n_slow - 1).mean())
    MACD = pd.Series(EMAfast - EMAslow, name='MACD_%d_%d' % (n_fast, n_slow))
    MACDsign = pd.Series(MACD.ewm(span=n_sig, min_periods=n_sig - 1).mean(),
                         name='MACDsign_%d_%d' % (n_fast, n_slow))
    MACDdiff = pd.Series(
        MACD - MACDsign, name='MACDdiff_%d_%d' % (n_fast, n_slow))
    result = pd.DataFrame([MACD, MACDsign, MACDdiff]).transpose()
    return out(SETTINGS, df, result)


def RSI(df, n):
    """
    Relative Strength Index
    """
    i = 0
    UpI = [0]
    DoI = [0]
    while i + 1 <= len(df) - 1:  # df.index[-1]
        UpMove = df.iat[i + 1,
                        df.columns.get_loc('High')] - df.iat[i, df.columns.get_loc('High')]
        DoMove = df.iat[i, df.columns.get_loc(
            'Low')] - df.iat[i + 1, df.columns.get_loc('Low')]
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else:
            UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else:
            DoD = 0
        DoI.append(DoD)
        i = i + 1
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    PosDI = pd.Series(UpI.ewm(span=n, min_periods=n - 1).mean())
    NegDI = pd.Series(DoI.ewm(span=n, min_periods=n - 1).mean())
    result = pd.Series(PosDI / (PosDI + NegDI), name='RSI_' + str(n))
    return out(SETTINGS, df, result)


def TSI(df, r, s):
    """
    True Strength Index
    """
    M = pd.Series(df['Close'].diff(1))
    aM = abs(M)
    EMA1 = pd.Series(M.ewm(span=r, min_periods=r - 1).mean())
    aEMA1 = pd.Series(aM.ewm(span=r, min_periods=r - 1).mean())
    EMA2 = pd.Series(EMA1.ewm(span=s, min_periods=s - 1).mean())
    aEMA2 = pd.Series(aEMA1.ewm(span=s, min_periods=s - 1).mean())
    result = pd.Series(EMA2 / aEMA2, name='TSI_' + str(r) + '_' + str(s))
    return out(SETTINGS, df, result)


def MFI(df, n):
    """
    Money Flow Index and Ratio
    """
    PP = (df['High'] + df['Low'] + df['Close']) / 3
    i = 0
    PosMF = [0]
    while i < len(df) - 1:  # df.index[-1]:
        if PP[i + 1] > PP[i]:
            PosMF.append(PP[i + 1] * df.iat[i + 1,
                                            df.columns.get_loc('Volume')])
        else:
            PosMF.append(0)
        i = i + 1
    PosMF = pd.Series(PosMF)
    TotMF = PP * df['Volume']
    MFR = pd.Series(PosMF / TotMF)
    result = pd.Series(MFR.rolling(n).mean(), name='MFI_' + str(n))
    return out(SETTINGS, df, result)


def CCI(df, n):
    """
    Commodity Channel Index
    """
    PP = (df['High'] + df['Low'] + df['Close']) / 3
    result = pd.Series((PP - PP.rolling(n).mean())
                       / PP.rolling(n).std(), name='CCI_' + str(n))
    return out(SETTINGS, df, result)


def STDDEV(df, n):
    """
    Standard Deviation
    """
    result = pd.Series(df['Close'].rolling(n).std(), name='STD_' + str(n))
    return out(SETTINGS, df, result)


def OBV(df, n):
    """
    On-balance Volume
    """
    i = 0
    OBV = [0]
    while i < len(df) - 1:  # df.index[-1]:
        if df.iat[i + 1, df.columns.get_loc('Close')] - df.iat[i, df.columns.get_loc('Close')] > 0:
            OBV.append(df.iat[i + 1, df.columns.get_loc('Volume')])
        if df.iat[i + 1, df.columns.get_loc('Close')] - df.iat[i, df.columns.get_loc('Close')] == 0:
            OBV.append(0)
        if df.iat[i + 1, df.columns.get_loc('Close')] - df.iat[i, df.columns.get_loc('Close')] < 0:
            OBV.append(-df.iat[i + 1, df.columns.get_loc('Volume')])
        i = i + 1
    OBV = pd.Series(OBV)
    result = pd.Series(OBV.rolling(n).mean(), name='OBV_' + str(n))
    return out(SETTINGS, df, result)


def ATR(df, n):
    """
    Average True Range
    """
    L = len(df['High'])
    TR_l = [None] * L
    for i in range(1, L):
        TR = max(df['High'].iloc[i] - df['Low'].iloc[i],
                 abs(df['High'].iloc[i] - df['Close'].iloc[i - 1]),
                 abs(df['Low'].iloc[i] - df['Close'].iloc[i - 1]))
        TR_l[i] = TR

    TR_s = pd.Series(TR_l[1::])

    alpha = 1.0 / n
    result = emaHelper(TR_s, n, alpha)
    result = pd.Series(result, name='ATR_' + str(n))
    return out(SETTINGS, df, result)


def SMMA(df, n):
    """
    Smoothed Moving Average.
    Formula:
    smma = avg(data(n)) - avg(data(n)/n) + data(t)/n
    """
    name = 'SMMA_{n}'.format(n=n)
    middle = df[['Close', 'High', 'Low']].sum(axis=1) / 3
    result = pd.Series(middle.ewm(alpha=1.0 / n).mean(), name=name)
    return out(SETTINGS, df, result)
    # return series.ewm(alpha=1.0/period).mean().values.flatten()
