# coding: utf-8
import sys

import pandas as pd
import numpy as np
import queue
import csv

from  .Technical_Indicators import mv_avrg, rsi, ichimoku, DeviationRate

PATH = './data/USDJPY1_20181016.csv'
AMOUNT_MAX = 1

class trade_pos():
    def __init__(self):
        self.dir = "NANE"
        self.average_cost = 0
        self.amount = 0

class trade_system():
    def __init__(self):
        self.leverage   = 25        # レバ25倍
        self.spread     = 0.005     # スプレッド固定 0.005pips

        # チャートを読み込み
        self.cols = ["YMD", "HM", "open", "high", "low", "close", "volume"]
        self.chart = pd.read_csv(PATH, names=self.cols )
        self.tick_num = 0
        self.tick = self.chart.iloc[self.tick_num]
        
        # インジケータを作成
        # ①25日移動平均線乖離率
        df = mv_avrg(self.chart.close, window_size=25)
        self.chart['mv_avrg_div'] = DeviationRate(self.chart.close, df)
        
        # ②14日RSI
        self.chart['RSI'] = rsi(self.chart.close, window_size=14)/100
        
        # ③一目均衡表乖離率
        df = ichimoku(self.chart)
        self.chart['tenkan_div'] = DeviationRate(self.chart.close, df.tenkan)
        self.chart['base'] = DeviationRate(self.chart.close, df.base)
        self.chart['senkou1'] = DeviationRate(self.chart.close, df.senkou1)
        self.chart['senkou2'] = DeviationRate(self.chart.close, df.senkou2)
        
        # N本のtickを進める
        N = 100
        self.tick_num = N
        self.tick = self.chart.iloc[N]
        
        self.reset()

    def reset(self):
        self.tick = self.chart.iloc[0]
        self.tick_num = 0
        self.profit     = 0             # 損益
        self.inprofit   = 0             # 含み損益
        self.trade_pos  = trade_pos()   # ポジション

    # Tick更新
    def update_tick(self):
        self.tick_num += 1
        if self.tick_num < len(self.chart.index):
            self.tick = self.chart.iloc[self.tick_num]
        self.calc_inprofit(self.tick.close)
                

    # 注文(買/売, レート, 量)
    def order(self, dir, rate, amount):
        # dir ; 注文["BUY", "SELL"]
        # rate  : 注文価格
        # amount: 注文枚数

        # スプレッドで補正
        if dir == "BUY":
            rate += self.spread
        elif dir == "SELL":
            rate -= self.spread

        # 注文枚数 × レバレッジ
        amount = amount * 10000 * self.leverage

        # 注文(約定)
         # ①新規買い/新規売り
        if self.trade_pos.amount == 0:
            self.trade_pos.average_cost = rate  # 取得平均価格 = 注文価格
            self.trade_pos.amount = amount      # 保有枚数     = 注文枚数
            self.trade_pos.dir = dir
         # ②買い増し/売り増し
        elif self.trade_pos.dir == dir:
            if( self.trade_pos.amount + amount ) <= AMOUNT_MAX:
                self.trade_pos.average_cost = ( self.trade_pos.average_cost * self.trade_pos.amount + rate * amount )/(self.trade_pos.amount + amount) # 取得平均価格更新
                self.trade_pos.amount += amount     # 保有枚数更新
        # ③反対売買
        elif self.trade_pos.dir != dir:
            # 一部決済
            if self.trade_pos.amount >= amount:                             # (保有枚数 ≧ 注文枚数)の場合
                self.update_profit(rate, amount)                            # 一部利確/一部損切
                self.trade_pos.amount -= amount                             # 保有枚数更新
            # ドテン買い/ドテン売り
            elif self.trade_pos.amount < amount:                            # (保有枚数 < 注文枚数)の場合
                self.update_profit(rate, self.trade_pos.amount)             # 全利確/全損切 (+ 新規買い/新規売り)
                self.trade_pos.amount = amount - self.trade_pos.amount      # 保有枚数更新
                self.trade_pos.average_cost = rate                          # 取得平均価格更新
                self.trade_pos.dir = dir                                    # 反対ポジション

        if self.trade_pos.amount == 0:
            self.trade_pos.dir ="NANE"

    # 損益更新
    def update_profit(self, rate, amount):
        if self.trade_pos.dir == "BUY":  # 買ポジの場合
            self.profit += (rate - self.trade_pos.average_cost) * amount
        elif self.trade_pos.dir == "SELL":   # 売ポジの場合
            self.profit -= (rate - self.trade_pos.average_cost) * amount

    # 含み損益計算
    def calc_inprofit(self, rate):
        if self.trade_pos.dir == "SELL": # 売りポジの場合
            self.inprofit =-(rate - self.trade_pos.average_cost) * self.trade_pos.amount
        elif self.trade_pos.dir == "BUY":  # 買いポジの場合
            self.inprofit = (rate - self.trade_pos.average_cost) * self.trade_pos.amount
        else:
            self.inprofit = 0


if __name__ == "__main__":
    TS = trade_system()
    print(TS.chart[100:].head(5))
