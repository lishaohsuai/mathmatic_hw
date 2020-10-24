#coding = utf-8
import oildrum
import utils as ut
from utils import cal_included_angle,point
import math
from core_question import centroid_t_to_f

class aircraft:
    def __init__(self, m):
        self.m = m # 飞行器的质量
        self.oildrums = [] # 总共的油桶数量
        self.local_x = 0
        self.local_y = 0
        self.local_z = 0
    def add_oildrum(self, o):
        '''
        :param o: oildrum 类对象 一次只能增加一个
        :return:
        '''
        self.oildrums.append(o)


    def choose_solution_for_60(self, vec, oil60):
        '''vec 前面60个质心的均值 的偏移, oil_con oil60表示飞机此刻需要的油水 list
        :return list [] 里面存储着3个油桶序列
        '''
        # 第一步生成所有方案
        one, two, three = self.gen_sttr()
        # 第二步初步校验所有方案（数量）
        # one_new = []
        # two_new = []
        three_new = []
        # for i in range(len(one)):
        #     l = list(one[i])
        #     if(self.check_scheme_legi(l)):
        #         one_new.append(l)
        # for i in range(len(two)):
        #     l = list(two[i])
        #     if(self.check_scheme_legi(l)):
        #         two_new.append(l)
        for i in range(len(three)):
            l = list(three[i])
            if(self.check_scheme_legi(l)):
                three_new.append(l)
        # 生了list的方案
        # 计算每个油桶单独工作生成的质心偏移标量
        projection = []
        flags = []
        for i in range(6):
            flag, proj = self.scheme_single(vec,i) ######
            projection.append(proj)
            flags.append(flag)
        two = []
        one = []
        three = []
        # 判断是否有将满的情况或者是将空的情况
        # for i in range(len(two_new)):
        #     if(self.check_scheme_legi2(two_new[i], flags)): # 2 的情况可以不检查？
        #         two.append(two_new[i])
        # for i in range(len(one_new)):
        #     if(self.check_scheme_legi2(one_new[i], flags)):
        #         one.append(one_new[i])
        # for i in range(len(three_new)):
        #     if(self.check_scheme_legi2(three_new[i], flags)):
        #         three.append(three_new[i])
        # 检查方案的供油是否能够满足飞机的消耗 不满足的剔除
        # 将所有方案杂合在一起排序判断
        # 暂时放弃 一个油箱和两个油箱的考虑
        # for i in range(len(one)):
        #     if(self.check_scheme_legi3(one[i], oil_con)):
        #         can_do.append(one[i])
        # for i in range(len(two)):
        #     if(self.check_scheme_legi3(two[i], oil_con)):
        #         can_do.append(two[i])
        # new_three = []
        # for i in range(len(three)):
        #     if(self.check_scheme_legi3(three[i], oil_con)): # 都能覆盖下次飞机油耗
        #         new_three.append(three[i])
        new_three = []
        for i in range(len(three_new)):
            if(self.check_scheme_legi4(three_new[i], oil60)):
                new_three.append(three_new[i])
        # 现在three 里面的方案都可以cover掉60s的数据
        if(len(new_three) == 0):
            print('[ERROR ERROR] can not cover 60s volume')
            # 打印所有的油箱里面的油
            for i in range(6):
                print(self.oildrums[i].name, self.oildrums[i].weight)
            print( flags, projection)
            print()
            return [-1, -1, -1]
        # 生成list 里面存储字典 {'st': ['0','0','0','0','1','0'], 'leng': 模长}
        cando = []
        for i in range(len(new_three)):
            cando.append(self.gen_mold_length(new_three[i], projection, flags))
        # 进行排序 这种排序方式是有问题的 太过于极端应该分成60s，然后只选择3个油桶供油，
        # 选择极端  动态调整
        new_cando = sorted(cando, key=lambda i: i['leng'], reverse=True) # 模长从大到小排序
        # 进行尝试减油操作 选择new_cando 中的第一个方案进行60s的生成
        return new_cando[0]['st']




    def check_scheme_legi4(self, sche, oil60):
        '''
        查看两个主油箱能否覆盖掉  60s 内的油耗
        :param sche: list 字符
        :param oil60: 60s 的油耗 list
        :return: true or false
        '''
        a = 0
        b = 0
        which = []
        for i in range(1,5):
            if(sche[i] == '1'):
                which.append(i)
        # print('[debug] ', sche)
        a = which[0]
        b = which[1]
        weight_a = self.oildrums[a].get_weight()
        weight_b = self.oildrums[b].get_weight()

        # 得到两个油箱 查看这两个油箱是否能cover这60s内的输出 一个油箱极限输出 或 输出满足要求的 另一个邮箱再输出剩下的油 虽然有点过压力
        # 但是暂时没有更好的办法了
        check = True
        for i in range(60):
            if(self.oildrums[a].get_U() >= oil60[i]):
                if(not self.oildrums[a].check_can_consume(oil60[i])):
                    check = False
                    break
            else:
                if(not self.oildrums[a].check_can_consume(self.oildrums[a].get_U())):
                    check = False
                    break
                else:
                    if(not self.oildrums[b].check_can_consume(oil60[i] - self.oildrums[a].get_U())):
                        check = False
                        break
        self.oildrums[a].set_weight(weight_a)
        self.oildrums[b].set_weight(weight_b)
        if(not check):
            # 看来a 不能完全覆盖
            check = True
            for i in range(60):
                if (self.oildrums[b].get_U() >= oil60[i]):
                    if (not self.oildrums[b].check_can_consume(oil60[i])):
                        check = False
                        break
                else:
                    if (not self.oildrums[b].consume_one_second(self.oildrums[b].get_U())):
                        check = False
                        break
                    else:
                        if (not self.oildrums[a].consume_one_second(oil60[i] - self.oildrums[b].get_U())):
                            check = False
                            break
        self.oildrums[a].set_weight(weight_a)
        self.oildrums[b].set_weight(weight_b)
        if(not check):
            return False
        return True # 倾向于另选方案

    def gen_mold_length(self, cando, projection, flags):
        '''
        :param cando: 方案所代表的 list
        :param projection: 单个起作用的模长 list
        :param flags: 单个是否能起作用的 bool list
        :return:  方案投影在理想向量模长
        '''
        rlt = {}
        sumPorj = 0
        for i in range(6):
            if cando[i] == '1' and flags[i]:
                sumPorj += projection[i]
        rlt['leng'] = sumPorj
        rlt['st'] = cando
        return rlt


    def check_scheme_legi3(self, sche, oil_con):
        '''
        对于是否能cover 飞机燃油消耗的判断 不单单是此次耗油覆盖
        :param sche: list 表示的燃油方案
        :param oil_con: 此时的燃油消耗
        :return: true or false
        '''
        ability = 0
        for i in range(1,5): # 主供油油箱
            if(sche[i] == '1'):
                ability += self.oildrums[i].get_U()
        if ability >= oil_con:
            return True
        return False



    def check_scheme_legi2(self, sche, flags):
        '''
        判断是否有将满的情况或者是将空的情况
        :param sche: list 表示的方案
        :param flags: 6个油箱的值
        :return: true of false
        '''
        for i in range(6):
            if(sche[i] == '1'):
                if flags[i] == False:
                    return False
        return True

    def check_scheme_legi(self, sche):
        '''
        初步校验方案的合法性
        首先校验个数 是否合法 开头和中间
        :param sche: list 表示的方案值
        :return: true or false
        '''
        headtail_num = 0
        mid_num = 0
        for i in range(1,5):
            if(sche[i] == '1'):
                mid_num+=1
        if(sche[0]=='1'):
            headtail_num+=1
        if(sche[5]=='1'):
            headtail_num+=1
        # 判断总共的大小是否符合要求
        if(mid_num == 3):
            return False
        elif(mid_num == 0):
            return False
        elif(mid_num == 1): # TODO
            return False
        return True
        # 因为生成的方案最多有3个发动机在工作所以总个数会不会大于3是不用判断的

    def gen_sttr(self):
        '''
        :param vec: 理想向量
        :return:
        '''
        solution_use_one = ut.perm_main('000001')
        solution_use_two = ut.perm_main('000011')
        solution_use_three = ut.perm_main('000111')
        return solution_use_one, solution_use_two, solution_use_three


    def scheme_single(self, vec, index):
        '''
        方案3 单独使用油箱index[0..5] 计算投影在偏差向量的长度
        :param vec: 理想向量之间的偏差
        :param index: 选中的油箱序号
        :return:
        '''
        if index == 0:
            # 选中1油桶不能单独供油
            return self.scheme_1(vec)
        elif index == 1:
            return self.scheme_2(vec)
        elif index == 2:
            return self.scheme_3(vec)
        elif index == 3:
            return self.scheme_4(vec)
        elif index == 4:
            return self.scheme_5(vec)
        elif index == 5:
            return self.scheme_6(vec)

    def scheme_1(self, vec):
        '''
        不能独立的方案  使用油箱1 供给给油箱2 产生的向量
        :return:
        '''
        cur_weight_point, central, weight = self.renew_centroid()
        if self.oildrums[0].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[0].add_one_second(0.01)  # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(
            math.radians(theta))
        # ------ 对于油桶2的影响
        if self.oildrums[1].add_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[1].consume_one_second(0.01)  # 还原质量
        vv = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(vv, vec)
        # 投影 标量已经带上正负
        projection_ = math.sqrt(math.pow(vv[0], 2) + math.pow(vv[1], 2) + math.pow(vv[2], 2)) * math.cos(
            math.radians(theta))
        projection = projection + projection_
        return True, projection

    def scheme_2(self, vec):
        '''
        方案1 采用单独使用 油箱2 的方式 计算投影在偏差向量的长度 个人觉得还是不要对圆心质心求偏移向量了 还是对真实情况减去1kg
        然后再加上1kg 还原
        :param vec: 偏差向量 list
        :return: 一个标量 带符号的书
        '''
        cur_weight_point, central, weight = self.renew_centroid()
        if self.oildrums[1].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[1].add_one_second(0.01) # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
               cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(math.radians(theta))
        return True, projection

    def scheme_3(self, vec):
        '''
        方案3 单独使用油箱3 计算投影在偏差向量的长度
        :param vec:
        :return:
        '''
        cur_weight_point, central, weight = self.renew_centroid()
        if self.oildrums[2].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[2].add_one_second(0.01) # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
               cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(math.radians(theta))
        return True, projection

    def scheme_4(self, vec):
        '''
        方案2 单独使用油箱4 计算投影在偏差向量的长度
        :param vec:偏差向量 list
        :return:
        '''
        cur_weight_point, central, weight = self.renew_centroid()
        if self.oildrums[3].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[3].add_one_second(0.01)  # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(
            math.radians(theta))
        return True, projection

    def scheme_5(self, vec):
        '''
        方案1 采用单独使用 油箱2 的方式 计算投影在偏差向量的长度
        :param vec: 偏差向量 list
        :return: 一个标量 带符号的书
        '''
        cur_weight_point, central, weight = self.renew_centroid()
        if self.oildrums[4].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[4].add_one_second(0.01)  # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(
            math.radians(theta))
        return True, projection

    def scheme_6(self, vec):
        '''
        不能独立的方案  使用油箱6 供给给油箱5 产生的向量
        :return:
        '''
        cur_weight_point, central, weight = self.renew_centroid()
        if self.oildrums[5].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[5].add_one_second(0.01)  # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(
            math.radians(theta))
        # ------ 对于油桶5的影响
        if self.oildrums[4].add_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[4].consume_one_second(0.01)  # 还原质量
        vv = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
              cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(vv, vec)
        # 投影 标量已经带上正负
        projection_ = math.sqrt(math.pow(vv[0], 2) + math.pow(vv[1], 2) + math.pow(vv[2], 2)) * math.cos(
            math.radians(theta))
        projection = projection + projection_
        return True, projection


    def choose_solution_for_60_(self, vec, oil60):
        '''vec 前面60个质心的均值 的偏移, oil_con oil60表示飞机此刻需要的油水 list
        :return list [] 里面存储着3个油桶序列
        '''
        # 第一步生成所有方案
        one, two, three = self.gen_sttr()
        # 第二步初步校验所有方案（数量）
        three_new = []
        for i in range(len(three)):
            l = list(three[i])
            if(self.check_scheme_legi(l)):
                three_new.append(l)
        # 生了list的方案
        # 计算每个油桶单独工作生成的质心偏移标量
        projection = []
        flags = []
        for i in range(6):
            flag, proj = self.scheme_single_(vec,i) ######
            projection.append(proj)
            flags.append(flag)
        two = []
        one = []
        three = []
        new_three = []
        for i in range(len(three_new)):
            if(self.check_scheme_legi4_(three_new[i], oil60)):
                new_three.append(three_new[i])
        # 现在three 里面的方案都可以cover掉60s的数据
        if(len(new_three) == 0):
            print('[ERROR ERROR] can not cover 60s volume')
            # 打印所有的油箱里面的油
            for i in range(6):
                print(self.oildrums[i].name, self.oildrums[i].weight)
            print(flags, projection)
            print()
            return [-1, -1, -1]
        # 生成list 里面存储字典 {'st': ['0','0','0','0','1','0'], 'leng': 模长}
        cando = []
        for i in range(len(new_three)):
            cando.append(self.gen_mold_length(new_three[i], projection, flags)) # 可以采用原函数
        # 进行排序 这种排序方式是有问题的 太过于极端应该分成60s，然后只选择3个油桶供油，
        # 选择极端  动态调整
        new_cando = sorted(cando, key=lambda i: i['leng'], reverse=True) # 模长从大到小排序
        # 进行尝试减油操作 选择new_cando 中的第一个方案进行60s的生成
        return new_cando[0]['st']

    def choose_solution_for_60_for_four(self, vec, oil60, theta):
        '''vec 前面60个质心的均值 的偏移, oil_con oil60表示飞机此刻需要的油水 list
            theta 表示角度
        :return list [] 里面存储着3个油桶序列
        '''
        # 第一步生成所有方案
        one, two, three = self.gen_sttr()
        # 第二步初步校验所有方案（数量）
        three_new = []
        for i in range(len(three)):
            l = list(three[i])
            if(self.check_scheme_legi(l)):
                three_new.append(l)
        # 生了list的方案
        # 计算每个油桶单独工作生成的质心偏移标量
        projection = []
        flags = []
        for i in range(6):
            flag, proj = self.scheme_single_for_four(vec,i, theta) # 修改完毕
            projection.append(proj)
            flags.append(flag)
        two = []
        one = []
        three = []
        new_three = []
        for i in range(len(three_new)):
            if(self.check_scheme_legi4_for_four(three_new[i], oil60)):
                new_three.append(three_new[i])
        # 现在three 里面的方案都可以cover掉60s的数据
        if(len(new_three) == 0):
            print('[ERROR ERROR] can not cover 60s volume')
            # 打印所有的油箱里面的油
            for i in range(6):
                print(self.oildrums[i].name, self.oildrums[i].weight)
            print(flags, projection)
            print()
            return [-1, -1, -1]
        # 生成list 里面存储字典 {'st': ['0','0','0','0','1','0'], 'leng': 模长}
        cando = []
        for i in range(len(new_three)):
            cando.append(self.gen_mold_length(new_three[i], projection, flags)) # 可以采用原函数 可以用原函数
        # 进行排序 这种排序方式是有问题的 太过于极端应该分成60s，然后只选择3个油桶供油，
        # 选择极端  动态调整
        new_cando = sorted(cando, key=lambda i: i['leng'], reverse=True) # 模长从大到小排序
        # 进行尝试减油操作 选择new_cando 中的第一个方案进行60s的生成
        return new_cando[0]['st']

    def scheme_single_for_four(self, vec, index, theta):
        '''
        方案3 单独使用油箱index[0..5] 计算投影在偏差向量的长度
        :param vec: 理想向量之间的偏差
        :param index: 选中的油箱序号
        :return:
        '''
        if index == 0:
            # 选中1油桶不能单独供油
            return self.scheme_1_for_four(vec, theta)
        elif index == 1:
            return self.scheme_2_for_four(vec, theta)
        elif index == 2:
            return self.scheme_3_for_four(vec, theta)
        elif index == 3:
            return self.scheme_4_for_four(vec, theta)
        elif index == 4:
            return self.scheme_5_for_four(vec, theta)
        elif index == 5:
            return self.scheme_6_for_four(vec, theta)

    def scheme_1_for_four(self, vec, theta):
        '''
        不能独立的方案  使用油箱1 供给给油箱2 产生的向量
        :return:
        '''
        cur_weight_point, central, weight = self.renew_centroid_for_four(theta)
        if self.oildrums[0].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid_for_four(theta)
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[0].add_one_second(0.01)  # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta_ = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(
            math.radians(theta_))
        # ------ 对于油桶2的影响
        if self.oildrums[1].add_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid_for_four(theta)
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[1].consume_one_second(0.01)  # 还原质量
        vv = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta_ = cal_included_angle(vv, vec)
        # 投影 标量已经带上正负
        projection_ = math.sqrt(math.pow(vv[0], 2) + math.pow(vv[1], 2) + math.pow(vv[2], 2)) * math.cos(
            math.radians(theta_))
        projection = projection + projection_
        return True, projection


    def scheme_2_for_four(self, vec, theta):
        '''
        方案1 采用单独使用 油箱2 的方式 计算投影在偏差向量的长度 个人觉得还是不要对圆心质心求偏移向量了 还是对真实情况减去1kg
        然后再加上1kg 还原
        :param vec: 偏差向量 list
        :return: 一个标量 带符号的书
        '''
        cur_weight_point, central, weight = self.renew_centroid_for_four(theta)
        if self.oildrums[1].consume_one_second(0.01) < 0: # 不能减少单位质量
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid_for_four(theta)
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[1].add_one_second(0.01) # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
               cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta_ = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(math.radians(theta_))
        return True, projection

    def scheme_3_for_four(self, vec, theta):
        '''
        方案3 单独使用油箱3 计算投影在偏差向量的长度
        :param vec:
        :return:
        '''
        cur_weight_point, central, weight = self.renew_centroid_for_four(theta)
        if self.oildrums[2].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid_for_four(theta)
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[2].add_one_second(0.01) # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
               cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta_ = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(math.radians(theta_))
        return True, projection

    def scheme_4_for_four(self, vec, theta):
        '''
        方案2 单独使用油箱4 计算投影在偏差向量的长度
        :param vec:偏差向量 list
        :return:
        '''
        cur_weight_point, central, weight = self.renew_centroid_for_four(theta)
        if self.oildrums[3].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid_for_four(theta)
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[3].add_one_second(0.01)  # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta_ = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(
            math.radians(theta_))
        return True, projection

    def scheme_5_for_four(self, vec, theta):
        '''
        方案1 采用单独使用 油箱2 的方式 计算投影在偏差向量的长度
        :param vec: 偏差向量 list
        :return: 一个标量 带符号的书
        '''
        cur_weight_point, central, weight = self.renew_centroid_for_four(theta)
        if self.oildrums[4].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid_for_four(theta)
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[4].add_one_second(0.01)  # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta_ = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(
            math.radians(theta_))
        return True, projection

    def scheme_6_for_four(self, vec, theta):
        '''
        不能独立的方案  使用油箱6 供给给油箱5 产生的向量
        :return:
        '''
        cur_weight_point, central, weight = self.renew_centroid_for_four(theta)
        if self.oildrums[5].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid_for_four(theta)
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[5].add_one_second(0.01)  # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta_ = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(
            math.radians(theta_))
        # ------ 对于油桶5的影响
        if self.oildrums[4].add_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid_for_four(theta)
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[4].consume_one_second(0.01)  # 还原质量
        vv = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
              cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta_ = cal_included_angle(vv, vec)
        # 投影 标量已经带上正负
        projection_ = math.sqrt(math.pow(vv[0], 2) + math.pow(vv[1], 2) + math.pow(vv[2], 2)) * math.cos(
            math.radians(theta_))
        projection = projection + projection_
        return True, projection

    def check_scheme_legi_(self, sche):
        '''
        初步校验方案的合法性
        首先校验个数 是否合法 开头和中间
        :param sche: list 表示的方案值
        :return: true or false
        '''
        headtail_num = 0
        mid_num = 0
        for i in range(1,5):
            if(sche[i] == '1'):
                mid_num+=1
        if(sche[0]=='1'):
            headtail_num+=1
        if(sche[5]=='1'):
            headtail_num+=1
        # 判断总共的大小是否符合要求
        if(mid_num == 3):
            return False
        elif(mid_num == 0):
            return False
        elif(mid_num == 1): # TODO
            return False
        return True
        # 因为生成的方案最多有3个发动机在工作所以总个数会不会大于3是不用判断的
    def scheme_single_(self, vec, index):
        '''
        方案3 单独使用油箱index[0..5] 计算投影在偏差向量的长度
        :param vec: 理想向量之间的偏差
        :param index: 选中的油箱序号
        :return:
        '''
        if index == 0:
            # 选中1油桶不能单独供油
            return self.scheme_1_(vec)
        elif index == 1:
            return self.scheme_2_(vec)
        elif index == 2:
            return self.scheme_3_(vec)
        elif index == 3:
            return self.scheme_4_(vec)
        elif index == 4:
            return self.scheme_5_(vec)
        elif index == 5:
            return self.scheme_6_(vec)

    def renew_centroid(self):
        theta = 0
        central = []
        weight = []
        for j in range(6):
            if (theta >= 0):
                so = centroid_t_to_f(self.oildrums[j].length, self.oildrums[j].width, self.oildrums[j].height, self.oildrums[j].volume, theta)
                p = so.solve()
                weight.append(self.oildrums[j].weight)
                t = ut.threeDim2threeDim(p, self.oildrums[j].get_xyz(), self.oildrums[j].get_lwh())
                central.append(ut.point(t[0], t[1], t[2]))
            else:
                weight.append(self.oildrums[j].weight)
                so = centroid_t_to_f(self.oildrums[j].length, self.oildrums[j].width,
                                     self.oildrums[j].height, self.oildrums[j].volume, math.fabs(theta))
                p = so.solve()
                tmp = point(self.oildrums[j].length - p.getX(),p.getY(), p.getZ())
                t = ut.threeDim2threeDim(tmp, self.oildrums[j].get_xyz(), self.oildrums[j].get_lwh())
                central.append(point(t[0], t[1], t[2]))
        central.append(ut.point(0,0,0)) # 加上飞行器的质心
        weight.append(3000) # 加上飞行器的质量
        cur_weight_point = ut.centroid_of_centorids(central, weight) #求多个质心坐标的到一个质心坐标 v point 质心坐标list  t 质量
        return cur_weight_point, central, weight

    def renew_centroid_for_four(self, theta):
        central = []
        weight = []
        for j in range(6):
            if (theta >= 0):
                so = centroid_t_to_f(self.oildrums[j].length, self.oildrums[j].width, self.oildrums[j].height, self.oildrums[j].volume, theta)
                p = so.solve()
                weight.append(self.oildrums[j].weight)
                t = ut.threeDim2threeDim(p, self.oildrums[j].get_xyz(), self.oildrums[j].get_lwh())
                central.append(ut.point(t[0], t[1], t[2]))
            else:
                weight.append(self.oildrums[j].weight)
                so = centroid_t_to_f(self.oildrums[j].length, self.oildrums[j].width,
                                     self.oildrums[j].height, self.oildrums[j].volume, math.fabs(theta))
                p = so.solve()
                tmp = point(self.oildrums[j].length - p.getX(),p.getY(), p.getZ())
                t = ut.threeDim2threeDim(tmp, self.oildrums[j].get_xyz(), self.oildrums[j].get_lwh())
                central.append(point(t[0], t[1], t[2]))
        central.append(ut.point(0,0,0)) # 加上飞行器的质心
        weight.append(3000) # 加上飞行器的质量
        cur_weight_point = ut.centroid_of_centorids(central, weight) #求多个质心坐标的到一个质心坐标 v point 质心坐标list  t 质量
        return cur_weight_point, central, weight

    def scheme_1_(self, vec):
        '''
        不能独立的方案  使用油箱1 供给给油箱2 产生的向量
        :return:
        '''
        cur_weight_point, central, weight = self.renew_centroid()
        if self.oildrums[0].add_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[0].consume_one_second(0.01)  # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(
            math.radians(theta))
        # ------ 对于油桶2的影响
        if self.oildrums[1].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[1].add_one_second(0.01)  # 还原质量
        vv = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(vv, vec)
        # 投影 标量已经带上正负
        projection_ = math.sqrt(math.pow(vv[0], 2) + math.pow(vv[1], 2) + math.pow(vv[2], 2)) * math.cos(
            math.radians(theta))
        projection = projection + projection_
        return True, projection

    def scheme_2_(self, vec):
        '''
        方案1 采用单独使用 油箱2 的方式 计算投影在偏差向量的长度 个人觉得还是不要对圆心质心求偏移向量了 还是对真实情况减去1kg
        然后再加上1kg 还原
        :param vec: 偏差向量 list
        :return: 一个标量 带符号的书
        '''
        cur_weight_point, central, weight = self.renew_centroid()
        if self.oildrums[1].add_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[1].consume_one_second(0.01) # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
               cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(math.radians(theta))
        return True, projection

    def scheme_3_(self, vec):
        '''
        方案3 单独使用油箱3 计算投影在偏差向量的长度
        :param vec:
        :return:
        '''
        cur_weight_point, central, weight = self.renew_centroid()
        if self.oildrums[2].add_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[2].consume_one_second(0.01) # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
               cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(math.radians(theta))
        return True, projection

    def scheme_4_(self, vec):
        '''
        方案2 单独使用油箱4 计算投影在偏差向量的长度
        :param vec:偏差向量 list
        :return:
        '''
        cur_weight_point, central, weight = self.renew_centroid()
        if self.oildrums[3].add_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[3].consume_one_second(0.01)  # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(
            math.radians(theta))
        return True, projection

    def scheme_5_(self, vec):
        '''
        方案1 采用单独使用 油箱2 的方式 计算投影在偏差向量的长度
        :param vec: 偏差向量 list
        :return: 一个标量 带符号的书
        '''
        cur_weight_point, central, weight = self.renew_centroid()
        if self.oildrums[4].add_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[4].consume_one_second(0.01)  # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(
            math.radians(theta))
        return True, projection

    def scheme_6_(self, vec):
        '''
        不能独立的方案  使用油箱6 供给给油箱5 产生的向量
        :return:
        '''
        cur_weight_point, central, weight = self.renew_centroid()
        if self.oildrums[5].add_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[5].consume_one_second(0.01)  # 还原质量
        v = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
             cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(v, vec)
        # 投影 标量已经带上正负
        projection = math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2) + math.pow(v[2], 2)) * math.cos(
            math.radians(theta))
        # ------ 对于油桶5的影响
        if self.oildrums[4].consume_one_second(0.01) < 0:
            return False, 0
        # 重新计算重心
        cur_weight_point_, central_, weight_ = self.renew_centroid()
        # 根据两次计算得到 飞行器 质心偏移向量
        self.oildrums[4].add_one_second(0.01)  # 还原质量
        vv = [cur_weight_point_.getX() - cur_weight_point.getX(), cur_weight_point_.getY() - cur_weight_point.getY(),
              cur_weight_point_.getZ() - cur_weight_point.getZ()]
        theta = cal_included_angle(vv, vec)
        # 投影 标量已经带上正负
        projection_ = math.sqrt(math.pow(vv[0], 2) + math.pow(vv[1], 2) + math.pow(vv[2], 2)) * math.cos(
            math.radians(theta))
        projection = projection + projection_
        return True, projection

    def check_scheme_legi4_(self, sche, oil60):
        '''
        查看两个主油箱能否覆盖掉  60s 内的增加油耗
        :param sche: list 字符
        :param oil60: 60s 的油耗 list
        :return: true or false
        '''
        a = 0
        b = 0
        which = []
        for i in range(1,5):
            if(sche[i] == '1'):
                which.append(i)
        # print('[debug] ', sche)
        a = which[0]
        b = which[1]
        weight_a = self.oildrums[a].get_weight()
        weight_b = self.oildrums[b].get_weight()

        # 得到两个油箱 查看这两个油箱是否能cover这60s内的输出 一个油箱极限输出 或 输出满足要求的 另一个邮箱再输出剩下的油 虽然有点过压力
        # 但是暂时没有更好的办法了
        check = True
        for i in range(60):
            if(self.oildrums[a].get_U() >= oil60[i]):
                if(not self.oildrums[a].check_can_add(oil60[i])):
                    check = False
                    break
            else:
                if(not self.oildrums[a].check_can_add(self.oildrums[a].get_U())):
                    check = False
                    break
                else:
                    if(not self.oildrums[b].check_can_add(oil60[i] - self.oildrums[a].get_U())):
                        check = False
                        break
        self.oildrums[a].set_weight(weight_a)
        self.oildrums[b].set_weight(weight_b)
        if(not check):
            # 看来a 不能完全覆盖
            check = True
            for i in range(60):
                if (self.oildrums[b].get_U() >= oil60[i]):
                    if (not self.oildrums[b].check_can_add(oil60[i])):
                        check = False
                        break
                else:
                    if (not self.oildrums[b].check_can_add(self.oildrums[b].get_U())):
                        check = False
                        break
                    else:
                        if (not self.oildrums[a].check_can_add(oil60[i] - self.oildrums[b].get_U())):
                            check = False
                            break
        self.oildrums[a].set_weight(weight_a)
        self.oildrums[b].set_weight(weight_b)
        if(not check):
            return False
        return True # 倾向于另选方案

    def check_scheme_legi4_for_four(self, sche, oil60):
        '''
        查看两个主油箱能否覆盖掉  60s 内的油耗
        :param sche: list 字符
        :param oil60: 60s 的油耗 list
        :return: true or false
        '''
        a = 0
        b = 0
        which = []
        for i in range(1,5):
            if(sche[i] == '1'):
                which.append(i)
        # print('[debug] ', sche)
        a = which[0]
        b = which[1]
        weight_a = self.oildrums[a].get_weight()
        weight_b = self.oildrums[b].get_weight()

        # 得到两个油箱 查看这两个油箱是否能cover这60s内的输出 一个油箱极限输出 或 输出满足要求的 另一个邮箱再输出剩下的油 虽然有点过压力
        # 但是暂时没有更好的办法了
        check = True
        for i in range(60):
            if(self.oildrums[a].get_U() >= oil60[i]):
                if(not self.oildrums[a].check_can_consume(oil60[i])):
                    check = False
                    break
            else:
                if(not self.oildrums[a].check_can_consume(self.oildrums[a].get_U())):
                    check = False
                    break
                else:
                    if(not self.oildrums[b].check_can_consume(oil60[i] - self.oildrums[a].get_U())):
                        check = False
                        break
        self.oildrums[a].set_weight(weight_a)
        self.oildrums[b].set_weight(weight_b)
        if(not check):
            # 看来a 不能完全覆盖
            check = True
            for i in range(60):
                if (self.oildrums[b].get_U() >= oil60[i]):
                    if (not self.oildrums[b].check_can_consume(oil60[i])):
                        check = False
                        break
                else:
                    if (not self.oildrums[b].consume_one_second(self.oildrums[b].get_U())):
                        check = False
                        break
                    else:
                        if (not self.oildrums[a].consume_one_second(oil60[i] - self.oildrums[b].get_U())):
                            check = False
                            break
        self.oildrums[a].set_weight(weight_a)
        self.oildrums[b].set_weight(weight_b)
        if(not check):
            return False
        return True # 倾向于另选方案


