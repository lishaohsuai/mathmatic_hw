#coding=utf-8
import xlrd
import xlwt
from aircraft import aircraft
from oildrum import oildrum
from utils import volume2weight,twoDim2threeDim,centroid_of_centorids,point,cal_included_angle,distance
import utils
from q1 import box_centre
from core_question import centroid_t_to_f
import math

class solution:
    def __init__(self):
        self.aircraft = 0
        self.result_one = []
        self.oil = []
        self.result_two = [] # 将油耗数据存储其中
        self.result_oil = []
        self.result_po = [] # 质心的时刻数据

        # self.result_three = [] # 将油增加的数据存储其中 第三问可以直接用第二问的数据？
    def readForQuestion_one(self, filename, sheet):
        '''
        对于问题1 读取设定参数
        '''
        data = xlrd.open_workbook(filename)
        table = data.sheet_by_name(sheet)
        name = table.name
        rowNum = table.nrows
        colNum = table.ncols
        print(name, rowNum, colNum)
        # 读取 飞行器 参数
        # 有些参数懒得读取直接赋值
        self.aircraft = aircraft(3000) # 质量3000kg
        for i in range(2,8): # 3 - 9 行读取油桶的数据
            position = []
            boxSize = []
            originVolume = 0
            name = table.cell(i, 0).value
            for j in range(1,4): # 2 - 4 列是油桶的数据 x y z
                position.append(table.cell(i, j).value)
            for j in range(4,8):
                boxSize.append(table.cell(i, j).value)
            originVolume = table.cell(i,7).value
            #  x, y, z, weight, length, width, height, name)
            originWeight = volume2weight(originVolume, 850) # roh 850
            t = oildrum(position[0], position[1], position[2], originWeight, boxSize[0], boxSize[1], boxSize[2], name)
            self.aircraft.add_oildrum(t)
        # 临时 打印相关的参数名字
        for i in range(len(self.aircraft.oildrums)):
            print(self.aircraft.oildrums[i].name)
        # 设定油桶的其他参数
        for i in range(18, 24):
            self.aircraft.oildrums[i - 18].set_other_para(table.cell(i, 2).value, 850)
        # 临时 打印相关的油桶的U
        for i in range(18,24):
            print(self.aircraft.oildrums[i - 18].U,self.aircraft.oildrums[i - 18].maxWeight)

    def readForQuestion_one_question(self, filename, sheet, sheet2):
        data = xlrd.open_workbook(filename)
        table = data.sheet_by_name(sheet)
        name = table.name
        rowNum = table.nrows
        colNum = table.ncols
        print(name, rowNum, colNum)
        oilPara = []
        for i in range(1, rowNum):
            tmp = []
            for j in range(7): # 加上时间的参数吧
                tmp.append(table.cell(i, j).value)
            oilPara.append(tmp)
        # 临时 为了校验
        # for i in range(10):
        #     print(oilPara[i][0], oilPara[i][1])
        # 读取另外一个表的参数
        data = xlrd.open_workbook(filename)
        table = data.sheet_by_name(sheet2)
        name = table.name
        rowNum = table.nrows
        colNum = table.ncols
        print(name, rowNum, colNum)
        thetaPara = []
        for i in range(1, rowNum):
            tmp = []
            for j in range(2): # 加上时间的参数吧
                tmp.append(table.cell(i, j).value)
            thetaPara.append(tmp)
        # 临时为了校验 参数校验完毕
        # print(thetaPara[99][0], thetaPara[99][1])
        # TODO:提供处理计算
        '''
        v : 油体积
        box: [x z y]  长高宽
        a: 倾斜角度
        return t [x, z]
        '''
        for i in range(len(thetaPara)):
            # 计算体积
            self.renew_oildrum(oilPara[i])
            # 对每个油箱开始计算质心
            self.renew_centroid(thetaPara[i][1])

    def readForQuestion_two(self, filename, sheet, sheet2):
        data = xlrd.open_workbook(filename)
        table = data.sheet_by_name(sheet)
        name = table.name
        rowNum = table.nrows
        colNum = table.ncols
        print(name, rowNum, colNum)
        oilcon = []
        for i in range(1, rowNum):
            oilcon.append(table.cell(i, 1).value)
        data = xlrd.open_workbook(filename)
        table = data.sheet_by_name(sheet2)
        name = table.name
        rowNum = table.nrows
        colNum = table.ncols
        print(name, rowNum, colNum)
        nicePosition = []
        for i in range(1, rowNum):
            tmp = []
            for j in range(1,4): # 不加上时间的参数吧
                tmp.append(table.cell(i, j).value)
            nicePosition.append(tmp) # list 类型
        # TODO:提供处理计算
        # 计算每一个油箱在油箱中放入单位质量造成的质心位移偏差的权重 为 选定的方案 供油比做参考
        for i in range(int(len(nicePosition) / 60)):
            # 真实当前时刻
            cur_time = i * 60
            print('[DEBUG] ', cur_time)
            # 计算真实质心和60s均值质心，作为这60s想要前往的偏差
            v = self.cal_60(cur_time, nicePosition)
            idea_vec = self.cal_nicePosition_curPosition(v)
            # 通过一个函数得到了方案，然后进行60s
            oil60 = []
            for t in range(60):
                oil60.append(oilcon[cur_time+t])
            s = self.aircraft.choose_solution_for_60(idea_vec, oil60)
            if(s[0] == -1):
                print('[ERROR] No Solution')
                return
            for j in range(60):
                cur_t = cur_time + j
                p = self.renew_centroid_for_two()
                two, li = self.cal_every_second_best_value(s, oilcon[cur_t], point(nicePosition[cur_t][0], nicePosition[cur_t][1], nicePosition[cur_t][2]))
                self.result_two.append(two)
                self.result_oil.append(li)
                self.result_po.append([p.getX(), p.getY(), p.getZ()])

    def readForQuestion_three(self, filename, sheet, sheet2):
        data = xlrd.open_workbook(filename)
        table = data.sheet_by_name(sheet)
        name = table.name
        rowNum = table.nrows
        colNum = table.ncols
        print(name, rowNum, colNum)
        oilcon = []
        for i in range(1, rowNum):
            oilcon.append(table.cell(i, 1).value)
        data = xlrd.open_workbook(filename)
        table = data.sheet_by_name(sheet2)
        name = table.name
        rowNum = table.nrows
        colNum = table.ncols
        print(name, rowNum, colNum)
        nicePosition = []
        for i in range(1, rowNum):
            tmp = []
            for j in range(1, 4):  # 不加上时间的参数吧
                tmp.append(table.cell(i, j).value)
            nicePosition.append(tmp)  # list 类型
        # ----- 上半部分将每个油箱的质量设定为0 然后将1m^3 的油进行
        # self.init_three()
        # 得到六个油桶的初始值 对于反过来说
        '''
        油箱1 10.0
        油箱2 10.79
        油箱3 220.35999999999711
        油箱4 84.59999999999977
        油箱5 0.5500000000002365
        油箱6 523.7000000000046
        '''
        self.aircraft.oildrums[0].set_weight(10.0)
        self.aircraft.oildrums[1].set_weight(10.79)
        self.aircraft.oildrums[2].set_weight(220.36)
        self.aircraft.oildrums[3].set_weight(84.60)
        self.aircraft.oildrums[4].set_weight(0.55)
        self.aircraft.oildrums[5].set_weight(523.7)
        # 倒转相关的点和油耗
        oilcon.reverse()
        nicePosition.reverse()

        # TODO:提供处理计算
        # 计算每一个油箱在油箱中放入单位质量造成的质心位移偏差的权重 为 选定的方案 供油比做参考
        for i in range(int(len(nicePosition) / 60)):
            # 真实当前时刻
            cur_time = i * 60
            print('[DEBUG] ', cur_time)
            # 计算真实质心和60s均值质心，作为这60s想要前往的偏差
            v = self.cal_60(cur_time, nicePosition)
            idea_vec = self.cal_nicePosition_curPosition(v)
            # 通过一个函数得到了方案，然后进行60s
            oil60 = []
            for t in range(60):
                oil60.append(oilcon[cur_time + t])
            s = self.aircraft.choose_solution_for_60_(idea_vec, oil60)
            if (s[0] == -1):
                print('[ERROR] No Solution')
                return
            for j in range(60):
                cur_t = cur_time + j

                p = self.renew_centroid_for_two()
                two, li = self.cal_every_second_best_value_(s, oilcon[cur_t],
                                                           point(nicePosition[cur_t][0], nicePosition[cur_t][1],
                                                                 nicePosition[cur_t][2]), cur_t)
                if(cur_t >= 6464 and cur_t < 6470):
                    print('come ', s, oilcon[cur_t], li, two, nicePosition[cur_t][0], nicePosition[cur_t][1], nicePosition[cur_t][2])
                self.result_two.append(two)
                self.result_oil.append(li)
                self.result_po.append([p.getX(), p.getY(), p.getZ()])
        # 将结果再倒转回来
        self.result_two.reverse()
        self.result_oil.reverse()
        self.result_po.reverse()
        for i in range(6):
            print(self.aircraft.oildrums[i].name, self.aircraft.oildrums[i].get_weight())

    def readForQuestion_four(self, filename, sheet, sheet2):
        data = xlrd.open_workbook(filename)
        table = data.sheet_by_name(sheet)
        name = table.name
        rowNum = table.nrows
        colNum = table.ncols
        print(name, rowNum, colNum)
        oilcon = []
        for i in range(1, rowNum):
            oilcon.append(table.cell(i, 1).value)
        data = xlrd.open_workbook(filename)
        table = data.sheet_by_name(sheet2)
        name = table.name
        rowNum = table.nrows
        colNum = table.ncols
        print(name, rowNum, colNum)
        allTheta = []
        for i in range(1, rowNum):
            allTheta.append(table.cell(i, 1).value)
        # TODO:提供处理计算
        # 计算每一个油箱在油箱中放入单位质量造成的质心位移偏差的权重 为 选定的方案 供油比做参考
        for i in range(int(len(allTheta) / 60)):
            # 真实当前时刻
            cur_time = i * 60
            print('[DEBUG] ', cur_time)
            # 在t+60 以t时刻的质量 产生的对于原点的偏移 作为 理想偏移
            theta60 = allTheta[cur_time+59]
            idea_vec = self.cal_60_1(theta60) # cal_60_1
            # 通过一个函数得到了方案，然后进行60s
            oil60 = []
            for t in range(60):
                oil60.append(oilcon[cur_time + t])
            s = self.aircraft.choose_solution_for_60_for_four(idea_vec, oil60, theta60)
            if (s[0] == -1):
                print('[ERROR] No Solution')
                return
            for j in range(60):
                cur_t = cur_time + j
                p = self.renew_centroid_for_four(allTheta[cur_t])
                two, li = self.cal_every_second_best_value_for_four(s, oilcon[cur_t], point(0, 0, 0), allTheta[cur_t]) # 以飞行器质心作为比较
                self.result_two.append(two)
                self.result_oil.append(li)
                self.result_po.append(p)



    def init_three(self):
        for i in range(6):
            self.aircraft.oildrums[i].set_weight(10)
        self.aircraft.oildrums[2].set_weight(20)
        start_weight = 1 * 850 - 10 * 6 - 10 # 780
        oilcon = []
        for i in range(start_weight * 10):
            oilcon.append(0.1)
        # 每次1kg 的燃油增加看看结果吧
        for i in range(int(start_weight * 10 / 60)):
            # 真实当前时刻
            cur_time = i * 60
            print('[DEBUG] ', cur_time)
            # 计算真实质心和60s均值质心，作为这60s想要前往的偏差
            # v = self.cal_60(cur_time, nicePosition)
            v = [-0.269842577 ,-0.134441897,-0.081529894]

            idea_vec = self.cal_nicePosition_curPosition(v)
            # 通过一个函数得到了方案，然后进行60s
            oil60 = []
            for t in range(60):
                oil60.append(oilcon[cur_time+t])
            s = self.aircraft.choose_solution_for_60_(idea_vec, oil60)
            if(s[0] == -1):
                print('[ERROR] No Solution')
                return
            for j in range(60):
                cur_t = cur_time + j
                p = self.renew_centroid_for_two()
                two, li = self.cal_every_second_best_value_(s, oilcon[cur_t], point(v[0], v[1], v[2]))
                self.result_two.append(two)
                self.result_oil.append(li)
                self.result_po.append([p.getX(), p.getY(), p.getZ()])
        for i in range(6):
            print(self.aircraft.oildrums[i].name, self.aircraft.oildrums[i].get_weight())

    def cal_every_second_best_value_for_four(self, sche, cur_oil, cur_weight_point, cur_theta):
        '''
        :param sche: ['0', '1'...]
        :param cur_oil: 当前需要消耗的油值
        :param cur_weight_point point 类型
        :param cur_theta 当前角度
        :return: 输出 最新质心
        '''
        a = -1
        b = -1 # 主油箱
        c = -1
        which = []
        for i in range(6):
            if(sche[i] == '1'):
                which.append(i)
        for i in which:
            if(i == 0 or i == 5):
                a = i # a 是副油箱
            else:
                if(b == -1):
                    b = i
                    continue
                if(c == -1):
                    c = i
        a_con = 1.1
        if(a == 0):
            # 遍历副油箱的供油情况
            timess = int(1.1 / 0.1) # 以0.1
            timess = 2 # 太慢了 加上不着不加上 0.1
            mina = 0
            minb = 0
            minc = 0
            minOL = 100000000
            weight_a = self.aircraft.oildrums[a].get_weight()
            weight_1 = self.aircraft.oildrums[1].get_weight()
            weight_b = self.aircraft.oildrums[b].get_weight()
            weight_c = self.aircraft.oildrums[c].get_weight()
            times = int(cur_oil / 0.01)
            for i in range(timess):
                self.aircraft.oildrums[a].set_weight(weight_a)
                self.aircraft.oildrums[1].set_weight(weight_1)
                self.aircraft.oildrums[b].set_weight(weight_b)
                self.aircraft.oildrums[c].set_weight(weight_c)
                if(self.aircraft.oildrums[a].check_can_consume(i * a_con)):
                    if(self.aircraft.oildrums[1].check_can_add(i * a_con)):
                        self.aircraft.oildrums[a].consume_one_second(i * a_con)
                        self.aircraft.oildrums[1].add_one_second(i * a_con)
                if (times == 0):
                    if (self.aircraft.oildrums[b].check_can_consume(cur_oil)):
                        self.aircraft.oildrums[b].consume_one_second(cur_oil)
                        cur_weight_point_ = self.renew_centroid_for_four(cur_theta)
                        cur_weight_point_ = point(cur_weight_point_[0], cur_weight_point_[1], cur_weight_point_[2])
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = cur_oil
                            minc = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                    if (self.aircraft.oildrums[c].check_can_consume(cur_oil)):
                        self.aircraft.oildrums[c].consume_one_second(cur_oil)
                        cur_weight_point_ = self.renew_centroid_for_four(cur_theta)
                        cur_weight_point_ = point(cur_weight_point_[0], cur_weight_point_[1], cur_weight_point_[2])
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minc = cur_oil
                            minb = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                for j in range(times+1):
                    if (self.aircraft.oildrums[b].check_can_consume(0.01 * j) and self.aircraft.oildrums[
                        c].check_can_consume(cur_oil - 0.01 * j) and j < times):
                        self.aircraft.oildrums[b].consume_one_second(0.01 * j)
                        self.aircraft.oildrums[c].consume_one_second(cur_oil - 0.01 * j)
                        cur_weight_point_ = self.renew_centroid_for_four(cur_theta)
                        cur_weight_point_ = point(cur_weight_point_[0], cur_weight_point_[1], cur_weight_point_[2])
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = 0.01 * j
                            minc = cur_oil - 0.01 * j
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                    elif (self.aircraft.oildrums[b].check_can_consume(cur_oil) and self.aircraft.oildrums[
                        c].check_can_consume(0) and j == times):
                        self.aircraft.oildrums[b].consume_one_second(cur_oil)
                        self.aircraft.oildrums[c].consume_one_second(0)
                        cur_weight_point_ = self.renew_centroid_for_four(cur_theta)
                        cur_weight_point_ = point(cur_weight_point_[0], cur_weight_point_[1], cur_weight_point_[2])
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = cur_oil
                            minc = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
            self.aircraft.oildrums[a].set_weight(weight_a)
            self.aircraft.oildrums[1].set_weight(weight_1)
            self.aircraft.oildrums[b].set_weight(weight_b)
            self.aircraft.oildrums[c].set_weight(weight_c)
        else: # a = 5
            timess = int(1.1 / 0.01)
            timess = 2
            mina = 0
            minb = 0
            minc = 0
            minOL = 100000000
            weight_a = self.aircraft.oildrums[a].get_weight()
            weight_4 = self.aircraft.oildrums[4].get_weight()
            weight_b = self.aircraft.oildrums[b].get_weight()
            weight_c = self.aircraft.oildrums[c].get_weight()
            times = int(cur_oil / 0.01)
            for i in range(timess):
                self.aircraft.oildrums[a].set_weight(weight_a)
                self.aircraft.oildrums[4].set_weight(weight_4)
                self.aircraft.oildrums[b].set_weight(weight_b)
                self.aircraft.oildrums[c].set_weight(weight_c)
                if(self.aircraft.oildrums[a].check_can_consume(i * a_con)):
                    if(self.aircraft.oildrums[4].check_can_add(i * a_con)):
                        self.aircraft.oildrums[a].consume_one_second(i * a_con)
                        self.aircraft.oildrums[4].add_one_second(i * a_con)
                if (times == 0):
                    if (self.aircraft.oildrums[b].check_can_consume(cur_oil)):
                        self.aircraft.oildrums[b].consume_one_second(cur_oil)
                        cur_weight_point_ = self.renew_centroid_for_four(cur_theta)
                        cur_weight_point_ = point(cur_weight_point_[0], cur_weight_point_[1], cur_weight_point_[2])
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = cur_oil
                            minc = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                    if (self.aircraft.oildrums[c].check_can_consume(cur_oil)):
                        self.aircraft.oildrums[c].consume_one_second(cur_oil)
                        cur_weight_point_ = self.renew_centroid_for_four(cur_theta)
                        cur_weight_point_ = point(cur_weight_point_[0], cur_weight_point_[1], cur_weight_point_[2])
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minc = cur_oil
                            minb = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                for j in range(times+1):
                    if (self.aircraft.oildrums[b].check_can_consume(0.01 * j) and self.aircraft.oildrums[
                        c].check_can_consume(cur_oil - 0.01 * j) and j < times):
                        self.aircraft.oildrums[b].consume_one_second(0.01 * j)
                        self.aircraft.oildrums[c].consume_one_second(cur_oil - 0.01 * j)
                        cur_weight_point_ = self.renew_centroid_for_four(cur_theta)
                        cur_weight_point_ = point(cur_weight_point_[0], cur_weight_point_[1], cur_weight_point_[2])
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = 0.01 * j
                            minc = cur_oil - 0.01 * j
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                    elif (self.aircraft.oildrums[b].check_can_consume(cur_oil) and self.aircraft.oildrums[
                        c].check_can_consume(0) and j == times):
                        self.aircraft.oildrums[b].consume_one_second(cur_oil)
                        self.aircraft.oildrums[c].consume_one_second(0)
                        cur_weight_point_ = self.renew_centroid_for_four(cur_theta)
                        cur_weight_point_ = point(cur_weight_point_[0], cur_weight_point_[1], cur_weight_point_[2])
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = cur_oil
                            minc = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
            self.aircraft.oildrums[a].set_weight(weight_a)
            self.aircraft.oildrums[4].set_weight(weight_4)
            self.aircraft.oildrums[b].set_weight(weight_b)
            self.aircraft.oildrums[c].set_weight(weight_c)
        self.aircraft.oildrums[a].consume_one_second(mina)
        if(a == 0):
            self.aircraft.oildrums[1].add_one_second(mina)
        elif(a==5):
            self.aircraft.oildrums[4].add_one_second(mina)
        self.aircraft.oildrums[b].consume_one_second(minb)
        self.aircraft.oildrums[c].consume_one_second(minc)
        out = []
        for i in range(0, 6):
            if (i == b):
                out.append(minb)
            elif (i == c):
                out.append(minc)
            elif (i == a):
                out.append(mina)
            else:
                out.append(0)
        return minOL, out


    def cal_every_second_best_value(self, sche, cur_oil, cur_weight_point):
        '''
        :param sche: ['0', '1'...]
        :param cur_oil: 当前需要消耗的油值
        :param cur_weight_point point 类型
        :return: 输出 最新质心
        '''
        a = -1
        b = -1 # 主油箱
        c = -1
        which = []
        for i in range(6):
            if(sche[i] == '1'):
                which.append(i)
        for i in which:
            if(i == 0 or i == 5):
                a = i # a 是副油箱
            else:
                if(b == -1):
                    b = i
                    continue
                if(c == -1):
                    c = i
        a_con = 1.1
        if(a == 0):
            # 遍历副油箱的供油情况
            timess = int(1.1 / 0.1) # 以0.1
            timess = 2 # 太慢了 加上不着不加上 0.1
            mina = 0
            minb = 0
            minc = 0
            minOL = 100000000
            weight_a = self.aircraft.oildrums[a].get_weight()
            weight_1 = self.aircraft.oildrums[1].get_weight()
            weight_b = self.aircraft.oildrums[b].get_weight()
            weight_c = self.aircraft.oildrums[c].get_weight()
            times = int(cur_oil / 0.01)
            for i in range(timess):
                self.aircraft.oildrums[a].set_weight(weight_a)
                self.aircraft.oildrums[1].set_weight(weight_1)
                self.aircraft.oildrums[b].set_weight(weight_b)
                self.aircraft.oildrums[c].set_weight(weight_c)
                if(self.aircraft.oildrums[a].check_can_consume(i * a_con)):
                    if(self.aircraft.oildrums[1].check_can_add(i * a_con)):
                        self.aircraft.oildrums[a].consume_one_second(i * a_con)
                        self.aircraft.oildrums[1].add_one_second(i * a_con)
                if (times == 0):
                    if (self.aircraft.oildrums[b].check_can_consume(cur_oil)):
                        self.aircraft.oildrums[b].consume_one_second(cur_oil)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = cur_oil
                            minc = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                    if (self.aircraft.oildrums[c].check_can_consume(cur_oil)):
                        self.aircraft.oildrums[c].consume_one_second(cur_oil)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minc = cur_oil
                            minb = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                for j in range(times+1):
                    if (self.aircraft.oildrums[b].check_can_consume(0.01 * j) and self.aircraft.oildrums[
                        c].check_can_consume(cur_oil - 0.01 * j) and j < times):
                        self.aircraft.oildrums[b].consume_one_second(0.01 * j)
                        self.aircraft.oildrums[c].consume_one_second(cur_oil - 0.01 * j)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = 0.01 * j
                            minc = cur_oil - 0.01 * j
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                    elif (self.aircraft.oildrums[b].check_can_consume(cur_oil) and self.aircraft.oildrums[
                        c].check_can_consume(0) and j == times):
                        self.aircraft.oildrums[b].consume_one_second(cur_oil)
                        self.aircraft.oildrums[c].consume_one_second(0)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = cur_oil
                            minc = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
            self.aircraft.oildrums[a].set_weight(weight_a)
            self.aircraft.oildrums[1].set_weight(weight_1)
            self.aircraft.oildrums[b].set_weight(weight_b)
            self.aircraft.oildrums[c].set_weight(weight_c)
        else: # a = 5
            timess = int(1.1 / 0.01)
            timess = 2
            mina = 0
            minb = 0
            minc = 0
            minOL = 100000000
            weight_a = self.aircraft.oildrums[a].get_weight()
            weight_4 = self.aircraft.oildrums[4].get_weight()
            weight_b = self.aircraft.oildrums[b].get_weight()
            weight_c = self.aircraft.oildrums[c].get_weight()
            times = int(cur_oil / 0.01)
            for i in range(timess):
                self.aircraft.oildrums[a].set_weight(weight_a)
                self.aircraft.oildrums[4].set_weight(weight_4)
                self.aircraft.oildrums[b].set_weight(weight_b)
                self.aircraft.oildrums[c].set_weight(weight_c)
                if(self.aircraft.oildrums[a].check_can_consume(i * a_con)):
                    if(self.aircraft.oildrums[4].check_can_add(i * a_con)):
                        self.aircraft.oildrums[a].consume_one_second(i * a_con)
                        self.aircraft.oildrums[4].add_one_second(i * a_con)
                if (times == 0):
                    if (self.aircraft.oildrums[b].check_can_consume(cur_oil)):
                        self.aircraft.oildrums[b].consume_one_second(cur_oil)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = cur_oil
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                    if (self.aircraft.oildrums[c].check_can_consume(cur_oil)):
                        self.aircraft.oildrums[c].consume_one_second(cur_oil)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minc = cur_oil
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                for j in range(times+1):
                    if (self.aircraft.oildrums[b].check_can_consume(0.01 * j) and self.aircraft.oildrums[
                        c].check_can_consume(cur_oil - 0.01 * j) and j < times):
                        self.aircraft.oildrums[b].consume_one_second(0.01 * j)
                        self.aircraft.oildrums[c].consume_one_second(cur_oil - 0.01 * j)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = 0.01 * j
                            minc = cur_oil - 0.01 * j
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                    elif (self.aircraft.oildrums[b].check_can_consume(cur_oil) and self.aircraft.oildrums[
                        c].check_can_consume(0) and j == times):
                        self.aircraft.oildrums[b].consume_one_second(cur_oil)
                        self.aircraft.oildrums[c].consume_one_second(0)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = cur_oil
                            minc = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
            self.aircraft.oildrums[a].set_weight(weight_a)
            self.aircraft.oildrums[4].set_weight(weight_4)
            self.aircraft.oildrums[b].set_weight(weight_b)
            self.aircraft.oildrums[c].set_weight(weight_c)
        self.aircraft.oildrums[a].consume_one_second(mina)
        if(a == 0):
            self.aircraft.oildrums[1].add_one_second(mina)
        elif(a==5):
            self.aircraft.oildrums[4].add_one_second(mina)
        self.aircraft.oildrums[b].consume_one_second(minb)
        self.aircraft.oildrums[c].consume_one_second(minc)
        out = []
        for i in range(0, 6):
            if (i == b):
                out.append(minb)
            elif (i == c):
                out.append(minc)
            elif (i == a):
                out.append(mina)
            else:
                out.append(0)
        return minOL, out

    def cal_every_second_best_value_(self, sche, cur_oil, cur_weight_point, cur_t):
        '''
        :param sche: ['0', '1'...]
        :param cur_oil: 当前需要增加的油值
        :param cur_weight_point point 类型
        :return: 输出 质心偏差
        '''
        a = -1
        b = -1 # 主油箱
        c = -1
        which = []
        for i in range(6):
            if(sche[i] == '1'):
                which.append(i)
        for i in which:
            if(i == 0 or i == 5):
                a = i # a 是副油箱
            else:
                if(b == -1):
                    b = i
                    continue
                if(c == -1):
                    c = i
        a_con = 1.1
        if (cur_t == 6465): # 6465
            cur_weight_point_ = self.renew_centroid_for_two()
            print('dist 459', a, b, c, cur_weight_point_.x, cur_weight_point_.y, cur_weight_point_.z,
                  cur_weight_point.x, cur_weight_point.y, cur_weight_point.z)
            print('self.aircraft.oildrums[b].check_can_add(cur_oil)', self.aircraft.oildrums[b].check_can_add(cur_oil))
            print('self.aircraft.oildrums[c].check_can_add(cur_oil))', self.aircraft.oildrums[c].check_can_add(cur_oil))
            times = int(cur_oil / 0.01)
            for j in range(times):
                print(self.aircraft.oildrums[b].check_can_add(0.01 * j) and self.aircraft.oildrums[c].check_can_add(cur_oil - 0.01 * j))
        if(a == 0):
            # 遍历副油箱的供油情况
            timess = int(1.1 / 0.1) # 以0.1
            timess = 2 # 太慢了 加上不着不加上 0.1
            mina = 0
            minb = 0
            minc = 0
            minOL = 100000000
            weight_a = self.aircraft.oildrums[a].get_weight()
            weight_1 = self.aircraft.oildrums[1].get_weight()
            weight_b = self.aircraft.oildrums[b].get_weight()
            weight_c = self.aircraft.oildrums[c].get_weight()
            times = int(cur_oil / 0.01)
            for i in range(timess):
                self.aircraft.oildrums[a].set_weight(weight_a)
                self.aircraft.oildrums[1].set_weight(weight_1)
                self.aircraft.oildrums[b].set_weight(weight_b)
                self.aircraft.oildrums[c].set_weight(weight_c)
                if(self.aircraft.oildrums[a].check_can_add(i * a_con)):
                    if(self.aircraft.oildrums[1].check_can_consume(i * a_con)):
                        self.aircraft.oildrums[a].add_one_second(i * a_con)
                        self.aircraft.oildrums[1].consume_one_second(i * a_con)
                if (times == 0):
                    if (self.aircraft.oildrums[b].check_can_add(cur_oil)):
                        self.aircraft.oildrums[b].add_one_second(cur_oil)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (cur_t == 6465):
                            print('dist', dist, cur_weight_point_.x, cur_weight_point_.y , cur_weight_point_.z,
                                  cur_weight_point.x, cur_weight_point.y, cur_weight_point.z)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = cur_oil
                            minc = 0
                            minOL = dist
                    self.aircraft.oildrums[b].set_weight(weight_b)
                    self.aircraft.oildrums[c].set_weight(weight_c)
                    if (self.aircraft.oildrums[c].check_can_add(cur_oil)):
                        self.aircraft.oildrums[c].add_one_second(cur_oil)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (cur_t == 6465):
                            print('dist', dist, cur_weight_point_.x, cur_weight_point_.y , cur_weight_point_.z,
                                  cur_weight_point.x, cur_weight_point.y, cur_weight_point.z)
                        if (dist < minOL):
                            mina = i * a_con
                            minc = cur_oil
                            minb = 0
                            minOL = dist
                    self.aircraft.oildrums[b].set_weight(weight_b)
                    self.aircraft.oildrums[c].set_weight(weight_c)
                for j in range(times+1):
                    if (self.aircraft.oildrums[b].check_can_add(0.01 * j) and self.aircraft.oildrums[
                        c].check_can_add(cur_oil - 0.01 * j) and j < times):
                        self.aircraft.oildrums[b].add_one_second(0.01 * j)
                        self.aircraft.oildrums[c].add_one_second(cur_oil - 0.01 * j)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (cur_t == 6465):
                            print('dist', dist, cur_weight_point_.x, cur_weight_point_.y , cur_weight_point_.z,
                                  cur_weight_point.x, cur_weight_point.y, cur_weight_point.z)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = 0.01 * j
                            minc = cur_oil - 0.01 * j
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                    elif (self.aircraft.oildrums[b].check_can_add(cur_oil) and self.aircraft.oildrums[
                        c].check_can_add(0) and j == times):
                        self.aircraft.oildrums[b].add_one_second(cur_oil)
                        self.aircraft.oildrums[c].add_one_second(0)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (cur_t == 6465):
                            print('dist', dist, cur_weight_point_.x, cur_weight_point_.y , cur_weight_point_.z,
                                  cur_weight_point.x, cur_weight_point.y, cur_weight_point.z)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = cur_oil
                            minc = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
            self.aircraft.oildrums[a].set_weight(weight_a)
            self.aircraft.oildrums[1].set_weight(weight_1)
            self.aircraft.oildrums[b].set_weight(weight_b)
            self.aircraft.oildrums[c].set_weight(weight_c)
        else: # a = 5
            timess = int(1.1 / 0.01)
            timess = 2
            mina = 0
            minb = 0
            minc = 0
            minOL = 100000000
            weight_a = self.aircraft.oildrums[a].get_weight()
            weight_4 = self.aircraft.oildrums[4].get_weight()
            weight_b = self.aircraft.oildrums[b].get_weight()
            weight_c = self.aircraft.oildrums[c].get_weight()
            times = int(cur_oil / 0.01)
            for i in range(timess):
                self.aircraft.oildrums[a].set_weight(weight_a)
                self.aircraft.oildrums[4].set_weight(weight_4)
                self.aircraft.oildrums[b].set_weight(weight_b)
                self.aircraft.oildrums[c].set_weight(weight_c)
                if(self.aircraft.oildrums[a].check_can_add(i * a_con)):
                    if(self.aircraft.oildrums[4].check_can_consume(i * a_con)):
                        self.aircraft.oildrums[a].add_one_second(i * a_con)
                        self.aircraft.oildrums[4].consume_one_second(i * a_con)
                if (times == 0):
                    if (self.aircraft.oildrums[b].check_can_add(cur_oil)):
                        self.aircraft.oildrums[b].add_one_second(cur_oil)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = cur_oil
                            minc = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                    if (self.aircraft.oildrums[c].check_can_add(cur_oil)):
                        self.aircraft.oildrums[c].add_one_second(cur_oil)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minc = cur_oil
                            minb = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                for j in range(times+1):
                    if (self.aircraft.oildrums[b].check_can_add(0.01 * j) and self.aircraft.oildrums[
                        c].check_can_add(cur_oil - 0.01 * j) and j < times):
                        self.aircraft.oildrums[b].add_one_second(0.01 * j)
                        self.aircraft.oildrums[c].add_one_second(cur_oil - 0.01 * j)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = 0.01 * j
                            minc = cur_oil - 0.01 * j
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
                    elif (self.aircraft.oildrums[b].check_can_add(cur_oil) and self.aircraft.oildrums[
                        c].check_can_add(0) and j == times):
                        self.aircraft.oildrums[b].add_one_second(cur_oil)
                        self.aircraft.oildrums[c].add_one_second(0)
                        cur_weight_point_ = self.renew_centroid_for_two()
                        dist = distance(cur_weight_point_, cur_weight_point)
                        if (cur_t == 6465):
                            print('dist', dist, cur_weight_point_.x, cur_weight_point_.y , cur_weight_point_.z,
                                  cur_weight_point.x, cur_weight_point.y, cur_weight_point.z)
                        if (dist < minOL):
                            mina = i * a_con
                            minb = cur_oil
                            minc = 0
                            minOL = dist
                        self.aircraft.oildrums[b].set_weight(weight_b)
                        self.aircraft.oildrums[c].set_weight(weight_c)
            self.aircraft.oildrums[a].set_weight(weight_a)
            self.aircraft.oildrums[4].set_weight(weight_4)
            self.aircraft.oildrums[b].set_weight(weight_b)
            self.aircraft.oildrums[c].set_weight(weight_c)
        self.aircraft.oildrums[a].add_one_second(mina)
        if(a == 0):
            self.aircraft.oildrums[1].consume_one_second(mina)
        elif(a == 5):
            self.aircraft.oildrums[4].consume_one_second(mina)
        self.aircraft.oildrums[b].add_one_second(minb)
        self.aircraft.oildrums[c].add_one_second(minc)
        out = []
        for i in range(0, 6):
            if (i == b):
                out.append(minb)
            elif (i == c):
                out.append(minc)
            elif (i == a):
                out.append(mina)
            else:
                out.append(0)
        return minOL, out

    def cal_nicePosition_curPosition(self, nPosition):
        # 计算当前重心和理想重心之间的偏差
        '''
        :param nPosition: 是一个list 存储着理想质心的 x y z
        :return: 得到一个list list 中存储着从当前质心指向理想质心的向量偏差
        '''
        p = self.renew_centroid_for_two()
        # delta_weight_point = math.sqrt(math.pow(p.getX() - nPosition[0], 2) + math.pow(p.getY() - nPosition[1], 2) + math.pow(p.getZ() - nPosition[2], 2))
        delta_weight_point = [nPosition[0] - p.getX(), nPosition[1] - p.getY(), nPosition[2] - p.getZ()]
        return delta_weight_point

    def solve_two(self):
        pass

    def cal_60(self, cur_t, nicePosition):
        '''
        计算 当前时刻 往后60s 的理想质心的均值
        nicePosition list
        :return: list 类型的 质心均值
        '''
        # tmp = [0,0,0]
        # for i in range(cur_t,cur_t + 60):
        #     tmp[0] += nicePosition[i][0]
        #     tmp[1] += nicePosition[i][1]
        #     tmp[2] += nicePosition[i][2]
        # tmp_avg = [0,0,0]
        # tmp_avg[0] = tmp[0] / 60
        # tmp_avg[1] = tmp[1] / 60
        # tmp_avg[2] = tmp[2] / 60
        tmp_avg = [nicePosition[cur_t+59][0], nicePosition[cur_t+59][1],nicePosition[cur_t+59][2]]
        return tmp_avg
    def cal_60_1(self, theta60):
        '''
        :param cur_t: t 时刻
        # :param m0: t时刻的质量 list [] 里面存储
        :param theta60: t+60 时刻的角度
        :return: list 类型的 质心
        '''
        v = self.renew_centroid_for_four(theta60) # 以当前质量 也就是 以t 时刻的质量
        tmp = [-v[0], -v[1], -v[2]]
        return tmp




    def renew_oildrum(self, oilPara):
        # param: 消耗油的list kg
        # 第一个油箱开始供油
        tmp = []
        for i in range(6):
            tmp.append(self.aircraft.oildrums[i].volume)
        self.oil.append(tmp)
        self.aircraft.oildrums[0].consume_one_second(oilPara[1])
        self.aircraft.oildrums[1].add_one_second(oilPara[1])
        # 第二个油箱开始供油
        self.aircraft.oildrums[1].consume_one_second(oilPara[2])
        # 第三个油箱开始供油
        self.aircraft.oildrums[2].consume_one_second(oilPara[3])
        # 第四个油箱开始供油
        self.aircraft.oildrums[3].consume_one_second(oilPara[4])
        # 第六个邮箱供油
        self.aircraft.oildrums[5].consume_one_second(oilPara[6])
        self.aircraft.oildrums[4].add_one_second(oilPara[6])
        # 第五个油箱开始供油
        self.aircraft.oildrums[4].consume_one_second(oilPara[5])

    def renew_centroid_for_two(self):
        theta = 0
        central = []
        weight = []
        for j in range(6):
            if (theta >= 0):
                so = centroid_t_to_f(self.aircraft.oildrums[j].length, self.aircraft.oildrums[j].width, self.aircraft.oildrums[j].height, self.aircraft.oildrums[j].volume, theta)
                p = so.solve()
                weight.append(self.aircraft.oildrums[j].weight)
                t = utils.threeDim2threeDim(p, self.aircraft.oildrums[j].get_xyz(), self.aircraft.oildrums[j].get_lwh())
                central.append(point(t[0], t[1], t[2]))
            else:
                weight.append(self.aircraft.oildrums[j].weight)
                so = centroid_t_to_f(self.aircraft.oildrums[j].length, self.aircraft.oildrums[j].width,
                                     self.aircraft.oildrums[j].height, self.aircraft.oildrums[j].volume, math.fabs(theta))
                p = so.solve()
                tmp = point(self.aircraft.oildrums[j].length - p.getX(),p.getY(), p.getZ())
                t = utils.threeDim2threeDim(tmp, self.aircraft.oildrums[j].get_xyz(), self.aircraft.oildrums[j].get_lwh())
                central.append(point(t[0], t[1], t[2]))
        central.append(point(0,0,0)) # 加上飞行器的质心
        weight.append(3000) # 加上飞行器的质量
        tmp = centroid_of_centorids(central, weight) #求多个质心坐标的到一个质心坐标 v point 质心坐标list  t 质量
        return tmp

    def renew_centroid_for_four(self, theta):
        # 返回list类型表示的质心
        central = []
        weight = []
        for j in range(6):
            if (theta >= 0):
                so = centroid_t_to_f(self.aircraft.oildrums[j].length, self.aircraft.oildrums[j].width, self.aircraft.oildrums[j].height, self.aircraft.oildrums[j].volume, theta)
                p = so.solve()
                weight.append(self.aircraft.oildrums[j].weight)
                t = utils.threeDim2threeDim(p, self.aircraft.oildrums[j].get_xyz(), self.aircraft.oildrums[j].get_lwh())
                central.append(point(t[0], t[1], t[2]))
            else:
                weight.append(self.aircraft.oildrums[j].weight)
                so = centroid_t_to_f(self.aircraft.oildrums[j].length, self.aircraft.oildrums[j].width,
                                     self.aircraft.oildrums[j].height, self.aircraft.oildrums[j].volume, math.fabs(theta))
                p = so.solve()
                tmp = point(self.aircraft.oildrums[j].length - p.getX(),p.getY(), p.getZ())
                t = utils.threeDim2threeDim(tmp, self.aircraft.oildrums[j].get_xyz(), self.aircraft.oildrums[j].get_lwh())
                central.append(point(t[0], t[1], t[2]))
        central.append(point(0,0,0)) # 加上飞行器的质心
        weight.append(3000) # 加上飞行器的质量
        tmp = centroid_of_centorids(central, weight) #求多个质心坐标的到一个质心坐标 v point 质心坐标list  t 质量
        return [tmp.getX(), tmp.getY(), tmp.getZ()]


    def renew_centroid(self, theta):
        central = []
        weight = []
        for j in range(6):
            if (theta >= 0):
                so = centroid_t_to_f(self.aircraft.oildrums[j].length, self.aircraft.oildrums[j].width, self.aircraft.oildrums[j].height, self.aircraft.oildrums[j].volume, theta)
                p = so.solve()
                weight.append(self.aircraft.oildrums[j].weight)
                t = utils.threeDim2threeDim(p, self.aircraft.oildrums[j].get_xyz(), self.aircraft.oildrums[j].get_lwh())
                central.append(point(t[0], t[1], t[2]))
            else:
                weight.append(self.aircraft.oildrums[j].weight)
                so = centroid_t_to_f(self.aircraft.oildrums[j].length, self.aircraft.oildrums[j].width,
                                     self.aircraft.oildrums[j].height, self.aircraft.oildrums[j].volume, math.fabs(theta))
                p = so.solve()
                tmp = point(self.aircraft.oildrums[j].length - p.getX(),p.getY(), p.getZ())
                t = utils.threeDim2threeDim(tmp, self.aircraft.oildrums[j].get_xyz(), self.aircraft.oildrums[j].get_lwh())
                central.append(point(t[0], t[1], t[2]))
        central.append(point(0,0,0)) # 加上飞行器的质心
        weight.append(3000) # 加上飞行器的质量
        tmp = centroid_of_centorids(central, weight) #求多个质心坐标的到一个质心坐标 v point 质心坐标list  t 质量
        self.result_one.append([tmp.getX(), tmp.getY(), tmp.getZ()])


    def write_one(self, filename, sheet):
        '''
        将结果数据输出到 excel
        :return:
        '''
        workbook = xlwt.Workbook(encoding='utf-8')
        # 创建一个worksheet
        worksheet = workbook.add_sheet(sheet)

        # 写入excel
        # 参数对应 行, 列, 值
        for i in range(len(self.result_one)):
            for j in range(3):
                worksheet.write(i, j, self.result_one[i][j])
        workbook.save(filename)

    def write_two(self, filename, sheet, sheet2, sheet3):
        '''
        将结果数据输出到 excel
        :return:
        '''
        workbook = xlwt.Workbook(encoding='utf-8')
        # 创建一个worksheet
        worksheet = workbook.add_sheet(sheet)
        worksheet2 = workbook.add_sheet(sheet2)
        worksheet3 = workbook.add_sheet(sheet3)
        # 写入excel
        # 参数对应 行, 列, 值
        for i in range(len(self.result_two)):
            worksheet.write(i, 0, self.result_two[i])
        for i in range(len(self.result_oil)):
            for j in range(6):
                worksheet2.write(i, j, self.result_oil[i][j])
        for i in range(len(self.result_po)):
            for j in range(3):
                worksheet3.write(i, j, self.result_po[i][j])
        workbook.save(filename)



