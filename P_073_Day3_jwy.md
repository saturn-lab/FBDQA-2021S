## 课程日志3

**一、python--numpy**

1. 数组与标量的算术运算：应用于整体
   例：$a = [1,2,3,4]，a\times2 = [2,4,6,8]$
   
2. $np.arange(first, last, step)$：产生数组，从first到last-1，步长为step（默认为1）

3. 函数运算：$np.sin()，np.sqrt()$；常数：$\pi:np.pi$

4. 矩阵的相乘
   1. 对应元素相乘：$A*B$
   2. 矩阵点乘：$np.dot(A, B)$
   
5. 矩阵维数的调整：对一原有矩阵A，直接使用$A.shape=(row,col)$可以直接改变A的维数

6. $A.ravel()$：将多维数组转换成一维数组

7. 垂直叠加：$np.vstack$()，横向叠加：$np.hstack()$

   
   

**二、python-matplotlib**

1. $plt.axis(0, 5, 0, 20)$：横坐标范围0到5，纵坐标0到20
2. $plt.plot$参数：'o'表示画点，省略则默认为画折线
3. $from\ matplotplib.font\_manager\ import\ FontProperties$，可以自定义字体
4. x轴y轴标签：$plt.xlabel，plt.ylabel$




**三、海龟交易策略**

1. 趋势跟随：只是一个交易观念，在趋势开始时入场，判断趋势将要结束时出场，追涨杀跌
   一般适用于高流动性的市场，问题是可能判断不准
   什么时候会死得很惨？宽幅震荡
   
2. 波动性：$N = (19 * PDN + TR) / 20$
   头寸规模单位的计算：每一点代表的美元 = 每一最小单位的资金（每一手交易最少100股）
   
   头寸规模单位：使得每笔交易最多亏损原账户的1%（可以自己选）
   
3. 头寸单位有上限

4. 入市信号：短期（20日突破，即突破过去20天最高点）、长期（55日突破）

5. 趋势交易策略：假突破伤害很大，且经常发生（60%以上都是假突破）
   趋势交易胜率很低，因此要赔率足够，一旦是真突破要赚的足够，因此要加仓
   逐步建仓：突破点建立1单位头寸，之后按$N/2$的价格间隔逐步建立头寸

6. 止损：价格变动上限$2N$

7. 退出：10日 / 20日反向突破退出

8. 用$Tradeblazer$实现海龟策略




**四、python--pandas**

1. 一维$Series$：
   1. 构造一维序列：$s = pd.Series(data, index = index)$，其中$index$可以省略，默认为$0，1...$
   2. $Series$操作默认使用$index$对齐，不能对其的部分当作$NaN$处理
2. 二维$DataFrame$：
   1. 数据结构：$Dataframe(data, index, columns)$，其中$index$为行，$columns$为列
   2. $Dataframe$类型的$df$，$df.index$和$df.columns$可以返回行和列的标签
   3. 从$csv$文件中读取：$pd.read_csv$；写入$csv$文件：$df.to_csv$
   4. 索引选择：$df.loc[label]$（填标签），$df.iloc(loc)$（填数字），均返回$Series$



**五、python--Seaborn**

1. Seaborn有一些内置的数据集，$load_dataset$
2. 画直方图时，可用hue参数区别不同种类的直方图
3. $kdeplot$：概率密度图，可以同时画直方图和概率密度图



**六、凯利公式**

