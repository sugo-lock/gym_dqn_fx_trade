# coding: utf-8
import sys

import pandas as pd
import numpy as np
import csv


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

        self.feature = ["ymd", "hm", "rate_st", "rate_hi", "rate_lo", "rate_ed", "production"]
        self.hist_data = pd.read_csv(PATH, names=self.feature )
        self.now = 0
        self.tick_now = self.hist_data.iloc[self.now]

        self.reset()

    def reset(self):
        self.profit     = 0         # 損益
        self.profit_pre = 0 
        self.inprofit       = 0         # 含み損益
        self.inprofit_pre   = 0
        self.trade_pos  = trade_pos()   # ポジション

    # Tick更新
    def update_tick(self):
        self.now += 1
        if self.now < len(self.hist_data.index):
            self.tick_now = self.hist_data.iloc[self.now]
        else:
            self.now = 0

    # 注文
    def order(self, dir, rate, amount):
        # dir ; 注文["BUY", "SELL"]
        # rate  : 注文価格
        # amount: 注文枚数

        # スプレッド考慮
        if dir == "BUY":
            rate += self.spread
        elif dir == "SELL":
            rate -= self.spread

        # レバレッジ
        amount = amount * 10000 * self.leverage

        # オーダー実行
         # ①ポジション無しの場合
        if self.trade_pos.amount == 0:
            self.trade_pos.average_cost = rate  # 取得平均価格 = 注文価格
            self.trade_pos.amount = amount      # 保有枚数     = 注文枚数
            self.trade_pos.dir = dir
         # ②ポジションと売買方向が同じ場合
        elif self.trade_pos.dir == dir:
            if( self.trade_pos.amount + amount ) <= AMOUNT_MAX:
                self.trade_pos.average_cost = ( self.trade_pos.average_cost * self.trade_pos.amount + rate * amount )/(self.trade_pos.amount + amount) # 取得平均価格更新
                self.trade_pos.amount += amount     # 保有枚数更新
         # ③ポジションと売買方向が異なる場合
        elif self.trade_pos.dir != dir:     
            if self.trade_pos.amount >= amount: # (保有枚数 ≧ 注文枚数)の場合
                self.update_profit(rate, amount)    # 一部利確
                self.trade_pos.amount -= amount           # 保有枚数更新
            elif self.trade_pos.amount < amount:  # (保有枚数 < 注文枚数)の場合
                self.update_profit(rate, self.trade_pos.amount)             # 全利確
                self.trade_pos.amount = amount - self.trade_pos.amount      # 保有枚数更新
                self.trade_pos.average_cost = rate                          # 取得平均価格更新
                self.trade_pos.dir = dir                                    # 方向更新

        if self.trade_pos.amount == 0:
            self.trade_pos.dir ="NANE"

    # 損益更新
    def update_profit(self, rate, amount):
        self.profit_pre = self.profit
        if self.trade_pos.dir == "BUY":  # 買ポジの場合
            self.profit += (rate - self.trade_pos.average_cost) * amount
        elif self.trade_pos.dir == "SELL":   # 売ポジの場合
            self.profit -= (rate - self.trade_pos.average_cost) * amount

    # 含み損益計算
    def calc_inprofit(self, rate):
        self.inprofit_pre = self.inprofit
        if self.trade_pos.dir == "SELL": # 売りポジの場合
            self.inprofit =-(rate - self.trade_pos.average_cost) * self.trade_pos.amount
        elif self.trade_pos.dir == "BUY":  # 買いポジの場合
            self.inprofit = (rate - self.trade_pos.average_cost) * self.trade_pos.amount
        else:
            self.inprofit = 0



