# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

# à⁄ìÆïΩãœ
def mv_avrg( df, window_size ):
    mv_avrg = df.rolling(window=window_size).mean()
    return mv_avrg

# RSI
def rsi( df, window_size):
    diff = df.diff()
    diff = diff[1:]
    up, down = diff.copy(), diff.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    up_sma_14 = up.rolling(window=window_size, center=False).mean()
    down_sma_14 = down.abs().rolling(window=window_size, center=False).mean()
    RS = up_sma_14 / down_sma_14
    RSI = 100.0 - (100.0 / (1.0 + RS))

    return RSI

# àÍñ⁄ãœçtï\
def ichimoku(df):
    h = df.high
    l = df.low
 
    max_9 = h.rolling(window=9, min_periods=1).max()
    min_9 = l.rolling(window=9, min_periods=1).min()
    tenkan = (max_9+min_9)/2
    base = (h.rolling(window=26, min_periods=1).max()+l.rolling(window=26, min_periods=1).min())/2
    senkou1 = ((tenkan+base)/2).iloc[:-26]
    senkou2 = ((h.rolling(window=52).max()+l.rolling(window=52).min())/2).iloc[:-26]

    df = pd.concat([tenkan, base, senkou1, senkou2],axis=1)
    df = df.rename(columns={0:'tenkan', 1:'base', 2:'senkou1', 3:'senkou2'})
    df.senkou1 =  df.senkou1.shift(26)
    df.senkou2 =  df.senkou2.shift(26)

    return df  # columns=['tenkan', 'base', 'senkou1', 'senkou2']

# ò®ó£ó¶
def DeviationRate(rate, indicator):
    DeviationRate = (rate - indicator)/indicator * 100
    return DeviationRate

    