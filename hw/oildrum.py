#coding=utf-8
from utils import centroid_of_centorids,point
class oildrum:
    def __init__(self, x, y, z, weight, length, width, height, name):
        self.ari_x = x # 相对于 飞行器的坐标
        self.air_y = y
        self.air_z = z
        self.weight = weight
        self.length = length
        self.width = width
        self.height = height
        self.name = name
        self.theta = 0
        self.power_weight = 0
        self.state = -1 # -1 状态表示不在工作
        self.value = [] # 供油值
    def set_other_para(self, U, roh):
        self.U = U  # 供油上限 kg/s
        self.roh = roh  # 液体的密度 kg/m^2
        self.maxWeight = (self.length * self.width * self.height) * self.roh
        self.volume = self.weight / self.roh  # 带有的液体体积

    def get_lwh(self):
        return [self.length, self.width, self.height]
    def get_lhw(self):
        return [self.length, self.height, self.width]
    def get_xyz(self):
        return [self.ari_x, self.air_y, self.air_z]

    def get_U(self):
        return self.U
    def get_state(self):
        return self.state
    def turn_on(self):
        if self.state == -1:
            self.state = 0
        else:
            self.state += 1
    def turn_off(self):
        if self.state != -1:
            self.state = -1



    def set_theta(self, theta):
        self.theta = theta

    def consume_one_second(self, con):
        '''
        消耗的体积 TODO -1 -2 判断
        :param con: kg
        :return:
        '''
        if con > self.U:
            # print('[ERROR] con bigger than self.U', con, self.U)
            return -1
        if self.weight - con < 0:
            #print('[ERROR] more than enpty()', self.name)
            return -2

        self.weight -= con
        self.volume = self.weight / self.roh
        return 1
    def check_can_consume(self, con):
        if con > self.U:
            return False
        if self.weight - con < 0:
            return False
        return True
    def check_can_add(self, other_con):
        if other_con + self.weight > self.maxWeight:
            return False
        return True

    def set_weight(self, weight):
        self.weight = weight
        self.volume = self.weight / self.roh

    def get_weight(self):
        return self.weight

    def add_one_second(self, other_con):
        '''
        :param other_con: 别的油桶的消耗 kg
        :return:
        '''
        if other_con + self.weight > self.maxWeight:
            # print('[ERROR] other_con bigger than self.maxWeight', other_con, self.weight, self.maxWeight)
            return -1
        self.weight += other_con
        self.volume = self.weight / self.roh
        return 1
    def cal_one_kg_pw(self):
        # 计算减少单位质量造成的飞行器质心偏移
        v = []
        v.append(point(self.ari_x, self.air_y, self.air_z))
        v.append(point(0,0,0))
        w = []
        w.append(100) # 表示这个点增加100的向量的反方向
        w.append(3000)
        p = centroid_of_centorids(v, w)
        p = point(-p.getX(), -p.getY(), -p.getZ())
        # p.norm()
        self.power_weight = p
        # print(self.name, p.getX(), p.getY(), p.getZ())
    def get_pw(self):
        return self.power_weight

    def cal_one_kg_pw_cur_weight_point(self, p):
        '''
        :param p: 计算1kg减少的权重对当时质心产生的影响
        好像不能这么做。在aircraft里面做
        :return:
        '''
        pass






