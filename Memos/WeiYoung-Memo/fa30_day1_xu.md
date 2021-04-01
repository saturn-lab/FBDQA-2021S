

## 1)

凯利公式仿真作业：

凯利公式：f=(b*p-q)/b

b=1（赔率），p=0.55（正面概率）由公式的f* = 0.1 I = 50（模拟序列个数）,  n = 100（每个序列100次实验） 红线为平均值 初始本金100 模拟投掷硬币 如果正面，将赢取的奖金加入 如果反面，从资本中减去损失 运行仿真



```python
import numpy as np
import matplotlib.pyplot as plt
#import random

b = 1.0
p = 0.55
q = 1-p
f = (b*p-q)/b

n = 100
lng = 50
win_loss = [1,0]
possib = [p,q]
result_total=[]

for _ in np.arange (1,lng):
    capital = 100
    
    
    result=[capital]
    for ind in np.arange(1,n+1):
        
        capital_change = capital * f
        res = np.random.choice(win_loss,p=possib)
        capital = capital+capital_change if res == 1 else capital - capital_change
        result.append(capital)
    #print (result)    
    
    len(result)
    if len(result_total)!=0:
        result_total=np.array(result_total)+np.array(result) 
    else:
        result_total=result

    plt.plot(result,'b')
    
    
result_average=np.array(result_total)/(np.ones(n+1)*(50))
len(np.array(result_total))
plt.plot(result_average,'r')   
plt.show() 


```



![kelly_formula](C:\Users\nordea\Documents\python\kelly_formula.png)

## 2) markdown 公式

$$
r_{P} = \beta_{P} \cdot r_{B} + \alpha_{P} + \epsilon_{P}
$$

p=portfolio, B=benchmark



## 3）markdown 画流程图



```flow
st=>start: start
op=>operation: My Operation
cond=>condition: Yes or No?
e=>end
st->op->cond
cond(yes)->e
cond(no)->op


```



## 4）markdown表格

| 课程 | 地点 | 时间 | 学分 |
| ---- | ---- | ---- | ---- |
| 数学 | 三教 | 1:00 | 2    |
| 物理 | 四教 | 2:00 | 3    |
| 化学 | 新水 | 3:00 | 4    |

