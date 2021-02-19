# -*- encoding:utf-8 -*-
from kuanke.user_space_api import *
import pandas as pd
import numpy as np

"""
普量学院量化投资课程系列案例源码包
普量学院版权所有
仅用于教学目的，严禁转发和用于盈利目的，违者必究
Plouto-Quants All Rights Reserved

普量学院助教微信：niuxiaomi3
"""

"""
信号统计
"""


class PL_MacdSignal:
    """
    触发的信号
    """

    def __init__(self, PL_code, PL_name, PL_period, PL_tm):
        """
        :param PL_code: 股票代码
        :param PL_name: 信号名称
        :param PL_period: 信号周期
        :param PL_tm: 触发信号的时间
        """
        self.code = PL_code
        self.name = PL_name
        self.period = PL_period
        self.tm = PL_tm


class PL_SignalStatistics:
    def __init__(self):
        pass

    @classmethod
    def PL_success_ratio(cls, PL_signals, PL_backtest_end_tm, PL_bar_idx_list):
        """
        :param PL_bar_idx_list: list类型。例如，[4,8,16]， 分别表示触发信号后第4根bar、第8根bar、第16根bar
        :param PL_backtest_end_tm: str类型， 回测结束日期。'2018-09-30 15:00:00'
        :param PL_signals: Signal类型，至少包含属性：code[股票代码], name[信号名称], tm[信号触发时间], period[信号周期]
        :return: 在投资研究页面，生成一个信号统计文件。统计项：触发信号后, M个bar内的胜率和赔率。最大支持100个bar
        """
        PL_df = cls.PL_calc_siganl_profit(PL_signals, PL_backtest_end_tm, PL_bar_idx_list)
        write_file('signals.csv', PL_df.to_csv(index=False), append=False)

        # 统计每种信号的成功率
        PL_signal_names = list(set(list(PL_df['signal_name'])))
        PL_signal_names.sort()

        PL_columns = [u"信号", u"触发次数", u"上涨次数", u"下跌次数",
                   u"上涨概率", u"下跌概率", u"平均涨跌幅",
                   u"上涨股票平均涨幅", u"下跌股票平均跌幅"]
        PL_temp = []
        for PL_idx in PL_bar_idx_list:
            PL_temp.append(['M=' + str(PL_idx)])
            PL_temp.append(PL_columns)
            for PL_name in PL_signal_names:
                row = cls.PL_success_ratio_of_single(PL_name, PL_df[PL_df['signal_name'] == PL_name], PL_idx)
                PL_temp.append(row)
            PL_temp.append([])
            PL_temp.append([])  # 追加两行空行
        write_file('signal_success_ratio.csv', pd.DataFrame(PL_temp).to_csv(index=False, header=False), append=False)

    @classmethod
    def PL_calc_siganl_profit(cls, PL_signals, PL_end_tm, PL_bar_idx_list):
        """
        计算所有信号m个bar内的涨跌幅
        :param PL_signals: list类型，所有的信号
        :param PL_end_tm: str类型， 统计截止时间
        :param PL_bar_idx_list:  list类型， 例如，[4,8,16]， 分别表示触发信号后第4根bar、第8根bar、第16根bar
        :return: DataFrame类型。包含：code/signal_name/period/chg_pct_1...chg_pct_m[从第1根bar到第n根bar的收益]
        """
        PL_columns = ['code', 'tm', 'signal_name', 'period']
        for PL_bar_idx in PL_bar_idx_list:
            PL_columns.append('chg_pct_' + str(PL_bar_idx))
        PL_signal_prifit_df = pd.DataFrame(columns=PL_columns)

        PL_count = 0
        for PL_signal in PL_signals:
            PL_tm = PL_signal.tm
            PL_code = PL_signal.code
            PL_df = get_price(PL_code, start_date=PL_tm, end_date=PL_end_tm, frequency=PL_signal.period, fields=['close'],
                           skip_paused=True, fq='pre')
            if PL_df.empty:
                continue
            PL_dfsize = len(PL_df)
            PL_temp = [PL_code, PL_tm, PL_signal.name, PL_signal.period]
            for PL_bar_idx in PL_bar_idx_list:
                PL_idx = PL_dfsize - 1 if PL_bar_idx >= PL_dfsize else PL_bar_idx
                PL_profit = (PL_df.iloc[PL_idx]['close'] - PL_df.iloc[0]['close']) / PL_df.iloc[0]['close']
                PL_temp.append(PL_profit)
            PL_signal_prifit_df.loc[str(PL_count)] = PL_temp
            PL_count += 1
        return PL_signal_prifit_df

    @classmethod
    def PL_success_ratio_of_single(cls, PL_name, PL_df, PL_bar_idx):
        """
        信号触发后第N个bar的胜率和赔率
        :param PL_name: str类型， 信号名称
        :param PL_df: Dataframe类型 所有名称相同的信号
        :param PL_bar_idx: int类型， 触发信号后的第几根bar
        :return: list类型：信号名称、信号触发次数、上涨次数、下跌次数、
                          上涨概率、下跌概率、平均涨跌幅、上涨平均涨幅、下跌平均跌幅
        """
        PL_pcol = 'chg_pct_' + str(PL_bar_idx)
        PL_rise = PL_df[PL_df[PL_pcol] > 0]
        PL_fall = PL_df[PL_df[PL_pcol] < 0]
        PL_rise_num = len(PL_rise)
        PL_fail_num = len(PL_fall)
        PL_rise_ratio = None
        PL_fall_ratio = None
        PL_trigger_num = len(PL_df)
        if PL_trigger_num > 0:
            PL_rise_ratio = cls.PL_to_per(float(PL_rise_num) / PL_trigger_num)
            PL_fall_ratio = cls.PL_to_per(float(PL_fail_num) / PL_trigger_num)

        return [PL_name, PL_trigger_num, PL_rise_num, PL_fail_num, PL_rise_ratio, PL_fall_ratio, cls.PL_to_per(PL_df[PL_pcol].mean()),
                cls.PL_to_per(PL_rise[PL_pcol].mean()), cls.PL_to_per(PL_fall[PL_pcol].mean())]

    @staticmethod
    def PL_to_per(PL_digits):
        if np.isnan(PL_digits) or PL_digits is None:
            return np.nan
        return '%.2f%%' % (PL_digits * 100)
