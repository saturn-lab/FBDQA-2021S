# -*- encoding:utf-8 -*-
import traceback
import pandas as pd
import numpy as np
from enum import Enum

"""
普量学院量化投资课程系列案例源码包
普量学院版权所有
仅用于教学目的，严禁转发和用于盈利目的，违者必究
Plouto-Quants All Rights Reserved

普量学院助教微信：niuxiaomi3
"""

"""
  MACD信号检测
  使用注意：先初始化MacdCache, 缓存历史数据
  包含以下几个类：
  - TOSTR                     实例转换成字符串
  - GoldCross                 金叉
  - DeathCross                死叉
  - CrossDetect               金叉死叉检测
  - MaxLimitDetect            最大值检测[相邻的金叉和死叉间的最大值]
  - MinLimitDetect            最小值检测[相邻的死叉和金叉间的最小值]
  - DivergenceType            背离的类型[顶背离、底背离]
  - Divergence                背离
  - DivergenceDetect          背离检测
  - TopDivergenceDetect       顶背离检测
  - BottomDivergenceDetect    底背离检测
  - Indicator                 macd指标检测, 包含：金叉、死叉、极值、背离
  - MacdCache                 缓存数据。
                                检测指标需要用到的数据：收盘价、dif、dea、macd
                                以及已经检测到的指标: 金叉、死叉、极值、背离
                                注意：背离只缓存最近一根bar触发的背离
"""

PL_environment = 'jukuan'
if PL_environment == 'jukuan':  # 设置回测环境-在聚宽上使用
    from kuanke.user_space_api import *  # 在自定义的类使用聚宽的接口，需要引入聚宽的API
    from PL_jukuan_macd_config import *  # 引入信号检测配置类。
    from PL_jukuan_db import PL_JukuanDBBase  # 引入获取数据的类。

    PL_DB_BASE = PL_JukuanDBBase  # 定义数据访问的实例。

__metaclass__ = type


class PL_TOSTR:
    """将实例转换成字符串，以方便输出到日志显示"""

    def PL_get_attr(self):
        """
        获取实例的所有属性
        :return:
        """
        return self.__dict__.items()

    def PL_to_json(self):
        """
        将实例转换成json字符串的形式。继承的子类实现
        """
        pass

    @staticmethod
    def PL_to_json_list(PL_obj_list):
        """
        将包含实例的数组转换成json字符串数组
        :param PL_obj_list:
        :return:
        """
        PL_dl = []
        for obj in PL_obj_list:
            if obj:
                PL_dl.append(obj.PL_to_json())
            else:
                PL_dl.append(None)
        return PL_dl


class PL_GoldCross:
    """
    定义金叉
    """

    def __init__(self):
        self.PL_cross_type = PL_GOLD

    @staticmethod
    def PL_is_cross(PL_pre_macd, PL_macd):
        """
        判断是否金叉
        :param PL_pre_macd: 前一个bar的macd
        :param PL_macd: 当前bar的macd
        :return:
        """
        return PL_pre_macd <= 0 < PL_macd


class PL_DeathCross:
    """
    定义死叉
    """

    def __init__(self):
        self.PL_cross_type = PL_DEATH

    @staticmethod
    def PL_is_cross(PL_pre_macd, PL_macd):
        """
        判断是否死叉
        :param PL_pre_macd: 前一个bar的macd
        :param PL_macd: 当前bar的macd
        :return:
        """
        return PL_pre_macd >= 0 > PL_macd


class PL_CrossDetect:
    """
    检测金叉死叉
    """

    @staticmethod
    def PL_is_cross(PL_df, PL_cross):
        """
        检测最后一根bar是不是定义的交叉类型
        :param PL_df: DataFrame类型。缓存的数据，最后一条记录是待检测的bar
        :param PL_cross: 金叉或死叉
        :return:
        """
        if PL_df.empty or len(PL_df) == 1:
            return False
        PL_row = PL_df.iloc[-1]
        PL_pre_row = PL_df.iloc[-2]
        if not PL_cross.PL_is_cross(PL_pre_row[PL_MACD], PL_row[PL_MACD]):
            log.debug(u'【%s】没有穿过, macd=%s, pre_macd=%s' % (PL_row.name, PL_row[PL_MACD], PL_pre_row[PL_MACD]))
            return False
        return True


class PL_MaxLimitDetect:
    """
     检测极值：最大值的时间。用于检测3种极值的时间，3种极值分别是：DIF/CLOSE/MACD
    """

    @classmethod
    def PL_get_close_limit_tm_in(cls, PL_df):
        """
        获取区间内CLOSE最大值对应的时间。
        :param PL_df: DataFrame类型， 相邻的金叉和死叉之间或两个金叉之间的所有数据[包含金叉点，不包含死叉点]
        :return:
        """
        PL_limit = PL_df[PL_CLOSE].max()
        if PL_limit > 0:
            # 必须是一个有效的价格
            return cls.PL___get_max_limit_tm(PL_df[PL_CLOSE], PL_limit)

    @classmethod
    def PL_get_dif_limit_tm_in(cls, PL_df):
        """
        获取区间内DIF最大值对应的时间。
        :param PL_df: DataFrame类型， 相邻的金叉和死叉之间或两个金叉之间的所有数据[包含金叉点，不包含死叉点]
        :return:
        """
        PL_limit = PL_df[PL_DIF].max()
        if PL_limit > 0:
            # 要求当前区间内的最大值必须在零轴上。
            return cls.PL___get_max_limit_tm(PL_df[PL_DIF], PL_limit)

    @classmethod
    def PL_get_macd_limit_tm_in(cls, PL_df):
        """
        获取区间内MACD最大值对应的时间。
        :param PL_df: DataFrame类型， 相邻的金叉和死叉之间或两个金叉之间的所有数据[包含金叉点，不包含死叉点]
        :return:
        """
        PL_limit = PL_df[PL_MACD].max()
        if PL_limit > 0:
            # 要求当前区间内的最大值必须是红柱。
            return cls.PL___get_max_limit_tm(PL_df[PL_MACD], PL_limit)

    @staticmethod
    def PL___get_max_limit_tm(PL_series, PL_limit):
        """
        获取series连续区间内的最大值所对应的时间。
        不同的数据源，累计的分钟级别close可能会不同，根据close计算的dif、macd也会不同，
        为了降低对于极值点的敏感度, 取所有与limit接近的值作为候选的极值点。
        存在多个候选的极值点时，取离当前交叉点最近的一个作为极值点。
        :param PL_series: 时间序列数据, Series类型。
        :param PL_limit: 当前区间内的最大值
        :return: 最大值的时间
        """
        # 所有候选的极值点
        PL_limits = PL_series[PL_series >= PL_limit * PL_LIMIT_DETECT_LIMIT_FACTOR]
        if not PL_limits.empty:
            PL_tm = PL_limits.index[-1]
            return PL_tm


class PL_MinLimitDetect:
    """
    检测极值：最小值的时间。用于检测3种极值的时间，3种极值分别是：DIF/CLOSE/MACD
    """

    @classmethod
    def PL_get_close_limit_tm_in(cls, PL_df):
        """
        获取区间内close最小值的时间。
        :param PL_df: DataFrame类型， 相邻的死叉和金叉之间或两个死叉之间的所有数据[包含死叉点，不包含金叉点]
        :return:
        """
        PL_limit = PL_df[PL_CLOSE].min()
        if PL_limit > 0:
            # 必须是一个有效的价格。
            PL_limit_df = PL_df[PL_df[PL_CLOSE] <= PL_limit * (2 - PL_LIMIT_DETECT_LIMIT_FACTOR)]
            if not PL_limit_df.empty:
                PL_tm = PL_limit_df.index[-1]
                return PL_tm

    @classmethod
    def PL_get_dif_limit_tm_in(cls, PL_df):
        """
        获取区间内DIF最小值的时间。
        :param PL_df: DataFrame类型， 相邻的死叉和金叉之间或两个死叉之间的所有数据[包含死叉点，不包含金叉点]
        :return:
        """
        PL_limit = PL_df[PL_DIF].min()
        if PL_limit < 0:
            # 要求当前区间内的最小值必须在零轴下。
            return cls.PL___get_min_limit_tm(PL_df[PL_DIF], PL_limit)

    @classmethod
    def PL_get_macd_limit_tm_in(cls, PL_df):
        """
        获取区间内MACD最大值的时间。
        :param PL_df: DataFrame类型， 相邻的死叉和金叉之间或两个死叉之间的所有数据[包含死叉点，不包含金叉点]
        :return:
        """
        PL_limit = PL_df[PL_MACD].min()
        if PL_limit < 0:
            # 要求当前区间内的最小值必须是绿柱。
            return cls.PL___get_min_limit_tm(PL_df[PL_MACD], PL_limit)

    @staticmethod
    def PL___get_min_limit_tm(PL_series, PL_limit):
        """
        获取series连续区间内的最小值的时间。
        不同的数据源，累计的分钟级别close可能会不同，根据close计算的dif、macd也会不同，
        为了降低对于极值点的敏感度, 取所有与limit接近的值作为候选的极值点。
        存在多个候选的极值点时，取离当前交叉点最近的一个作为极值点。
        :param PL_series: 时间序列数据, Series类型。
        :param PL_limit: 当前区间内的最大值
        :return: 最大值的时间
        """
        # 所有候选的极值点
        PL_limits = PL_series[PL_series <= PL_limit * PL_LIMIT_DETECT_LIMIT_FACTOR]
        if not PL_limits.empty:
            PL_tm = PL_limits.index[-1]
            return PL_tm


class PL_DivergenceType(Enum):
    """
    定义背离的类型
    """
    Top = 'TOP'  # 顶背离
    Bottom = 'BOTTOM'  # 底背离


class PL_Divergence(PL_TOSTR):
    """
    背离
    """

    def __init__(self, PL_divergence_type=None, PL_pre_dif_limit_tm=None, PL_last_dif_limit_tm=None, PL_significance=None):
        self.PL_divergence_type = PL_divergence_type
        self.PL_pre_dif_limit_tm = PL_pre_dif_limit_tm
        self.PL_last_dif_limit_tm = PL_last_dif_limit_tm
        self.PL_significance = PL_significance  # 背离的可见度

    def PL_to_json(self):
        return {
            'type': self.PL_divergence_type,
            'pre_dif_limit_tm': str(self.PL_pre_dif_limit_tm),
            'last_dif_limit_tm': str(self.PL_last_dif_limit_tm),
            'significance': self.PL_significance
        }


class PL_DivergenceDetect:
    """
    检测背离
    """

    def __init__(self):
        self.PL_most_limit_num = PL_DIVERGENCE_DETECT_MOST_LIMIT_NUM  # 最大允许在几个相邻的极值点检测背离。
        self.PL_significance = PL_DIVERGENCE_DETECT_SIGNIFICANCE  # 背离的可见度
        self.PL_dif_limit_bar_num = PL_DIVERGENCE_DETECT_DIF_LIMIT_BAR_NUM  # bar的数量。往前追溯多少个bar计算dif最大值
        self.PL_dif_limit_factor = PL_DIVERGENCE_DETECT_DIF_LIMIT_FACTOR  # dif极值的调节因子。
        self.PL_cross_type = None  # 交叉点的类型[金叉或死叉]
        self.PL_divergence_type = None  # 背离的类型[顶背离或底背离]

    def PL_is_valid_by_zero_axis(self, PL_dif, PL_pre_dif):
        """
        验证两个极值点的dif与零轴的关系，是否满足背离要求。具体的验证方法由子类实现
        :param PL_dif:
        :param PL_pre_dif:
        :return:
        """
        pass

    def PL_is_valid_by_close_and_dif(self, PL_close, PL_pre_close, PL_dif, PL_pre_dif):
        """
        验证两个极值点的dif和close，是否满足背离要求。具体的验证方法由子类实现
        :param PL_close:
        :param PL_pre_close:
        :param PL_dif:
        :param PL_pre_dif:
        :return:
        """
        pass

    def PL_get_divergences(self, PL_df):
        """
        检测最近一个bar是否发生背离
        :param PL_df: DataFrame类型，至少包含以下列：CLOSE、DIF、MACD、是否金叉、是否死叉、
                   以及根据交叉点检测到的3种极值的时间，DIF极值时间、MACD极值时间、收盘价极值时间
        :return: 背离
        """
        PL_divergences = []
        PL_row = PL_df.iloc[-1]

        if not self.PL_cross_type or not PL_row[self.PL_cross_type]:
            return PL_divergences
        PL_cdf = PL_df[PL_df[self.PL_cross_type].notnull()]

        PL_cdf = PL_cdf[PL_cdf[self.PL_cross_type]].iloc[-self.PL_most_limit_num:]  # 相邻的2个金叉点
        if len(PL_cdf) <= 1:  # 只找到一个极值点
            log.debug(u'【%s, %s】只有一个极值点, dif_limit_tm=%s' % (PL_row.name, self.PL_cross_type, PL_row[PL_DIF_LIMIT_TM]))
            return PL_divergences

        PL_dif, PL_close, PL_macd = self.PL_get_limit_by_cross(PL_df, PL_row)
        if PL_dif is None or PL_close is None or PL_macd is None:
            log.debug(
                u'【%s, %s】未找到穿越前的极值, dif_limit_tm=%s' % (PL_row.name, self.PL_cross_type, PL_row[PL_DIF_LIMIT_TM]))
            return PL_divergences

        for i in range(len(PL_cdf) - 2, -1, -1):
            PL_pre_cross = PL_cdf.iloc[i]
            PL_pre_dif, PL_pre_close, PL_pre_macd = self.PL_get_limit_by_cross(PL_df, PL_pre_cross)
            if PL_pre_dif is None or PL_pre_close is None or PL_pre_macd is None:
                log.debug(u'【%s, %s】未找到前一个背离点的极值, dif_limit_tm=%s' % (PL_row.name, self.PL_cross_type, PL_row[PL_DIF_LIMIT_TM]))
                continue

            # 分别对比两个点的价格以及dif的高低关系.顶背离：价格创新高，dif没有创新高，底背离：价格创新低，dif没有创新低
            if not self.PL_is_valid_by_close_and_dif(PL_close[PL_CLOSE], PL_pre_close[PL_CLOSE], PL_dif[PL_DIF],PL_pre_dif[PL_DIF]):
                log.debug(
                    u'【%s, %s】极值点价格和DIF分别比较, dif_limit_tm=%s, dif=%s, close_limit_tm=%s, close=%s, pre_dif_tm=%s, pre_dif=%s, pre_close_limit_tm=%s, pre_close=%s' % (
                        PL_row.name, self.PL_cross_type, PL_dif.name, PL_dif[PL_DIF], PL_close.name, PL_close[PL_CLOSE],
                        PL_pre_dif.name, PL_pre_dif[PL_DIF], PL_pre_close.name, PL_pre_close[PL_CLOSE]))
                continue

            # 解决DIF和DEA纠缠的问题：要求两个背离点对应的macd值不能太小。
            PL_ldf = PL_df[PL_df.index <= PL_dif.name]  # dif极值点之前的数据[包含dif极值点]
            if not self.PL_is_tangle_by_dea_and_dif(PL_macd, PL_pre_macd, PL_ldf[PL_MACD]):
                log.debug(
                    u'【%s, %s】纠缠, dif_limit_tm=%s, dif=%s, macd_limit_tm=%s, macd=%s, pre_dif_limit_tm=%s, pre_dif=%s, pre_macd_limit_tm=%s, pre_macd=%s' % (
                        PL_row.name, self.PL_cross_type, PL_dif.name, PL_dif[PL_DIF], PL_macd.name, PL_macd[PL_MACD],
                        PL_pre_dif.name, PL_pre_dif[PL_DIF], PL_pre_macd.name, PL_pre_macd[PL_MACD]))
                continue

            # 对背离点高度的要求：
            if not self.PL_is_valid_by_dif_max(PL_ldf[PL_DIF], PL_dif[PL_DIF], PL_pre_dif[PL_DIF]):
                log.debug(u'【%s, %s】背离点高度检测, dif_limit_tm=%s, dif=%s, pre_dif_limit_tm=%s, pre_dif=%s' % (
                    PL_row.name, self.PL_cross_type, PL_dif.name, PL_dif[PL_DIF], PL_pre_dif.name, PL_pre_dif[PL_DIF]))
                continue

            # DIF和价格的差，至少有一个比较显著才能算显著背离。
            # 判断方法：(DIF极值涨跌幅的绝对值+价格极值涨跌幅的绝对值) > self.significance
            PL_significance = self.PL_calc_significance_of_divergence(PL_dif, PL_close, PL_pre_dif, PL_pre_close)
            if self.PL_significance is not None and PL_significance <= self.PL_significance:
                log.debug(
                    u'【%s, %s】显著背离检测, dif_limit_tm=%s, pre_dif_limit_tm=%s, significance=%s' % (
                        PL_row.name, self.PL_cross_type, PL_dif.name, PL_pre_dif.name, PL_significance))
                continue

            PL_divergences.append(
                PL_Divergence(self.PL_divergence_type, PL_pre_dif_limit_tm=PL_pre_cross[PL_DIF_LIMIT_TM],
                              PL_last_dif_limit_tm=PL_row[PL_DIF_LIMIT_TM],
                              PL_significance=PL_significance))
        return PL_divergences

    def PL_is_valid_by_dif_max(self, PL_dif_series, PL_dif, PL_pre_dif):
        """
        判断是不是最大值
        采用过去250个bar内极值的最大值的绝对值作为参考，
        背离点中必须至少有一个极值的绝对值大于阈值dif_max[绝对值的最大值*dif_limit_factor]。
        :param PL_dif_series:
        :param PL_dif:
        :param PL_pre_dif:
        :return:
        """
        PL_dif_max = self.PL_get_abs_max(PL_dif_series, self.PL_dif_limit_bar_num) * self.PL_dif_limit_factor
        if not np.isnan(PL_dif_max) and (abs(PL_dif) < PL_dif_max and abs(PL_pre_dif) < PL_dif_max):
            return False
        return True

    @staticmethod
    def PL_get_limit_by_cross(PL_df, PL_row):
        PL_dif_limit_tm, PL_close_limit_tm, PL_macd_limit_tm = PL_row[PL_DIF_LIMIT_TM], PL_row[PL_CLOSE_LIMIT_TM], PL_row[PL_MACD_LIMIT_TM]
        try:
            PL_dif = PL_df.loc[PL_dif_limit_tm]  # 交叉点对应的DIF极值
            PL_close = PL_df.loc[PL_close_limit_tm]  # 交叉点对应的价格极值
            PL_macd = PL_df.loc[PL_macd_limit_tm]  # 交叉点对应的macd极值
            return PL_dif, PL_close, PL_macd
        except:
            log.debug(u'【%s】获取极值为空' % PL_row.name)
            return None, None, None

    @staticmethod
    def PL_get_abs_max(PL_series, PL_num):
        """
        获取近num个bar内，绝对值的最大值
        :param PL_series: Series类型
        :param PL_num: 数量。最近多少个bar内计算最大值
        :return:
        """
        PL_ser = PL_series.iloc[-PL_num:]
        PL_max_val = np.nanmax(PL_ser)
        PL_min_val = np.nanmin(PL_ser)
        return np.nanmax([abs(PL_max_val), abs(PL_min_val)])

    def PL_is_tangle_by_dea_and_dif(self, PL_macd, PL_pre_macd, PL_macd_ser):
        """
        判断dif和dea是否纠缠, 解决DIF和DEA纠缠在一起的问题：要求两个背离点对应的macd值不能太小。
        必须同时满足以下条件：
            1)abs(macd/pre_macd)>0.3
            2)max([abs(macd), abs(pre_macd)])/macd_max > 0.5

        :param PL_macd: 当前bar的MACD值
        :param PL_pre_macd: 前一个bar的MACD值
        :param PL_macd_ser: Series类型，MACD的时间序列数据
        :return: 是-纠缠， 否-不纠缠
        """
        if abs(PL_macd[PL_MACD] / PL_pre_macd[PL_MACD]) <= 0.3:
            log.debug(u'【%s, %s】MACD、MACD_PRE纠缠, %s, %s' % (PL_macd.name, PL_pre_macd.name, PL_macd[PL_MACD], PL_pre_macd[PL_MACD]))
            return False
        PL_macd_max = abs(self.PL_get_abs_max(PL_macd_ser, 250)) * 0.5
        if max([abs(PL_macd[PL_MACD]), abs(PL_pre_macd[PL_MACD])]) <= PL_macd_max:
            log.debug(
                u'【%s, %s】与最大值相比，发生纠缠, %s, %s, %s' % (PL_macd.name, PL_pre_macd.name, PL_macd[PL_MACD], PL_pre_macd[PL_MACD], PL_macd_max))
            return False
        return True

    @staticmethod
    def PL_calc_significance_of_divergence(PL_dif, PL_close, PL_pre_dif, PL_pre_close):
        """
        检测是不是明显的背离： DIF和价格的差，至少有一个比较显著才能算显著背离。
        判断方法：DIF涨跌幅的绝对值+价格涨跌幅的绝对值>阈值
        :param PL_dif: 当前bar的数据，Series类型，至少包含DIF
        :param PL_close: 当前bar的数据，Series类型，至少包含CLOSE
        :param PL_pre_dif: 前一个bar的数据，Series类型，至少包含DIF
        :param PL_pre_close:前一个bar的数据，Series类型，至少包含CLOSE
        :return: True-是显著背离 False-不是显著背离
        """
        return abs((PL_dif[PL_DIF] - PL_pre_dif[PL_DIF]) / PL_pre_dif[PL_DIF]) + abs(PL_close[PL_CLOSE] - PL_pre_close[PL_CLOSE]) / PL_pre_close[PL_CLOSE]

    def PL___larger_than(self, PL_val1, PL_val2):
        """
        判断val1是否大于val2。由子类实现
        """
        pass


class PL_TopDivergenceDetect(PL_DivergenceDetect):
    """
        检测顶背离：价格创新高， DIF没有创新高
    """

    def __init__(self):
        super(PL_TopDivergenceDetect, self).__init__()
        self.PL_divergence_type = PL_DivergenceType.Top
        self.PL_cross_type = PL_DEATH  # 根据死叉往前找顶背离

    def PL_is_valid_by_zero_axis(self, PL_dif, PL_pre_dif):
        """
        判断两个dif极值点是否都在0轴以上
        :param PL_dif:当前bar的dif值
        :param PL_pre_dif:前一个bar的dif值
        :return:
        """
        return PL_dif > 0 and PL_pre_dif > 0

    def PL_is_valid_by_close_and_dif(self, PL_close, PL_pre_close, PL_dif, PL_pre_dif):
        """
        判断是否满足价格创新高， DIF没有创新高。
        :param PL_close:
        :param PL_pre_close:
        :param PL_dif:
        :param PL_pre_dif:
        :return:
        """
        return PL_pre_close < PL_close and PL_pre_dif >= PL_dif

    def PL___larger_than(self, PL_val1, PL_val2):
        """
        判断val1是不是高于val2
        :param PL_val1:
        :param PL_val2:
        :return:
        """
        return PL_val1 > PL_val2


class PL_BottomDivergenceDetect(PL_DivergenceDetect):
    """
        检测底背离：价格创新低， DIF没有创新低
    """

    def __init__(self):
        super(PL_BottomDivergenceDetect, self).__init__()
        self.PL_divergence_type = PL_DivergenceType.Bottom
        self.PL_cross_type = PL_GOLD  # 根据金叉往前找底背离

    def PL_is_valid_by_zero_axis(self, PL_dif, PL_pre_dif):
        """
        判断两个dif极值点是否都在0轴以下
        :param PL_dif:当前bar的dif值
        :param PL_pre_dif:前一个bar的dif值
        :return:
        """
        return PL_dif < 0 and PL_pre_dif < 0

    def PL_is_valid_by_close_and_dif(self, PL_close, PL_pre_close, PL_dif, PL_pre_dif):
        """
        判断是否满足价格创新低， DIF没有创新低。
        :param PL_close:
        :param PL_pre_close:
        :param PL_dif:
        :param PL_pre_dif:
        :return:
        """
        return PL_pre_close > PL_close and PL_pre_dif <= PL_dif

    def PL___larger_than(self, PL_val1, PL_val2):
        """判断val1是不是低于val2"""
        return PL_val1 < PL_val2


class PL_Indicator:
    """
    检测MACD指标
    """

    def __init__(self):
        self.PL_min_limit_detect = PL_MinLimitDetect
        self.PL_max_limit_detect = PL_MaxLimitDetect
        self.PL_top_detect = PL_TopDivergenceDetect()
        self.PL_bottom_detect = PL_BottomDivergenceDetect()
        self.PL_cross_detect = PL_CrossDetect()

    def PL_last_cross(self, PL_df, PL_idx):
        """
        检测索引为idx的bar,检测是否触发金叉或死叉，并且设置这根bar的金叉、死叉的值
        :param PL_df: DataFrame类型。时间序列为索引
        :param PL_idx: 位置。df的每一行的位置编号
        :return:
        """
        PL_gold, PL_death = False, False
        PL_tm = PL_df.iloc[PL_idx].name
        PL_cross_df = PL_df[PL_df.index <= PL_tm]
        PL_gold = self.PL_cross_detect.PL_is_cross(PL_cross_df, PL_GoldCross)
        if not PL_gold:
            PL_death = self.PL_cross_detect.PL_is_cross(PL_cross_df, PL_DeathCross)
        PL_df.loc[PL_tm, [PL_GOLD, PL_DEATH]] = PL_gold, PL_death

    def PL_last_limit_point_tm(self, PL_df, PL_idx):
        """
        检测索引为idx的bar, 如果这个bar发生了金叉或死叉，根据交叉点查找3种极值[MACD，CLOSE, DIF]，并在当前bar，记录极值产生的时间
        :param PL_df:
        :param PL_idx:
        :return:
        """
        PL_row = PL_df.iloc[PL_idx]
        PL_tm = PL_row.name
        if PL_row[PL_GOLD]:
            # 如果当前bar触发金叉，往前检测MinLimit
            PL_dif_limit_tm, PL_close_limit_tm, PL_macd_limit_tm = self.PL_get_limit_before_cross(PL_df, PL_tm,PL_DEATH,
                                                                                                  self.PL_min_limit_detect)
        elif PL_row[PL_DEATH]:
            # 如果当前bar触发死叉， 往前检测MaxLimit
            PL_dif_limit_tm, PL_close_limit_tm, PL_macd_limit_tm = self.PL_get_limit_before_cross(PL_df, PL_tm, PL_GOLD,
                                                                                                  self.PL_max_limit_detect)
        else:
            PL_dif_limit_tm, PL_close_limit_tm, PL_macd_limit_tm = None, None, None

        # 在当前bar对应的数据结构中，记录以下3个极值点的时间：dif极值点、价格极值点、macd极值点
        PL_df.loc[PL_tm, [PL_DIF_LIMIT_TM, PL_CLOSE_LIMIT_TM,
                          PL_MACD_LIMIT_TM]] = PL_dif_limit_tm, PL_close_limit_tm, PL_macd_limit_tm

    def PL_get_last_divergences(self, PL_df):
        """
        检测最近一个bar,是否发生顶背离或底背离
        :param PL_df:
        :return:
        """
        PL_divergences = self.PL_bottom_detect.PL_get_divergences(PL_df)
        PL_divergences += self.PL_top_detect.PL_get_divergences(PL_df)
        return PL_divergences

    def PL_get_limit_before_cross(self, PL_df, PL_current_bar_tm, PL_pre_cross_type, PL_limit_detect):
        """
        获取三种极值的时间[MACD，CLOSE, DIF]
        :param PL_df: DataFrame类型
        :param PL_current_bar_tm: 当前bar的时间
        :param PL_pre_cross_type: 前一个交叉点的类型
        :param PL_limit_detect: 检测极值的类
        :return:
        """
        PL_pre_cross_tm = self.PL_get_pre_cross_tm(PL_df, PL_current_bar_tm, PL_pre_cross_type)

        if not PL_pre_cross_tm:
            PL_limit_df = PL_df[(PL_df.index < PL_current_bar_tm)]  # 检测极值的区间不能包含当前穿越点，可以包含前一个穿越点
        else:
            PL_limit_df = PL_df[(PL_df.index < PL_current_bar_tm) & (PL_df.index >= PL_pre_cross_tm)]
        if PL_limit_df.empty:
            return None, None, None
        log.debug(u'[%s,%s]穿越点' % (PL_current_bar_tm, PL_pre_cross_tm))
        PL_dif_limit_tm = PL_limit_detect.PL_get_dif_limit_tm_in(PL_limit_df)
        PL_close_limit_tm = PL_limit_detect.PL_get_close_limit_tm_in(PL_limit_df)
        PL_macd_limit_tm = PL_limit_detect.PL_get_macd_limit_tm_in(PL_limit_df)
        return PL_dif_limit_tm, PL_close_limit_tm, PL_macd_limit_tm

    @staticmethod
    def PL_get_pre_cross_tm(PL_df, PL_cross_tm, PL_pre_cross_type):
        """
        获取dif和dea前一个交叉点的时间
        :param PL_df: DataFrame类型
        :param PL_cross_tm: 交叉的时间
        :param PL_pre_cross_type: 前一次交叉的类型[金叉或死叉]
        :return:
        """
        PL_cross_df = PL_df[(PL_df.index < PL_cross_tm) & (PL_df[PL_pre_cross_type])]
        if PL_cross_df.empty:
            return None
        else:
            return PL_cross_df.index[-1]

    @staticmethod
    def PL_macd(PL_df):
        """
        计算MACD的三个指标：DIFF, DEA, MACD
        DIFF=今日EMA（12）- 今日EMA（26）
        MACD= (DIFF－DEA)*2
        :param PL_df:
        :return: 补充dif,dea,macd计算结果
        """
        PL_close = PL_df[PL_CLOSE]
        if pd.__version__ >= "0.18.0":
            PL_dif = PL_close.ewm(span=PL_SHORT).mean() - PL_close.ewm(span=PL_LONG).mean()
            PL_dea = PL_dif.ewm(span=PL_MID).mean()
        else:
            # 聚宽使用的pandas库版本比较低
            PL_dif = pd.ewma(PL_close, span=PL_SHORT) - pd.ewma(PL_close, span=PL_LONG)
            PL_dea = pd.ewma(PL_dif, span=PL_MID)
        PL_macd = (PL_dif - PL_dea) * 2
        PL_df[PL_DIF], PL_df[PL_DEA], PL_df[PL_MACD] = PL_dif, PL_dea, PL_macd


class PL_MacdCache:
    """
    macd缓存：缓存历史数据，用于检测金叉、死叉、背离。缓存的数据包含以下几项：
        - bars:dict类型, key-股票代码, value-DataFrame类型,包含的列:
            - close[收盘价]/dif/dea/macd
            - gold[是否金叉]/death[是否死叉]
            - dif_limit_tm[dif极值的时间]
            - close_limit_tm[收盘价极值的时间]
            - macd_limit_tm[macd极值的时间]
            注：触发金叉或死叉后，以当前交叉点往前检测寻找价格、DIF、MACD极值点。并记录极值的时间
        - divergences: dict类型， key-股票代码， value - 触发的背离，包含顶背离和底背离, 只缓存最新一根bar触发的背离
    """

    def __init__(self, PL_period, PL_init_tm, PL_count=500, PL_stocks=None):
        self.PL_dbkline = PL_DB_BASE()  # 数据查询接口
        self.PL_indicator = PL_Indicator()  # macd指标检测接口
        self.PL_period = PL_period  # 指标检测的时间周期
        if not PL_init_tm:  # 初始化时间
            raise Exception(u'【macd缓存初始化异常】:init_tm is null')
        self.PL_init_tm = PL_init_tm
        self.PL_bar_cache_num = PL_count  # 数量. 缓存多少个bar的检测结果
        if not PL_stocks:
            PL_stocks = []
        self.PL_stocks = PL_stocks
        self.PL_bar_cache_cols = PL_COLS
        self.PL_bars = {}
        self.PL_divergences = {}  # 当前收盘后触发的背离
        self.PL___init_cache()

    def PL___init_cache(self):
        """
        如果股票池不为空，初始化后就开始缓存股票池的数据
        :return:
        """
        for code in self.PL_stocks:
            try:
                self.PL___init_single_cache(code, self.PL_init_tm)
                log.debug(u'【macd缓存初始化end】code={}, init_tm={}'.format(code, self.PL_init_tm))
            except:
                log.debug(u'【macd缓存初始化】异常：code={}, exception={}'.format(code, traceback.format_exc()))

    def PL___init_single_cache(self, PL_code, PL_init_tm):
        """
        初始化单支股票的缓存
        :param PL_code:
        :param PL_init_tm:
        :return:
        """
        PL_df = self.PL_dbkline.PL_get_bars(PL_code, PL_count=self.PL_bar_cache_num + PL_EXTRA_LOAD_BAR_NUM, PL_unit=self.PL_period,
                                         PL_fields=[PL_CLOSE],
                                         PL_end_tm=PL_init_tm)
        if PL_df.empty:
            log.debug(u'【macd缓存初始化】警告：code={},  bars empty'.format(PL_code))
            return

        self.PL_supply_cols(PL_df, self.PL_bar_cache_cols)
        self.PL_indicator.PL_macd(PL_df)
        for idx in range(0, len(PL_df)):
            self.PL_update_last_bar_single_stock(PL_df, PL_code, idx, self.PL_indicator)

    def PL_update_last_bar_single_stock(self, PL_df, PL_code, PL_idx, PL_indicator):
        """
        更新单支股票的缓存数据
        :param PL_df: 缓存的bar
        :param PL_code: str类型。股票代码
        :param PL_idx: int类型。bar的位置。当前需要更新的bar,在df中的位置。
        :param PL_indicator: Indicator类型。 用于指标计算以信号检测的实例。
        :return:
        """
        PL_indicator.PL_last_cross(PL_df, PL_idx)  # 记录idx位置的bar是否发生金叉死叉
        PL_indicator.PL_last_limit_point_tm(PL_df, PL_idx)  # 记录极值点
        self.PL_bars[PL_code] = PL_df

        PL_row = PL_df.iloc[PL_idx]
        PL_tm = PL_row.name
        if PL_df.iloc[-1].name == PL_tm:  # 初始化缓存数据的时候：历史数据不检测背离
            self.PL_update_divergences(PL_df.iloc[:PL_idx + 1], PL_code)

        PL_divergences = self.PL_divergences[PL_code] if PL_code in self.PL_divergences.keys() else []
        log.debug(u'【%s, %s】MACD更新完成, row=%s, divergences=%s' % (PL_code, PL_tm, PL_row.to_dict(),
                                                                 PL_Divergence.PL_to_json_list(PL_divergences)))

    def PL_update_cache(self, PL_last_tm=None):
        """
        指定当前时间，更新股票池中所有股票的缓存。
        :param PL_last_tm:当前时间
        :return:
        """
        for PL_code in self.PL_stocks:
            log.debug(u'【%s, %s】MACD指定时间更新缓存' % (PL_code, PL_last_tm))
            df = self.PL_dbkline.PL_get_bars(PL_code, PL_count=1, PL_end_tm=PL_last_tm, PL_unit=self.PL_period, PL_fields=['close'])
            if df.empty:
                log.warn(u'【%s, %s】查询k线数据为空' % (PL_code, PL_last_tm))
                continue
            PL_last = df.iloc[-1]
            if PL_last.empty:
                continue
            PL_close = PL_last[PL_CLOSE]
            if np.isnan(PL_close):
                continue
            self.PL_update_single_cache(PL_code, df.iloc[-1].name, PL_close)  # NOTICE: 取查询的结果与已经缓存的结果对比。

    def PL_update_single_cache(self, PL_code, PL_last_tm, PL_last_close):
        """
        指定当前时间，更新一只股票的缓存。
        :param PL_code: 股票代码
        :param PL_last_tm: 指定的时间
        :param PL_last_close: 指定时间的收盘价
        :return:
        """
        log.debug(u'【%s, %s】MACD查询数据close=%s，缓存更新' % (PL_code, PL_last_tm, PL_last_close))
        if PL_code not in self.PL_bars.keys():
            self.PL___init_single_cache(PL_code, PL_last_tm)
            return

        # 发生除权除息后，重新计算缓存的数据
        PL_factors = self.PL_dbkline.PL_get_bars(PL_code, PL_count=2, PL_end_tm=PL_last_tm, PL_unit='daily',
                                              PL_fields=[PL_ADJ_FACTOR])
        if PL_factors.empty:
            log.debug(u'【%s, %s】复权因子为空', PL_code, PL_last_tm)
            return

        PL_factors = PL_factors[~(np.isnan(PL_factors[PL_ADJ_FACTOR]))]
        # 复权因子发生变化，重新初始化缓存数据
        if len(PL_factors) > 1 and PL_factors.iloc[0]['factor'] != PL_factors.iloc[1]['factor']:
            self.PL___init_single_cache(PL_code, PL_last_tm)
            log.debug(u'【%s, %s】复权因子发生变化,重新初始化缓存', PL_code, PL_last_tm)
            return
        PL_df = self.PL_bars[PL_code]
        if PL_df.empty:
            return
        if PL_last_tm <= PL_df.iloc[-1].name:  # 已经是最新的数据，不需要更新
            return

        PL_df.at[PL_last_tm, PL_CLOSE] = PL_last_close  # 追加最新的一根bar
        if len(PL_df) > PL_DEFAULT_LOAD_BAR_NUM + PL_EXTRA_LOAD_BAR_NUM:
            PL_df = PL_df.iloc[1:].copy()  # 超过缓存数量，去掉最早的一根bar

        PL_idx = len(PL_df) - 1  # 最后一根bar的位置
        self.PL_indicator.PL_macd(PL_df)  # 计算dif,dea,macd
        self.PL_update_last_bar_single_stock(PL_df, PL_code, PL_idx, self.PL_indicator)

    @staticmethod
    def PL_supply_cols(PL_df, PL_add_cols):
        """
        设置df的列
        :param PL_df:Dataframe类型。缓存的数据。
        :param PL_add_cols:要设置的列
        :return:
        """
        df_cols = PL_df.columns.values.tolist()
        for PL_col in PL_add_cols:
            if PL_col in df_cols:
                continue
            PL_df[PL_col] = None

    def PL_update_divergences(self, PL_df, PL_code):
        """
        更新缓存中的背离信息。只缓存最近一根bar产生的背离
        :param PL_df:Dataframe类型。缓存的数据。
        :param PL_code:股票代码
        :return:
        """
        # 检测背离
        if PL_code not in self.PL_divergences.keys():
            self.PL_divergences[PL_code] = []
        # 记录当前点产生的所有的背离[同一个极值点的末端，可能检测到多个起始点不同的背离]
        self.PL_divergences[PL_code] = self.PL_indicator.PL_get_last_divergences(PL_df)
