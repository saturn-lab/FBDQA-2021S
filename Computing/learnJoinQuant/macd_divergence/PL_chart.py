# coding=utf-8
from __future__ import unicode_literals
import math
import re

from pyecharts import Bar, configure, Grid
from pyecharts import Page
import pandas as pd

"""
普量学院量化投资课程系列案例源码包
普量学院版权所有
仅用于教学目的，严禁转发和用于盈利目的，违者必究
Plouto-Quants All Rights Reserved

普量学院助教微信：niuxiaomi3
"""

"""
绘制统计图
"""

# 更换运行环境内所有图表主题
configure(global_theme='dark')


def PL_draw_echarts(PL_df, PL_slices):
    # 初始化一个画图的页面.每一种信号画一张图片
    PL_page = Page()
    PL_columns = PL_df.columns.values.tolist()
    # 所有统计的信号种类
    PL_signal_items = list(set(PL_df['signal_name'].tolist()))
    PL_signal_items.sort()

    # 所有的N[第n个bar]
    PL_bar_nos = []
    for PL_col in PL_columns:
        if re.match('chg_pct_', PL_col):
            # 获取当前统计的是第几根bar的收益
            PL_bar_nos.append(PL_col.replace('chg_pct_', ''))

    for PL_sig in PL_signal_items:
        # 获取一种信号在M个bar内的收益统计
        PL_bar = Bar(PL_sig + "收益分布", title_text_size=14, width='100%')

        PL_sdf = PL_df[(PL_df['signal_name'] == PL_sig)]
        if PL_sdf.empty:
            continue

        # 划分收益区间,从0开始往正负两端划分收益区间
        # 计算每个收益区间的大小
        PL_max_profit = 0
        PL_min_profit = 0
        for PL_no in PL_bar_nos:
            PL_pcol = 'chg_pct_' + PL_no
            PL_profits = PL_sdf[PL_pcol].tolist()
            PL_max_profit = max(max(PL_profits), PL_max_profit)
            PL_min_profit = min(min(PL_profits), PL_min_profit)
        PL_intervals = []
        if PL_min_profit < 0:
            PL_unit = round(max(PL_max_profit, abs(PL_min_profit)) / PL_slices, 4)
            # 先划分小于0的区间
            for i in range(0, int(math.ceil(abs(PL_min_profit) / PL_unit))):
                PL_intervals.append([round(-(i + 1) * PL_unit, 4), round(-i * PL_unit, 4)])
            PL_intervals.reverse()
        else:
            PL_unit = PL_max_profit / PL_slices

        for i in range(0, int(math.ceil(abs(PL_max_profit) / PL_unit))):
            PL_intervals.append([i * PL_unit, (i + 1) * PL_unit])

        # 显示收益区间之前先格式化成百分比。
        PL_format_intervals = ['%.2f%%~%.2f%%' % (i[0] * 100, i[1] * 100) for i in PL_intervals]

        for PL_no in PL_bar_nos:
            # 计算第M个bar收益，落在某一个收益区间的概率
            PL_win_ratios = []
            PL_pcol = 'chg_pct_' + PL_no
            for PL_interval in PL_intervals:
                # 统计在收益落在某个收益区间的概率
                PL_conf = (PL_sdf[PL_pcol] > PL_interval[0]) & (PL_sdf[PL_pcol] <= PL_interval[1])
                # 避免int类型直接除之后返回的还是int,这里*1.0
                PL_win_ratios.append(round(len(PL_sdf[PL_conf]) / (len(PL_sdf) * 1.0), 2))
            PL_bar.add("第%s个bar" % PL_no, PL_format_intervals, PL_win_ratios,
                    xaxis_name='收益区间',
                    xaxis_name_pos='end',
                    xaxis_name_size=12,
                    xaxis_label_textsize=12,
                    xaxis_interval=1,
                    xaxis_rotate=45,
                    yaxis_name='概率',
                    yaxis_name_pos='end',
                    yaxis_name_size=12,
                    yaxis_label_textsize=12,
                    is_splitline_show=False,
                    # 默认为 X 轴，横向
                    is_datazoom_show=True,
                    datazoom_type="both",
                    datazoom_range=[40, 60],
                    # 额外的 dataZoom 控制条，纵向
                    # is_datazoom_extra_show=True,
                    # datazoom_extra_type="slider",
                    # datazoom_extra_range=[10, 25],
                    # is_toolbox_show=False,
                    )
        PL_grid = Grid(width='100%')
        PL_grid.add(PL_bar, grid_bottom=120)
        PL_page.add(PL_grid)

    PL_page.render()


if __name__ == '__main__':
    PL_df = pd.read_csv('resources/signals.csv')
    if PL_df.empty:
        raise Exception('没有任何信号')
    PL_draw_echarts(PL_df, 50)
