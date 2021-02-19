# -*- encoding:utf-8 -*-
"""
普量学院量化投资课程系列案例源码包
普量学院版权所有
仅用于教学目的，严禁转发和用于盈利目的，违者必究
Plouto-Quants All Rights Reserved

普量学院助教微信：niuxiaomi3
"""

"""
MACD信号检测配置
"""

"""
时间窗口长度：计算移动平均线[EMA]使用, DIFF = 快速移动平均线 - 慢速移动平均线
"""
PL_SHORT = 12  # 快速移动平均线的滑动窗口长度。
PL_LONG = 26  # 慢速移动平均线de 滑动窗口

"""
时间窗口长度：计算DEA使用，DEA = DIF的MID日EMA
"""
PL_MID = 9

"""
检测极值点的参数配置
"""
# 极值的调节因子。用于匹配多个近似的极值点。
# 多个近似的极值点，取离当前交叉点最近的一个。
PL_LIMIT_DETECT_LIMIT_FACTOR = 0.99

"""
检测背离的参数配置
"""
# 背离检测：最多使用5个相邻的极值点，两两组合检测背离
PL_DIVERGENCE_DETECT_MOST_LIMIT_NUM = 5

# 背离检测：DIF涨跌幅的绝对值+价格涨跌幅的绝对值。用于判断是不是一个比较显著的背离。
PL_DIVERGENCE_DETECT_SIGNIFICANCE = 0.1

# 背离检测：价格跌幅/dif涨幅。用于判断背离的质量。
PL_DIVERGENCE_DETECT_DIF_PRICE_RATIO = 3

# 背离检测：对背离点高度的要求。采用过去250个bar内极值的最大值作为参考，背离点中必须至少有一个极值小于最大值的【20%】。
PL_DIVERGENCE_DETECT_DIF_LIMIT_BAR_NUM = 250
PL_DIVERGENCE_DETECT_DIF_LIMIT_FACTOR = 0.2

"""
缓存的MACD数据配置，缓存数据是一个包含收盘价、是否金叉、是否死叉以及根据交叉检测到的3个极值点日期：
    -   3个极值日期分别是：DIF极值的日期/收盘价极值的日期/macd极值的日期
    -   极值：金叉和死叉之间取最大值，死叉和金叉之间取最小值
"""
# macd信号检测，需要加载的历史数据。往前计算250根bar的数据，尽量不要修改
PL_DEFAULT_LOAD_BAR_NUM = 250

# EMA衰减时间：解决EMA起点不同，计算结果不同的问题。额外多查询215根bar计算EMA。
PL_EXTRA_LOAD_BAR_NUM = 215

"""
缓存的信息：MACD缓存用到的key, 不可修改
"""
PL_CLOSE = 'close'
PL_DIF = 'dif'
PL_DEA = 'dea'
PL_MACD = 'macd'
PL_GOLD = 'gold'  # 金叉
PL_DEATH = 'death'  # 死叉
PL_DIF_LIMIT_TM = 'dif_limit_tm'  # DIF极值的日期
PL_CLOSE_LIMIT_TM = 'close_limit_tm'  # 收盘价极值的日期
PL_MACD_LIMIT_TM = 'macd_limit_tm'  # macd极值的日期
PL_COLS = [PL_CLOSE, PL_DIF, PL_DEA, PL_MACD, PL_GOLD, PL_DEATH, PL_DIF_LIMIT_TM, PL_CLOSE_LIMIT_TM, PL_MACD_LIMIT_TM]  # DateFrame的列， 缓存数据
PL_ADJ_FACTOR = 'factor'
