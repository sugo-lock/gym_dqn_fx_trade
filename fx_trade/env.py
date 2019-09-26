# coding: utf-8
import sys

import pandas as pd
import gym
import numpy as np
import gym.spaces
import csv
from . import trade_system

class trade(gym.Env):
    def __init__(self):
        super().__init__()
        # action_space, observation_space, reward_range を設定する
        self.action_space = gym.spaces.Discrete(3)  # トレーダーの行動の選択肢数[Buy, Sell, Stay]
        self.observation_space = gym.spaces.Box(    
            low = 0.,          # 最小値
            high = 10000.,     # 最大値
            shape=(6,)         # 観測値
        )
        self.reward_range = [-500000., 500000.] 
        self.trade_sys = trade_system.trade_system()
        self._reset()

    def _reset(self):
        # 諸々の変数を初期化する
        self.done = False
        self.trade_sys.reset()
        return self._observe()

    def _step(self, action):
        # 1ステップ進める処理を記述。戻り値は observation, reward, done(ゲーム終了したか), info(追加の情報の辞書)
        # ①レート取得
        rate = self.trade_sys.tick["close"]
        # ②トレードアクション実行( buy, sell, stay )
        if action == 0:
            self.trade_sys.order("BUY", rate, trade_system.AMOUNT_MAX)
        elif action == 1:
            self.trade_sys.order("SELL", rate, trade_system.AMOUNT_MAX)
        else:
            pass
        # ③tickを更新
        self.trade_sys.update_tick()

        observation = self._observe()
        reward = self._get_reward()
        self.done = self._is_done()
        return observation, reward, self.done, {}

    def _render(self, mode='human', close=False):
        # human の場合はコンソールに出力。ansiの場合は StringIO を返す
        outfile = StringIO() if mode == 'ansi' else sys.stdout
        close =  str("{0:.2f}".format(self.trade_sys.tick.close))
        profit =  str("{0:.2f}".format(self.trade_sys.profit))
        inprofit =  str("{0:.2f}".format(self.trade_sys.inprofit))
        dir = str(self.trade_sys.trade_pos.dir)
        outfile.write( close+'\t\t'+profit+'\t\t'+inprofit+'\t\t'+dir+'\n')
        return outfile

    def _close(self):
        pass

    def _seed(self, seed=None):
        pass

    def _get_reward(self):
        # 報酬を返す。
        reward = self.trade_sys.profit + self.trade_sys.inprofit
        self.reward_pre = reward
        return reward

    def _observe(self):
        cols = ['mv_avrg_div', 'RSI', 'tenkan_div', 'base', 'senkou1', 'senkou2']
        observation = np.array(self.trade_sys.tick[cols])
        return observation

class trade_train(trade):
    def _is_done(self):
        if self.trade_sys.tick_num == (len(self.trade_sys.chart.index) - 1) :
            return True
        else:
            return False

class trade_test(trade):
    def _is_done(self):
        if self.trade_sys.tick_num == (len(self.trade_sys.chart.index) - 1) :
            return True
