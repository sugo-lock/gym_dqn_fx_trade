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
        self.leverage   = 25        # o25{
        self.spread     = 0.005     # XvbhÅè 0.005pips

        # `[gðÇÝÝ
        self.cols = ["YMD", "HM", "open", "high", "low", "close", "volume"]
        self.chart = pd.read_csv(PATH, names=self.cols )
        self.tick_num = 0
        self.tick = self.chart.iloc[self.tick_num]
        
        # CWP[^ðì¬
        # @25úÚ®½Ïü¨£¦
        df = mv_avrg(self.chart.close, window_size=25)
        self.chart['mv_avrg_div'] = DeviationRate(self.chart.close, df)
        
        # A14úRSI
        self.chart['RSI'] = rsi(self.chart.close, window_size=14)/100
        
        # BêÚÏt\¨£¦
        df = ichimoku(self.chart)
        self.chart['tenkan_div'] = DeviationRate(self.chart.close, df.tenkan)
        self.chart['base'] = DeviationRate(self.chart.close, df.base)
        self.chart['senkou1'] = DeviationRate(self.chart.close, df.senkou1)
        self.chart['senkou2'] = DeviationRate(self.chart.close, df.senkou2)
        
        # N{Ìtickðißé
        N = 100
        self.tick_num = N
        self.tick = self.chart.iloc[N]
        
        self.reset()

    def reset(self):
        self.tick = self.chart.iloc[0]
        self.tick_num = 0
        self.profit     = 0             # ¹v
        self.inprofit   = 0             # ÜÝ¹v
        self.trade_pos  = trade_pos()   # |WV

    # TickXV
    def update_tick(self):
        self.tick_num += 1
        if self.tick_num < len(self.chart.index):
            self.tick = self.chart.iloc[self.tick_num]
        self.calc_inprofit(self.tick.close)
                

    # ¶(/, [g, Ê)
    def order(self, dir, rate, amount):
        # dir ; ¶["BUY", "SELL"]
        # rate  : ¶¿i
        # amount: ¶

        # XvbhÅâ³
        if dir == "BUY":
            rate += self.spread
        elif dir == "SELL":
            rate -= self.spread

        # ¶ ~ obW
        amount = amount * 10000 * self.leverage

        # ¶(ñè)
         # @VK¢/VKè
        if self.trade_pos.amount == 0:
            self.trade_pos.average_cost = rate  # æ¾½Ï¿i = ¶¿i
            self.trade_pos.amount = amount      # ÛL     = ¶
            self.trade_pos.dir = dir
         # A¢µ/èµ
        elif self.trade_pos.dir == dir:
            if( self.trade_pos.amount + amount ) <= AMOUNT_MAX:
                self.trade_pos.average_cost = ( self.trade_pos.average_cost * self.trade_pos.amount + rate * amount )/(self.trade_pos.amount + amount) # æ¾½Ï¿iXV
                self.trade_pos.amount += amount     # ÛLXV
        # B½Î
        elif self.trade_pos.dir != dir:
            # êÏ
            if self.trade_pos.amount >= amount:                             # (ÛL  ¶)Ìê
                self.update_profit(rate, amount)                            # êm/ê¹Ø
                self.trade_pos.amount -= amount                             # ÛLXV
            # he¢/heè
            elif self.trade_pos.amount < amount:                            # (ÛL < ¶)Ìê
                self.update_profit(rate, self.trade_pos.amount)             # Sm/S¹Ø (+ VK¢/VKè)
                self.trade_pos.amount = amount - self.trade_pos.amount      # ÛLXV
                self.trade_pos.average_cost = rate                          # æ¾½Ï¿iXV
                self.trade_pos.dir = dir                                    # ½Î|WV

        if self.trade_pos.amount == 0:
            self.trade_pos.dir ="NANE"

    # ¹vXV
    def update_profit(self, rate, amount):
        if self.trade_pos.dir == "BUY":  # |WÌê
            self.profit += (rate - self.trade_pos.average_cost) * amount
        elif self.trade_pos.dir == "SELL":   # |WÌê
            self.profit -= (rate - self.trade_pos.average_cost) * amount

    # ÜÝ¹vvZ
    def calc_inprofit(self, rate):
        if self.trade_pos.dir == "SELL": # è|WÌê
            self.inprofit =-(rate - self.trade_pos.average_cost) * self.trade_pos.amount
        elif self.trade_pos.dir == "BUY":  # ¢|WÌê
            self.inprofit = (rate - self.trade_pos.average_cost) * self.trade_pos.amount
        else:
            self.inprofit = 0


if __name__ == "__main__":
    TS = trade_system()
    print(TS.chart[100:].head(5))
