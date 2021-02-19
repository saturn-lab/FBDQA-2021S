from jqdata import *
import pandas as pd

"""
普量学院量化投资课程系列案例源码包
普量学院版权所有
仅用于教学目的，严禁转发和用于盈利目的，违者必究
Plouto-Quants All Rights Reserved

普量学院助教微信：niuxiaomi3
"""

"""
功能：macd信号检测。
检测的信号：金叉、死叉、顶背离、底背离
精简版： 背离的极值点以金叉点的值近似。例如：
    检测顶背离的极值， close_limit[收盘价极值] = 金叉点的收盘价， dif_limit[dif极值] = 金叉点的dif值
"""


def initialize(context):
    """
    初始化函数，设定要操作的股票、基准等等
    """
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    log.set_level('order', 'error')
    run_daily(PL_every_bar_start, time='every_bar', reference_security='000300.XSHG')
    # 设置策略的日级输出级别。可选：debug、info、warning、error
    log.set_level('strategy', 'info')

    # 检测信号的k线周期
    g.PL_period = '60m'
    # 检测信号的时间间隔。与信号检测的周期保持一致。
    g.PL_signal_period_unit = 60

    # 设置股票池
    g.PL_stock_pool = [str(normalize_code(code)) for code in
                       ['002466', '601398', '600085', '000063', '002236', '000651', '002415', '600703', '300187',
                        '002028']]
    g.PL_counter = 0


def PL_every_bar_start(context):
    """
    每隔SIGNAL_PL_period_UNIT分钟检测一次信号。每根bar开盘前检测，以上一根bar的收盘价产生的信号。
    """
    if g.PL_counter % g.PL_signal_period_unit != 0:
        g.PL_counter += 1
        return
    elif g.PL_counter == 0:
        g.PL_counter += 1
    elif g.PL_counter != 0:
        g.PL_counter = 1

    # 信号检测
    PL_current_tm = context.current_dt
    for code in g.PL_stock_pool:
        PL_signals = PL_detect_signals(code, PL_current_tm, g.PL_period)
        if len(PL_signals) == 0:
            continue
        for signal in PL_signals:
            log.info('检测到信号: %s', signal)


################################信号检测#######################################
class PL_MacdSignal:
    """
    触发的信号
    """

    def __init__(self, PL_code, PL_name, PL_period, PL_tm, PL_extra=None):
        """
        :param PL_code: 股票代码
        :param PL_name: 信号名称
        :param PL_period: 信号周期
        :param PL_tm: 触发信号的时间
        """
        self.code = PL_code
        self.name = PL_name
        self.period = PL_period
        self.tm = str(PL_tm)
        self.extra = PL_extra

    def __str__(self):
        """
        :return: 实例转换成字符串输出
        """
        signal = {
            'code': self.code,
            'name': str(self.name),
            'period': str(self.period),
            'tm': self.tm,
            'extra': self.extra,
        }
        return str(signal)

    __repr__ = __str__


def PL_detect_signals(PL_code, PL_current_tm, PL_period):
    """
    信号检测：只输出触发的金叉、死叉、顶背离、底背离
    :param PL_code: 股票代码
    :param PL_current_tm: 检测信号的时间
    :param PL_period: 信号的周期
    :return: signals 最近一根bar触发的信号,包括：金叉、死叉、顶背离、底背离
    """
    PL_signals = []
    # 查询收盘价
    PL_df = get_price(PL_code, end_date=PL_current_tm, frequency=PL_period, fields=['close'], skip_paused=True,
                      fq='pre',
                      count=250)
    if PL_df.empty:
        return PL_signals

    PL_df['dif'], PL_df['dea'], PL_df['macd'] = PL_calc_macd(PL_df['close'])
    # 为了方便批量计算：将当前bar的macd与前一个bar的macd放在同一行上。
    PL_df['pre_macd'] = PL_df['macd'].shift(1)

    # 批量检测dif,dea的交叉点
    PL_df['cross_type'] = PL_df.apply(lambda row: PL_get_cross_type(row['macd'], row['pre_macd']), axis=1)
    PL_last_bar = PL_df.iloc[-1]
    # 最近一根bar的时间
    PL_last_bar_tm = PL_last_bar.name
    if PL_last_bar['cross_type'] == 'Death':
        # 生成死叉信号
        PL_signals.append(PL_MacdSignal(PL_code=PL_code, PL_period=PL_period, PL_tm=PL_last_bar_tm, PL_name='Death'))
        # 判断是否触发顶背离[这是一个近似的检测：把死叉点的dif和价格当做极值，判断前后两个死叉点是否满足顶背离关系]
        PL_death_df = PL_df[PL_df['cross_type'] == 'Death']
        if len(PL_death_df) > 2:
            # 前一个死叉点
            PL_pre_death = PL_death_df.iloc[-2]
            # 顶背离：价格创新高，dif没有创新高
            if PL_last_bar['close'] > PL_pre_death['close'] and PL_last_bar['dif'] <= PL_pre_death['dif']:
                # 生成顶背离信号
                PL_signals.append(
                    PL_MacdSignal(PL_code=PL_code, PL_period=PL_period, PL_tm=PL_last_bar_tm, PL_name='TopDivergence',
                                  PL_extra={
                                      'pre_dif_limit_tm': str(PL_pre_death.name),
                                      'last_dif_limit_tm': str(PL_last_bar_tm)}))

    elif PL_last_bar['cross_type'] == 'Gold':
        # 生成金叉信号
        PL_signals.append(PL_MacdSignal(PL_code=PL_code, PL_period=PL_period, PL_tm=PL_last_bar_tm, PL_name='Gold'))
        PL_gold_df = PL_df[PL_df['cross_type'] == 'Gold']
        if len(PL_gold_df) > 2:
            # 前一个金叉点
            PL_pre_gold = PL_gold_df.iloc[-2]
            # 底背离: 价格创新低，dif没有创新低
            if PL_last_bar['close'] < PL_pre_gold['close'] and PL_last_bar['dif'] >= PL_pre_gold['dif']:
                # 生成底背离信号
                PL_signals.append(PL_MacdSignal(PL_code=PL_code, PL_period=PL_period, PL_tm=PL_last_bar_tm,
                                                PL_name='BottomDivergence',
                                                PL_extra={
                                                    'pre_dif_limit_tm': str(PL_pre_gold.name),
                                                    'last_dif_limit_tm': str(PL_last_bar_tm)}
                                                ))
    return PL_signals


def PL_get_cross_type(PL_macd, PL_pre_macd):
    """
    根据当前bar的macd和前一个bar的macd判断是否触发了金叉或死叉。
    :param PL_macd: 当前bar的macd
    :param PL_pre_macd: 前一个bar的macd
    :return: 金叉-'Gold'， 死叉-'Death'，没有交叉-None
    """
    if PL_pre_macd <= 0 < PL_macd:
        return 'Gold'
    elif PL_pre_macd >= 0 > PL_macd:
        return 'Death'
    else:
        return None


def PL_calc_macd(PL_close_series):
    """
    计算MACD的三个指标：DIF, DEA, MACD
    DIF = 当前收盘价的EMA（12）- 当前收盘价的EMA（26）
    DEA = 近9个DIF的EMA
    MACD= (DIF－DEA)*2
    :param PL_close_series:
    :return: 补充dif,dea,macd计算结果
    """
    PL_dif = pd.ewma(PL_close_series, span=12) - pd.ewma(PL_close_series, span=26)
    PL_dea = pd.ewma(PL_dif, span=9)
    PL_macd = (PL_dif - PL_dea) * 2
    return PL_dif, PL_dea, PL_macd
