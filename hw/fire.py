# coding=utf-8
import numpy as np
import random
class fire:
    def __init__(self, nchars, oildrums, consume):
        self.nchars = nchars
        self.oildrum = oildrums
        self.consume = consume
    def genNewResult(self, res):
        '''
        res 就是 X 的值 T 温度越高产生翻转的概率越大 oldT 原本最大温度
        '''
        r = res.copy()
        x = np.random.uniform(low= 0 , high= 1)
        if x >= 0 and x < 0.4: # 使用交换法生成新的路径
            # print('交换')
            c1 = random.randint(0, len(r)-1)
            c2 = random.randint(0, len(r)-1)
            tmp = r[c1]
            r[c1] = r[c2]
            r[c2] = tmp
        elif  x >= 0.4 and x < 0.7: # 使用移动序列产生新路径
            # print('移动')
            c1 = random.randint(0, len(r) - 1)
            c2 = random.randint(0, len(r) - 1)
            c3 = random.randint(0, len(r) - 1)
            tmp = [c1, c2, c3]
            tmp.sort()
            c1 = tmp[0]
            c2 = tmp[1]
            c3 = tmp[2]
            tmp1 = r[0:c1]
            tmp2 = r[c1:c2]
            tmp3 = r[c2:c3]
            tmp4 = r[c3:]
            r = tmp1 + tmp3 + tmp2 + tmp4
        else:
            # print('倒置')
            c1 = random.randint(0, len(r) - 1)
            c2 = random.randint(0, len(r) - 1)
            if c1 > c2:
                tmp = c1
                c1 = c2
                c2 = tmp
            tmp1 = r[0:c1]
            tmp2 = r[c1:c2]
            tmp3 = r[c2:]
            tmp2.reverse()
            r = tmp1 + tmp2 + tmp3
        return r

    def solutionForTwo(self):
        T = 100  # initiate temperature
        # 初始化所有分布
        x = self.initX()
        k = 500
        y = 1000000  # 初始y值
        xmin = []  # 记录数据值
        ymin = 1000000
        # 温度衰减系数
        a = 0.95
        # 绘图
        drawX = [i for i in range(500)]
        drawY = []
        n = 500
        while n > 0:
            n -= 1
            for i in range(k):
                y = self.aimFunction1(x)
                # generate a new x in the neighboorhood of x by transform function （）
                xNew = self.genNewResult(x)
                yNew = self.aimFunction1(xNew)
                if (yNew <= y):
                    x = xNew.copy()
                    y = yNew
                    if (yNew < ymin):
                        xmin = x.copy()
                        ymin = yNew
                else:
                    p = math.exp(-(yNew - y) / T)
                    r = np.random.uniform(low=0, high=1)
                    if (r < p):
                        x = xNew.copy()
                        y = yNew
            drawY.append(y)
            T = T * a
        print('直接输出', x, self.aimFunction1(x))
        print('记录最小数值', xmin, ymin)
        return xmin, drawX, drawY

    def aimFunction(self, x):
        # 计算 质心的差值的欧式距离 同时判断方案的可行性，如果方案不可行，那么加上一个惩罚性的值
        # 判断方案是否可行
        value = 0
        for i in range(len(x)/6):
            tmp = []
            number_mid = 0
            top_tail = 0
            for j in range(6):
                tmp.append(x[i*6 + j])
                if j != 0 and j!=5:
                    if(x[i*6 + j]):
                        number_mid+=1
                else:
                    if(x[i * 6 + j]):
                        top_tail+=1
            # 判断中间的起作用的元素的个数
            if (top_tail + number_mid > 3):
                value += 100000000000
                return value
            # 判断能否cover掉输出值
            if (x[i*6 + 0]):
                self.oildrum[0].consume_one_second(self.consume[i*6 + j] / 2)




    def initX(self):
        # 生成 6 个字符随机 且中间的至少要两个也就是油桶 2 - 5 要有两个在工作，第一个和最后一个至多有一个在工作
        for j in range(10):
            t = np.random.ranf(self.nchars) # 直接生成600个随机数 如果均匀分布那么会有300个0 和 300 个1
            x = []
            for i in range(self.nchars):
                if t[i] > 0.6:
                    x.append(1)
                else:
                    x.append(0)
            sumtmp = 0
            for t in range(self.nchars):
                if(x[t] == 1):
                    sumtmp++
            if sumtmp > 150 and sumtmp < 300:
                break
        return x