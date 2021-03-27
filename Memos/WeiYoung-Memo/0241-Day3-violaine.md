# Python库Numpy

**Python科学栈**

科学栈（scientific stack）是一些Python库的集合的统称，包括：

-   Numpy
-   Scipy
-   Matplotlib
-   Pandas

**创建数组和数据类型定义**

创建数组：array()

```python
import numpy as np
c = np.array([[1,2,3],(4,5,6)],dtype=complex)
c
```

**算术运算**

与标量的算术运算：element-wise operation

```python
a = np.arange(4)
a + 4
a * 2
b = np.arange(4,8)
a + b
a - b
a * b
```

**函数算数运算符**

```python
a * np.sin(b)
a * np.sqrt(b)
A = np.arange(0,9).reshape(3,3)
B = np.ones((3,3))
```

**矩阵乘积**

$*$ is element-wise

dot() is not element-wise

```python
np.dot(A,B)
```

**增减算符operators**

-   Python中没有++或–
-   使用+=，-=，*=

**数组变形**

```python
* reshape()就按书转换数组的形状
* ravel()将多维数组转换为一维数组
a = a.ravel()
* transpose()调换数组行列值的索引值，相当于转置
A.transpose()
```

**Numpy使用**

| Numpy方法   | 描述                                                 |
| ----------- | ---------------------------------------------------- |
| np.matmul   | 矩阵相乘 (Matrix multiply)                           |
| np.zeros    | 创建零矩阵 (Create a matrix filled with zeros)       |
| np.arange   | 定义范围（开始，停止，步长）(Start, stop, step size) |
| np.identity | 创建一个单位矩阵 (Create an identity matrix)         |
| np.vstack   | 垂直叠加2阵列 (Vertically stack 2 arrays)            |

matmul和dot区别：

matmul是内积

当两个变量都是一维数组时，dot是内积；其他时候是矢量积

**Numpy调试**

| Numpy方法                   | Description                                                  |
| --------------------------- | ------------------------------------------------------------ |
| array.shape                 | 得到numpy数组的形状 (Get shape of numpy array)               |
| array.dtype                 | 检查数组的数据类型 (Check data type of array)                |
| type(stuff)                 | 获取变量的类型 (Get type of a variable)                      |
| import pdb; pdb.set_trace() | 设置断点 (Set a breakpoint) (http://docs.python.org/3/library/pdb.html) |
| print(f’My name is {name}’) | 输出信息 (Easy way to construct a message)                   |

python的print字符串前面加f表示格式化字符串，加f后可以在字符串里面使用用花括号括起来的变量和表达式

# Matplotlib画图

点线的颜色：g|green; b|blue; c|cyan; m|magenta

点的形状：.|点；v|实心倒三角；^|实心三角；o|实心圆；*|实心五角星；+|加号；s|实心方块

线的形状：-|实线；- -|虚线；-.|点划线

**散点图 (Scatter plot)**

```python
import matplotlib.pyplot as plt
plt.axis([0,5,0,20])
plt.title('My first plot')
plt.plot([1,2,3,4],[1,4,9,16],'ro')
```

**线图 (Line plot)**

Import

```python
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
```

Create data

```python
t = np.arange(0.0,2.0,0.01)
s = 1 + np.sin(2*np.pi*t)
```

Plotting

```python
plt.plot(t,s,'r')
```

Format plot

```
font = FontProperties(fname=r"C:\Windows\Fonts\simsunb.ttf",size=14)
plt.title(u'Voltage/Time',fontproperties=font)
plt.xlabel(u'time(s)',fontproperties=font)
plt.ylabel(u'voltage(mV)',fontproperties=font)
```

Save

```python
plt.savefig('test.png')
```

一图多条线

```python
plt.plot(t,y1,'b-',t,y2,'g-',t,y3,'r-')
```

绘制子图

plt.subplot(行数目，列数目，第几张图)

plt.show()

**pygal**

```pyhton
from random import randint
results = []
for roll_num in range(1000):
    result = randint(1,6)
    results.append(result)
    
frequencies = []
for value in range(1,7):
    frequency = results.count(value)
    frequencies.append(frequency)
    
import pygal

hist = pygal.Bar()
hist.title = 'Result of rolling one D6 1000 times.'
hist.x_labels = ['1','2','3','4','5','6']
hist.x_title = 'Result'
hist.y_title = ('Frequency of Result')
hist.add('D6',frequencies)
hist.render_to_file('visual.svg')
```

# 创建自己的交易策略

## 趋势跟随型策略

交易策略的要点：市场、头寸规模、入市、止损、退出、战术

**市场**

高流动性的市场

**头寸规模**
$$
N=(19*PDN+TR)/20\\
TR = Max (H-L,H-PDC,PDC-L)
$$
N = 波动性

PDN = 前一日的N值

TR = 当日的真实波动幅度

H = 当日最高价

L = 当日最低价

PDC = 前一日收盘价
$$
头寸规模单位=\frac{账户的1\%}{N*每一点数所代表的美元}
$$
头寸规模的进一步限制：

| 层面 | 限制范围               | 头寸单位上限 |
| ---- | ---------------------- | ------------ |
| 1    | 单个市场               | 4            |
| 2    | 高度关联的多个市场     | 6            |
| 3    | 松散关联的多个市场     | 10           |
| 4    | 单个方向（多头或空头） | 12           |

**入市信号**

系统1 以20日突破为基础的短期系统

系统2 以55日突破为基础的长期系统

**逐步建仓**

在突破点建立1个单位的头寸，按N/2的价格间隔逐步扩大头寸（以上一份订单的实际成交价为基准），直到头寸达到规模上限。

**止损**

价格变动的上限就是2N，对于加仓情况，止损点上浮。

**退出**

系统1 10日反向突破退出

系统2 20日反向突破退出

# Pandas基础

pandas中有三种基本结构：1D Series, 2D DataFrame, 3D Panel

## pandas一维数据series

**基本调用方法**

s = pd.Series(data, index=index)

data可以是字典、ndarray、标量

如果data是个ndarray，那么index的长度必须跟data一致

**向量化操作**

简单的向量操作与ndarray的表现一致

但Series和ndarray不同的地方在于，Series的操作默认是使用index的值进行对齐的，而不是相对位置。不能对齐的部分当作缺失值处理。

## pandas二维数据DataFrame

DataFrame(data,index,columns)中的data可以接受很多数据类型

-   一个存储一维数组，字典，列表或者Series的字典
-   2-D数组
-   结构或者记录数组
-   一个Series
-   另一个DataFrame

index用于指定行的label，colums用于指定列的label，如果参数不传入，那么会按照传入的内容进行设定。

**从Series字典中构造**

```python
d = {'one': pd.Series([1.,2.,3.], index=['a', 'b', 'c']), 'two': pd.Series([1.,2.,3.,4.],index=['a', 'b', 'c', 'd'])}
df = pd.DataFrame(d)
```

如果没有传入columns的值，那么columns的值默认为字典key，index默认为所有value中index的并集。

```python
df.index
df.columns
```

如果指定了columns值，会去字典中寻找，找不到的值为NaN：

```python
pd.DataFrame(d, index=['d','b','a'],columns=['two','three'])
```

**列操作**

DataFrame可以类似于字典一样对列进行操作

**操作csv文件**

从csv文件中读取：

```python
pd.read_csv('foo.csv')
```

保存写入csv文件：

```python
df.to_csv('foo.csv')
```

**总结索引和选择**

| Operation                      | Syntax        | Result    |
| ------------------------------ | ------------- | --------- |
| Select column                  | df[col]       | Series    |
| Select row by label            | df.loc[label] | Series    |
| Select row by integer location | df.iloc[loc]  | Series    |
| Slice rows                     | df[5:10]      | DataFrame |
| Select rows by boolean vector  | df[bool_vec]  | DataFrame |

## Seaborn绘图示例

http://seaborn.pydata.org/api.html

relplot(relational): scatterplot, lineplot

displot(distributions): histplot, kdeplot, ecdfplot, rugplot

catplot(categorical): stripplot, swarmplot, boxplot, violinplot, pointplot, barplot

**直方图**

```python
sns.displot(tips, x='total_bills')
sns.histplot(tips, x='total_bills')
# hue参数使用不同颜色区分类别
sns.displot(tips, x='total_bills', hue='sex')
sns.displot(tips, x='total_bills', hue='sex', col='sex')
```

**概率密度图**

```python
sns.kdeplot(data=tips,x='total_bill',hue='sex')
sns.displot(tips,x='total_bill',kind='kde',hue='sex')
# 同时绘制直方图和概率密度图
sns.displot(tips,x='total_bill',kde=True)
```

**累积分布图**

```python
sns.displot(tips,x='tota_bill',hue='sex',kind='ecdf')
sns.ecdfplot(tips,x='total_bill',hue='sex')
```

**多变量图**

```python
sns.displot(tips,x='total_bill',y='tip',hue='sex')
sns.displot(tips,x='total_bill',y='tip',hue='sex',kind=kde)
```

**散点图**

```python
sns.relplot(x="total_bill", y="tip", data=tips)
sns.scatterplot(x="total_bill", y="tip", data=tips)
# style参数根据类别使用不同形状，推荐和hue使用相同变量
sns.relplot(x="total_bill", y="tip", hue="smoker", style="smoker")
# 使用col或row绘制子图区分新的种类
sns.relplot(x="total_bill", y="tip", hue="sex", col="smoker")
```

**线图**

```python
sns.relplot(data=fmri, x="timepoint", y="signal", hue="event", style="event", kind="line")
sns.lineplot(data=fmri, x="timepoint",hue="event", style="event", y="signal")
```

**相关图**

```python
sns.jointplot(data=df, x="total_bill", y="tip", hue="sex")
sns.pairplot(data=df, hue="sex")
```

**分布图**

```python
sns.stripplot(data=df, x="day", jitter=False, y="tip")
sns.catplot(data=df, x="day", jitter=False, y="tip")
sns.catplot(data=df, x="day", y="tip", kind="swarm")
# 根据分位数箱数，box四分位数，boxen更多的分位数
sns.catplot(data=df, x="day", y="tip", kind="box", hue="smoker")
sns.catplot(data=df, x="day", y="tip", kind="boxen")
# 概率密度图和box结合，因此可使用和kde类似的平滑参数
sns.catplot(data=df, x="day", y="tip", kind="violin")
```

**统计图**

```python
sns.catplot(x="sex", y="survived", hue="class", kind="bar", data=titanic)
sns.catplot(x="sex", y="survived", hue="class", kind="point", data=titanic)
```

**回归分析**

```python
sns.regplot(x='total_bill', y='tip', data=tips)
sns.lmplot(x='total_bill', y='tip', data=tips)
sns.lmplot(x='x', y='y', data=anscombe.query("dataset == 'II'"), order=2)
# 通过robust选项忽略特异点
sns.lmplot(x='x', y='y', data=anscombe.query("dataset == 'II'"), ci=None, robust=True)
# 通过kind参数可以在其他图形级绘图函数中进行回归分析
sns.jointplot(x='total_bill', y='tip', data=tips, kind='reg')
```

**总结**

-   画布级函数
    -   displot, relplot, catplot
    -   jointplot, pairplot, lmplot
-   参数
    -   col, row：分类子图（画布级）
    -   kind：图形类别（画布级）
    -   hue, style：颜色，样式区分
