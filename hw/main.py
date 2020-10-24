#coding=utf-8
from solution import solution
import winsound
import xlwt
import time
def main1():
    s = solution()
    s.readForQuestion_one('C:/Users/lee/Desktop/华为杯/2020年中国研究生数学建模竞赛赛题/2020年F题/2020年F题--飞行器质心平衡供油策略优化/附件1-飞行器参数.xlsx', '飞行器结构参数')
    s.readForQuestion_one_question('C:/Users/lee/Desktop/华为杯/2020年中国研究生数学建模竞赛赛题/2020年F题/2020年F题--飞行器质心平衡供油策略优化/附件2-问题1数据.xlsx', '油箱供油曲线', '飞行器俯仰角')
    s.write_one('C:/Users/lee/Desktop/question_one.xls', '飞行器坐标')

def main2():
    s = solution()
    s.readForQuestion_one('C:/Users/lee/Desktop/华为杯/2020年中国研究生数学建模竞赛赛题/2020年F题/2020年F题--飞行器质心平衡供油策略优化/附件1-飞行器参数.xlsx', '飞行器结构参数')
    s.readForQuestion_two('C:/Users/lee/Desktop/华为杯/2020年中国研究生数学建模竞赛赛题/2020年F题/2020年F题--飞行器质心平衡供油策略优化/附件3-问题2数据.xlsx', '发动机耗油速度', '飞行器理想质心数据')
    s.write_two('C:/Users/lee/Desktop/question_two.xls', '飞行器质心距离', '供油', '飞行器质心')

def main3():
    s = solution()
    s.readForQuestion_one('C:/Users/lee/Desktop/华为杯/2020年中国研究生数学建模竞赛赛题/2020年F题/2020年F题--飞行器质心平衡供油策略优化/附件1-飞行器参数.xlsx', '飞行器结构参数')
    # 不知道为什么表格的名字还不一样
    s.readForQuestion_three('C:/Users/lee/Desktop/华为杯/2020年中国研究生数学建模竞赛赛题/2020年F题/2020年F题--飞行器质心平衡供油策略优化/附件4-问题3数据.xlsx', '发动机耗油数据', '飞行器理想质心')
    s.write_two('C:/Users/lee/Desktop/question_three.xls', '飞行器质心距离', '供油', '飞行器质心')

def main4():
    s = solution()
    s.readForQuestion_one('C:/Users/lee/Desktop/华为杯/2020年中国研究生数学建模竞赛赛题/2020年F题/2020年F题--飞行器质心平衡供油策略优化/附件1-飞行器参数.xlsx','飞行器结构参数')
    s.readForQuestion_four('C:/Users/lee/Desktop/华为杯/2020年中国研究生数学建模竞赛赛题/2020年F题/2020年F题--飞行器质心平衡供油策略优化/附件5-问题4数据.xlsx', '发动机耗油数据', '飞行器俯仰角')
    s.write_two('C:/Users/lee/Desktop/question_four.xls', '飞行器质心距离', '供油', '飞行器质心')
if __name__ == "__main__":
    start = time.time()
    main4()
    end = time.time()
    print(end - start)
    # winsound.Beep(600, 2000)
