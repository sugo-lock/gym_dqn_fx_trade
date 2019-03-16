# coding: utf-8
import sys

import pandas as pd
import gym
import numpy as np
import gym.spaces
import csv

PATH = './data/USDJPY1_201810.csv'
AMOUNT_MAX = 1


class trade_pos():
    def __init__(self):
        self.dir = "NONE"
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

    def update_tick(self):
        self.now += 1
        if self.now < len(self.hist_data.index):
            self.tick_now = self.hist_data.iloc[self.now]

    # 注文
    def order(self, dir, rate, amount):
        # dir ; 注文["BUY", "SELL", "NONE"]
        # rate  : 注文価格
        # amount: 注文枚数
        if dir == "BUY":
            rate += self.spread
        elif dir == "SELL":
            rate -= self.spread

        amount = amount * 10000 * self.leverage
        if self.trade_pos.amount == 0:      # ①ポジション無しの場合
            self.trade_pos.average_cost = rate  # 取得平均価格 = 注文価格
            self.trade_pos.amount = amount      # 保有枚数     = 注文枚数
            self.trade_pos.dir = dir
        elif self.trade_pos.dir == dir:     # ②ポジションと売買方向が同じ場合
            if( self.trade_pos.amount + amount ) <= AMOUNT_MAX:
                self.trade_pos.average_cost = ( self.trade_pos.average_cost * self.trade_pos.amount + rate * amount )/(self.trade_pos.amount + amount) # 取得平均価格更新
                self.trade_pos.amount += amount     # 保有枚数更新
        elif self.trade_pos.dir != dir:     # ③ポジションと売買方向が異なる場合
            if self.trade_pos.amount >= amount: # (保有枚数 ≧ 注文枚数)の場合
                self.update_profit(dir, rate, amount)    # 一部利確
                self.trade_pos.amount -= amount           # 保有枚数更新
            elif self.trade_pos.amount < amount:  # (保有枚数 < 注文枚数)の場合
                self.update_profit(dir, rate, self.trade_pos.amount)        # 全利確
                self.trade_pos.amount = amount - self.trade_pos.amount      # 保有枚数更新
                self.trade_pos.average_cost = rate                          # 取得平均価格更新
                self.trade_pos.dir = dir                                    # 方向更新
    # 損益更新
    def update_profit(self, dir, rate, amount):
        self.profit_pre = self.profit
        if dir == "SELL":  # 売り注文の場合
            self.profit += (rate - self.trade_pos.average_cost) * amount
        elif dir == "BUY":   # 買い注文の場合
            self.profit -= (rate - self.trade_pos.average_cost) * amount
    # 含み損益計算
    def calc_inprofit(self, rate):
        self.inprofit_pre = self.inprofit
        if self.trade_pos.dir == "SELL": # 売りポジの場合
            self.inprofit = (rate - self.trade_pos.average_cost) * self.trade_pos.amount
        elif self.trade_pos.dir == "BUY":  # 買いポジの場合
            self.inprofit = (rate - self.trade_pos.average_cost) * self.trade_pos.amount



class trade(gym.Env):
    def __init__(self):
        super().__init__()
        # action_space, observation_space, reward_range を設定する
        self.action_space = gym.spaces.Discrete(3)  # トレーダーの行動の選択肢数
        self.observation_space = gym.spaces.Box(    
            low = 0.,          # 最小値
            high = 10000.,     # 最大値
            shape=(5,)         # 観測値
        )
        self.reward_range = [-500000., 500000.] # WIN or LOSE
        self.trade_sys = trade_system()
        self._reset()

    def _reset(self):
        # 諸々の変数を初期化する
        self.done = False
        self.trade_sys = trade_system()
        return self._observe()

    def _step(self, action):
        # 1ステップ進める処理を記述。戻り値は observation, reward, done(ゲーム終了したか), info(追加の情報の辞書)
        # ①レート取得
        rate = self.trade_sys.tick_now["rate_ed"]
        # ②トレードアクション実行( buy, sell, stay )
        if action == 0:
            self.trade_sys.order("BUY", rate, amount=AMOUNT_MAX)
        elif action == 1:
            self.trade_sys.order("SELL", rate, amount=AMOUNT_MAX)
        else:
            pass
        # ③tickを次へ
        self.trade_sys.update_tick()
        # ④含み益計算
        rate = self.trade_sys.tick_now["rate_ed"]
        self.trade_sys.calc_inprofit(rate)

        observation = self._observe()
        reward = self._get_reward()
        self.done = self._is_done()
        return observation, reward, self.done, {}

    def _render(self, mode='human', close=False):
        # human の場合はコンソールに出力。ansiの場合は StringIO を返す
        outfile = StringIO() if mode == 'ansi' else sys.stdout
        outfile.write( str(self.trade_sys.tick_now["rate_ed"])+"\t"+str(self.trade_sys.profit)+",\t"+str(self.trade_sys.inprofit)+'\n')
        return outfile

    def _close(self):
        pass

    def _seed(self, seed=None):
        pass

    def _get_reward(self):
        # 報酬を返す。
        reward = (self.trade_sys.profit - self.trade_sys.profit_pre) + (self.trade_sys.inprofit - self.trade_sys.inprofit_pre)
        return reward

    def _observe(self):
        rate_st = self.trade_sys.tick_now["rate_st"]
        rate_hi = self.trade_sys.tick_now["rate_hi"]
        rate_lo = self.trade_sys.tick_now["rate_lo"]
        rate_ed = self.trade_sys.tick_now["rate_ed"]
        production = self.trade_sys.tick_now["production"]
        observation = np.array([rate_st, rate_hi, rate_lo, rate_ed, production])
        return observation

    def _is_done(self):
         if self.trade_sys.now == (len(self.trade_sys.hist_data.index) - 1) :
             return True
         else:
             return False
