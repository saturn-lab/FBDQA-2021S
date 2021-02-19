from jqdata import *
from PL_jukuan_macd_signal import *  # 导入自定义的，用于信号检测的库
from PL_signal_statistics import *  # 导入用于统计信号胜率和赔率的库

"""
普量学院量化投资课程系列案例源码包
普量学院版权所有
仅用于教学目的，严禁转发和用于盈利目的，违者必究
Plouto-Quants All Rights Reserved

普量学院助教微信：niuxiaomi3
"""

"""
macd信号检测demo。
"""

PL_PERIOD = '60m'  # 检测信号的k线周期
PL_SIGNAL_PERIOD_UNIT = 60  # 检测信号的时间间隔。与信号检测的周期保持一致。
PL_STOCK_POOL = [str(normalize_code(code)) for code in
                 ['002466', '601398', '600085', '0000063', '002236', '000651', '002415', '600703', '300187',
                  '002028']]  # 股票池


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
    g.PL_macd_signals = []


def process_initialize(context):
    """
    策略每次启动后运行的函数。策略重启后，initialize函数只能恢复可序列化的对象。
    不可序列化的对象必须要在这里定义。
    """
    g.PL_period = PL_PERIOD
    g.PL_macd_cache = None
    g.PL_stocks = PL_STOCK_POOL
    g.PL_counter = 0

    ## 初始化macd缓存
    if g.PL_macd_cache is None:
        # 使用回测时间，初始化MacdCache
        g.PL_macd_cache = PL_MacdCache(g.PL_period, context.current_dt, PL_count=250, PL_stocks=g.PL_stocks)


def PL_every_bar_start(context):
    """
    每隔SIGNAL_PERIOD_UNIT分钟检测一次信号。每根bar开盘前检测，以上一根bar的收盘价产生的信号。
    """
    if g.PL_counter % PL_SIGNAL_PERIOD_UNIT != 0:
        g.PL_counter += 1
        return
    elif g.PL_counter == 0:
        g.PL_counter += 1
    elif g.PL_counter != 0:
        g.PL_counter = 1

    # 以当前回测时间，更新缓存
    PL_current_tm = context.current_dt
    g.PL_macd_cache.PL_update_cache(PL_current_tm)

    for PL_code in g.PL_macd_cache.PL_bars.keys():
        # 获取最新一根bar检测到的背离、金叉、死叉
        PL_divergences = g.PL_macd_cache.PL_divergences[
            PL_code] if PL_code in g.PL_macd_cache.PL_divergences.keys() else []
        PL_last_bar = g.PL_macd_cache.PL_bars[PL_code].iloc[-1] if not g.PL_macd_cache.PL_bars[PL_code].empty else {}
        PL_tm = PL_last_bar.name
        if len(PL_divergences) > 0:
            for PL_divergence in PL_divergences:
                # DivergenceType.Bottom - 底背离，DivergenceType.Top - 顶背离
                if PL_divergence.PL_divergence_type == PL_DivergenceType.Bottom:
                    g.PL_macd_signals.append(
                        PL_MacdSignal(PL_code=PL_code, PL_period=g.PL_macd_cache.PL_period, PL_tm=PL_tm,
                                      PL_name='BottomDivergence'))
                    log.info(
                        '【%s, %s】all divergences=%s' % (
                            PL_code, PL_current_tm, PL_Divergence.PL_to_json_list(PL_divergences)))
                    break

        if 'gold' in PL_last_bar.keys() and PL_last_bar['gold']:
            g.PL_macd_signals.append(
                PL_MacdSignal(PL_code=PL_code, PL_period=g.PL_macd_cache.PL_period, PL_tm=PL_tm, PL_name='Gold'))
            log.info('【%s, %s】Gold, last_bar=%s, ' % (PL_code, PL_current_tm, PL_last_bar.to_dict()))

        if 'death' in PL_last_bar.keys() and PL_last_bar['death']:
            g.PL_macd_signals.append(
                PL_MacdSignal(PL_code=PL_code, PL_period=g.PL_macd_cache.PL_period, PL_tm=PL_tm, PL_name='Death'))
            log.info('【%s, %s】Death, last_bar=%s, ' % (PL_code, PL_current_tm, PL_last_bar.to_dict()))


def on_strategy_end(context):
    log.info('开始统计')
    PL_backtest_end_tm = context.run_params.end_date
    PL_SignalStatistics.PL_success_ratio(g.PL_macd_signals, PL_backtest_end_tm, [4, 8, 16, 20, 24])
