#coding=utf-8
import math
'''
功能函数  计算液体的质心
@:param  三个点坐标值
'''
class point:
    def __init__(self,x,y,z=0):
        self.x = x
        self.y = y
        self.z = z
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def getZ(self):
        return self.z
    def setX(self, x):
        self.x = x
    def setY(self, y):
        self.y = y
    def setZ(self, z):
        self.z = z
    def norm(self):
        no = math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2) + math.pow(self.z, 2))
        self.x = self.x / no
        self.y = self.y / no
        self.z = self.z / no


class triangle:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
        self.centroid_x = 0
        self.centroid_y = 0
        self.centroid_z = 0
        self.centroid = 0
        self.area = 0
        '''
        构造好三角形之后直接计算面积和质心
        '''
        self.get_centroid_of_triangle()
        self.get_area_of_triangle()
    def getA(self):
        return self.a
    def getB(self):
        return self.b
    def getC(self):
        return self.c
    def get_centroid_of_triangle(self):
        self.centroid_x = (self.a.getX() + self.b.getX() + self.c.getX()) / 3.0
        self.centroid_y = (self.a.getY() + self.b.getY() + self.c.getY()) / 3.0
        self.centroid_z = (self.a.getZ() + self.b.getZ() + self.c.getZ()) / 3.0
        self.centroid = point(self.centroid_x, self.centroid_y, self.centroid_z)
        return self.centroid
    def get_area_of_triangle(self):
        '''
        得到三角形的面积  使用海伦公式
        '''
        lenA = math.sqrt(math.pow(self.b.getX() - self.c.getX(), 2) + math.pow(self.b.getY() - self.c.getY(), 2) + math.pow(self.b.getZ() - self.c.getZ(), 2))
        lenB = math.sqrt(math.pow(self.a.getX() - self.c.getX(), 2) + math.pow(self.a.getY() - self.c.getY(), 2) + math.pow(self.a.getZ() - self.c.getZ(), 2))
        lenC = math.sqrt(math.pow(self.b.getX() - self.a.getX(), 2) + math.pow(self.b.getY() - self.a.getY(), 2) + math.pow(self.b.getZ() - self.a.getZ(), 2))
        self.area = 1.0 / 4.0 * math.sqrt((lenA + lenB + lenC) * (lenA + lenB - lenC) * (lenA + lenC - lenB) * (lenB + lenC - lenA))
        return self.area
    def get_centroid_x(self):
        '''
            一定要求解完质心坐标再使用
        '''
        return self.centroid_x
    def get_centroid_y(self):
        return self.centroid_y
    def get_centroid_z(self):
        return self.centroid_z
    def get_area(self):
        return self.area
    def get_centroid(self):
        return self.centroid




'''
功能函数  求多边形的质心
@:param v 是多个点的坐标 list point 类型 
参考链接 https://www.cnblogs.com/ningmouming/p/9803783.html
'''
def centroid_of_convex_polygon(v):
    if(len(v) < 3):
        return -1
    if(len(v) == 3):
        t = triangle(v[0], v[1], v[2])
        return t.get_centroid_of_triangle()
    sum_Area = 0 # 用面积替代质量？
    # 多个三角形的类对象
    tmp = [] # tmp 似乎没有用
    centroid = point(0,0,0)
    for i in range(len(v) - 2):
        t = triangle(v[0], v[i+1], v[i+2])
        tmp.append(t)
        sum_Area += t.get_area()
        centroid.x += t.get_centroid_x() * t.get_area()
        centroid.y += t.get_centroid_y() * t.get_area()
        centroid.z += t.get_centroid_z() * t.get_area()
    if(sum_Area == 0):
        return centroid
    centroid.x = centroid.x / sum_Area
    centroid.y = centroid.y / sum_Area
    centroid.z = centroid.z / sum_Area
    return centroid

'''
求多个质心坐标的到一个质心坐标 v point 质心坐标list  t 质量  返回point
'''
def centroid_of_centorids(v, t):
    # 多个质心
    tmp = []
    centroid = point(0,0,0)
    sumWeight = 0
    for i in range(len(v)):
        sumWeight += t[i]
        centroid.x += t[i] * v[i].getX()
        centroid.y += t[i] * v[i].getY()
        centroid.z += t[i] * v[i].getZ()
    centroid.x = centroid.x / sumWeight
    centroid.y = centroid.y / sumWeight
    centroid.z = centroid.z / sumWeight
    return centroid

'''
体积转质量 
'''
def volume2weight(v, roh):
    '''
    :param v: 体积值
    :param roh: 密度值
    :return: 质量值
    '''
    return roh * v

'''
质量转体积
'''
def weight2volume(m, roh):
    '''
    :param m: 质量
    :param roh: 密度
    :return: 体积值
    '''
    return m / roh

'''
多边形重心 采用 周同学的list
'''
def centroid_of_convex_polygon_list(para):
    v = []
    for i in range(len(para)):
        v.append(point(para[i][0], para[i][1], 0))

    if(len(v) < 3):
        return -1
    if(len(v) == 3):
        t = triangle(v[0], v[1], v[2])
        t = t.get_centroid_of_triangle()
        centroid_list = []
        centroid_list.append(t.x)
        centroid_list.append(t.y)
        return centroid_list
    sum_Area = 0 # 用面积替代质量？
    # 多个三角形的类对象
    tmp = [] # tmp 似乎没有用
    centroid = point(0,0,0)
    for i in range(len(v) - 2):
        t = triangle(v[i], v[i+1], v[i+2])
        tmp.append(t)
        sum_Area += t.get_area()
        centroid.x += t.get_centroid_x() * t.get_area()
        centroid.y += t.get_centroid_y() * t.get_area()
        centroid.z += t.get_centroid_z() * t.get_area()
    centroid.x = centroid.x / sum_Area
    centroid.y = centroid.y / sum_Area
    centroid.z = centroid.z / sum_Area
    centroid_list = []
    centroid_list.append(centroid.x)
    centroid_list.append(centroid.y)
    return centroid_list

'''
根据得到的  平面的重心  计算 三维的中心 
'''
def twoDim2threeDim(v, oilPoint, lwh):
    '''
    :param v: list 输入的  x z list
           oilPoint: list (油桶的中心坐标)
           lwh: 油桶的长宽高
    :return: 以飞机质心为原点的坐标系
    '''
    # 现在假设得到的坐标是（x_c, z_c）
    length = lwh[0]
    width = lwh[1]
    height = lwh[2]
    v_local = [v[0] - 0.5 * length + oilPoint[0], oilPoint[1], v[1] - 0.5 * height + oilPoint[2]]
    return v_local


def threeDim2threeDim(v, oilPoint, lwh):
    '''
    :param v: point flat
           oilPoint: list (油桶的中心坐标)
           lwh: 油桶的长宽高
    :return: 以飞机质心为原点的坐标系
    '''
    # 现在假设得到的坐标是（x_c, z_c）
    length = lwh[0]
    width = lwh[1]
    height = lwh[2]
    # v_local = [v[0] - 0.5 * length + oilPoint[0], oilPoint[1], v[1] - 0.5 * height +oilPoint[2]]
    v_local = [oilPoint[0] - 0.5 * length + v.getX(), oilPoint[1], v.getZ() + oilPoint[2] - 0.5 * height]
    return v_local

def cal_included_angle(a, b):
    '''
    余弦定理
    :param a:  list [x, y, z]
    :param b: == a
    :return:  angle
    '''
    cos_theta = (a[0] * b[0] + a[1] * b[1] + a[2] * b[2]) / (math.sqrt(math.pow(a[0], 2) + math.pow(a[1], 2) + math.pow(a[2], 2)) *
                                                             math.sqrt(math.pow(b[0], 2) + math.pow(b[1], 2) + math.pow(b[2], 2)))
    theta = math.degrees(math.acos(cos_theta))
    return theta

# 组合字符串代码
def perm(s=''):
    # 这里是递归函数的出口，为什么呢，因为这里表示：一个长度为1的字符串，它的排列组合就是它自己。
    if len(s) <= 1:
        return [s]
    sl = []  # 保存字符串的所有可能排列组合
    for i in range(len(s)):  # 这个循环，对应 解题思路1）确定字符串的第一个字母是谁，有n种可能（n为字符串s的长度
        for j in perm(s[0:i] + s[i + 1:]):  # 这个循环，对应 解题思路2）进入递归，s[0:i]+s[i+1:]的意思就是把s中的s[i]给去掉
            sl.append(s[i] + j)  # 对应 解题思路2）问题就从“返回字符串中的字母排列组合” **变成了** “返回 第一个字母+除去第一个字母外的字符串的排列组合”
    return sl

def perm_main(s=''):
    perm_nums = perm(s)  # 有可能存在字母相同的情况
    no_repeat_nums = list(set(perm_nums))  # 去重，挺牛的，这个代码
    # print('perm_nums', len(perm_nums), perm_nums)
    # print('no_repeat_nums', len(no_repeat_nums), no_repeat_nums)
    return no_repeat_nums

def distance(a, b):
    return math.sqrt(math.pow(a.getX() - b.getX(), 2) + math.pow(a.getY() - b.getY(), 2) + math.pow(a.getZ() - b.getZ(), 2))

if __name__=='__main__':
    pass
'''
    校验质心坐标没有问题
    v = []
    v.append(point(1,1,1))
    v.append(point(0,0,0))
    v.append(point(1,1,0))
    v.append(point(0,0,1))
    v.append(point(0,1,0))
    v.append(point(1,0,0))
    v.append(point(0,1,1))
    v.append(point(1,0,1))
    w = []
    for i in range(8):
        w.append(1)
    t = centroid_of_centorids(v, w)
    print(t.getX(),t.getY(), t.getZ())
'''













