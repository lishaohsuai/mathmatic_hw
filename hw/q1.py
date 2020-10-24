#coding=utf-8
import math
from utils import centroid_of_convex_polygon_list

'''
将point 改成 v 防止python 冲突
'''

'''
v : 油体积
box: [x z y]  长高宽
a: 倾斜角度
return t [x, z]
'''
def box_centre(v,box,a):
    s = v / box[2]
    solution = chose_sloution(s,box[:2],a)
    solutio_list = [solution_0,solution_1,solution_2,solution_3,solution_4]
    t = solutio_list[solution](s,box[:2],a)
    return t

#输入油箱剩余油的面积，飞机仰角，以及油箱长以及高,返回需要调用的解决方法
def chose_sloution(s,box,a):
    a0 = get_a0(box) # 得到对角线角度
    if a == 0:
        print('倾斜角0度')
        return 0
    # 得到临界的面积 四种临界面积
    s1 = get_squre1(a,box) # 角度小 容量没有超过一半
    s2 = get_squre2(a,box) #
    s3 = get_squre3(a,box)
    s4 = get_squre4(a,box)
    if a <= a0:
        if s <= s1:
            return 4 # 角度小 容量没有超过一半
        elif s <= s2: # 角度小 容量超过一半
            return 1
        else:
            return 2
    else:
        if s < s3:
            return 4
        elif s < s4 :
            return 3
        else:
            return 2
#获取油箱a0角度
#box[1]为油箱x轴方向长度，box[2] 为油箱z轴方向长度
def get_a0(box):
    return math.degrees(math.atan(box[1] / box[0] ))

#获取临界面积
#box[1]为油箱x轴方向长度，box[2] 为油箱z轴方向长度
def get_squre1(a,box):
    '''
    第一种情况  对应word 第一种情况的面积  感觉有点小问题 box[0] * math.tan(math.radians(a)) 会不会比 box[1] 高？
    :param a: 角度 如果角度比临界角度小时不会有问题的
    :param box: 长 & 高
    :return:
    '''
    return 0.5 * box[0] * box[0] * math.tan(math.radians(a))

def get_squre2(a,box):
    '''
    第二种情况 对应word 第二种情况的面积  跟第一种情况一样的问题?  box[0] * math.tan(math.radians(a)) 会不会比 box[1] 高？
    :param a:
    :param box:
    :return:
    '''
    return box[0] * box[1] - 0.5 * box[0] * box[0] * math.tan(math.radians(a))

def get_squre3(a,box):
    '''
    第3种情况 对应word 第四种情况 跟第一种情况一样的问题?  box[1] / math.tan(math.radians(a)) 会不会比 box[0] 长？
    :param a:
    :param box:
    :return:
    '''
    return box[1] * box[1] / math.tan(math.radians(a)) * 0.5

def get_squre4(a,box):
    '''
    第4种情况 对应word 第三种情况  box[1] / math.tan(math.radians(a)) * 0.5 会大于 box[0] 么？
    :param a:
    :param box:
    :return:
    '''
    return box[0] * box[1] - box[1] * box[1] / math.tan(math.radians(a)) * 0.5

"""
不同情况下的质心求解，输入为油箱剩余油量面积，油箱的长宽高，飞机俯仰角
返回质心相对与左下角[0,0]的位置[x,z]
"""
def solution_0(s,box,a):
    '''
    对于水平方式的质心求解
    '''
    return [box[0] / 2, s / box[0] / 2]

def solution_1(s,box,a):
    v = []
    v.append([0,0])
    v.append([box[0],0])
    s_parallelogram = s - get_squre1(a,box)
    h_parallelogram = s_parallelogram / (box[0] / math.cos(math.radians(a)))
    z_parallelogram = h_parallelogram / math.cos(math.radians(a))
    v.append([box[0],z_parallelogram])
    v.append([0,box[0] * math.tan(math.radians(a)) + z_parallelogram])
    return centroid_of_convex_polygon_list(v)

def solution_2(s,box,a):
    v = []
    v.append([0,box[1]])
    v.append([0,0])
    v.append([box[0],0])
    s_trangle = box[0] * box[1] - s
    x = math.sqrt(2 * s_trangle / math.tan(math.radians(a)))
    z = x * math.tan(math.radians(a))
    v.append([box[0],box[1] - z])
    v.append([box[0] - x,box[1]])
    return centroid_of_convex_polygon_list(v)



def solution_3(s,box,a):
    v = []
    v.append([0, box[1]])
    v.append([0,0])
    s_parallelogram = s - get_squre3(a, box)
    h_parallelogram = s_parallelogram / (box[1] / math.sin(math.radians(a)))
    z_parallelogram = h_parallelogram / math.sin(math.radians(a))
    v.append([z_parallelogram + box[1]/math.tan(math.radians(a)),0])
    v.append([z_parallelogram,box[1]])
    return centroid_of_convex_polygon_list(v)



def solution_4(s,box,a):
    v = []
    if s == 0:
        return [0,0]
    else:
        x = math.sqrt(2 * s / math.tan(math.radians(a))) # x * tan(theta) * x = S * 2
        v.append([x,0])
        v.append([0,x * math.tan(math.radians(a))])
        v.append([0,0])
        return  centroid_of_convex_polygon_list(v)

if __name__ == "__main__":
    # 进行测试校验
    # 进行水平测试校验 ok
    # 参数 0.1m^3 长高宽 倾斜角 0 度
    # print(box_centre(0.1,[1,1,1],0.))
    # ---------------------------------
    # 进行正小容量的校验
    # 参数 0.1m^3 长高宽 倾斜角 30 度  出错
    print(box_centre(0.1, [1, 1, 1], 30.))
