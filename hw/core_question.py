#coding=utf-8
import math
import utils
class centroid_t_to_f:
    def __init__(self, length, width, height, volume, theta):
        self.length = length
        self.width = width
        self.height = height
        self.volume = volume
        self.theta = theta
        self.area = self.area()
        self.a0 = self.extremeAngle() # 计算临界角度

        self.extreme_small_volume_small_angle_left_height = 0
        self.extreme_small_volume_small_angle_area = self.cal_extreme_small_volume_small_angle() # 计算小体积小角度的临界面积

        self.extreme_big_volume_small_angle_right_height = 0
        self.extreme_big_volume_small_angle_area = self.cal_extreme_big_volume_small_angle() # 计算大体积小角度的临界面积

        self.extreme_small_volume_big_angle_bottom_point = 0
        self.extreme_small_volume_big_angle_area = self.cal_extreme_small_volume_big_angle()  # 计算小体积大角度的临界面积


        self.extreme_big_volume_big_angle_area = self.cal_extreme_big_volume_big_angle() # j计算大体积大角度的临界面积
    def area(self):
        self.area = self.volume / self.width
        return self.area
    def extremeAngle(self):
        self.a0 = math.degrees(math.atan2(self.height,self.length))
        return self.a0
    def cal_extreme_small_volume_small_angle(self):
        # 小体积小角度极限面积
        left_height = self.length * math.tan(math.radians(self.theta))
        self.extreme_small_volume_small_angle_left_height = left_height
        return left_height * self.length * 0.5
    def cal_extreme_big_volume_small_angle(self):
        # 大体积 小角度的极限面积
        rect_area = self.height * self.length
        right_height = self.length * math.tan(math.radians(self.theta))
        self.extreme_big_volume_small_angle_right_height = right_height
        return rect_area - right_height * self.length * 0.5
    def cal_extreme_small_volume_big_angle(self):
        # 计算小体积大角度的极限值
        left_bottom = self.height * math.tan(math.radians(90 - self.theta))
        self.extreme_small_volume_big_angle_bottom_point = left_bottom
        return left_bottom * self.height * 0.5
    def cal_extreme_big_volume_big_angle(self):
        # 计算大体积大角度的极限值
        rect_area = self.height * self.length
        right_upper = self.height * math.tan(math.radians(90 - self.theta))
        return rect_area - right_upper * self.height * 0.5

    def solve(self):
        if(self.theta == 0):
            height_left = self.area / self.length
            v = []
            v.append(utils.point(0, 0, 0))
            v.append(utils.point(self.length, 0, 0))
            v.append(utils.point(self.length, 0, height_left))
            v.append(utils.point(0, 0, height_left))
            return utils.centroid_of_convex_polygon(v)
        if(self.theta < self.a0):
            # 此时分3中情况讨论
            if(self.area <= self.extreme_small_volume_small_angle_area):
                # 此时三角形的两个点落在直角的两条边上  x * x * tan(theta) = 2 * s
                bottom = math.sqrt(2 * self.area  / math.tan(math.radians(self.theta)))
                left = bottom * math.tan(math.radians(self.theta))
                v = []
                v.append(utils.point(0,0,0))
                v.append(utils.point(0,0,left))
                v.append(utils.point(bottom,0,0))
                return utils.centroid_of_convex_polygon(v)
            elif self.area > self.extreme_small_volume_small_angle_area and self.area <= self.extreme_big_volume_small_angle_area:
                # 此时两个点落在两条高线上 一共四个点
                area_s1 = self.area - self.extreme_small_volume_small_angle_area
                delta_left = area_s1 / self.length
                v = []
                v.append(utils.point(0, 0, self.extreme_small_volume_small_angle_left_height + delta_left))
                v.append(utils.point(self.length,0,delta_left))
                v.append(utils.point(self.length, 0 , 0))
                v.append(utils.point(0,0,0))
                return utils.centroid_of_convex_polygon(v)
            elif self.area > self.extreme_big_volume_small_angle_area:
                rect_area = self.length * self.height
                delta_s = rect_area - self.area
                # x * x * tan(theta) = 2 * delta_s
                upper = math.sqrt(2 * delta_s / math.tan(math.radians(self.theta)))
                right = upper * math.tan(math.radians(self.theta))
                v = []
                v.append(utils.point(self.length - upper,0,self.height))
                v.append(utils.point(0,0,self.height))
                v.append(utils.point(0,0,0))
                v.append(utils.point(self.length, 0, 0))
                v.append(utils.point(self.length, 0, self.height - right))
                return utils.centroid_of_convex_polygon(v)
            else:
                print('ERROR')
        else:
            # 角度 >= a0
            # 此时分3种情况讨论
            if self.area < self.extreme_small_volume_big_angle_area:
                # 此时三角形的两个点落在直角的两条边上
                bottom = math.sqrt(2 * self.area / math.tan(math.radians(self.theta)))
                left = bottom * math.tan(math.radians(self.theta))
                v = []
                v.append(utils.point(0, 0, 0))
                v.append(utils.point(0, 0, left))
                v.append(utils.point(bottom, 0, 0))
                return utils.centroid_of_convex_polygon(v)
            elif self.area >= self.extreme_small_volume_big_angle_area and self.area < self.extreme_big_volume_big_angle_area:
                # 此时两个点落在两条高线上 一共四个点
                area_s1 = self.area - self.extreme_small_volume_small_angle_area
                delta_bottom = area_s1 / self.height
                v = []
                v.append(utils.point(self.extreme_small_volume_big_angle_bottom_point + delta_bottom, 0, 0))
                v.append(utils.point(delta_bottom, 0, self.height))
                v.append(utils.point(0, 0, self.height))
                v.append(utils.point(0, 0, 0))
                return utils.centroid_of_convex_polygon(v)
            elif self.area > self.extreme_big_volume_big_angle_area:
                rect_area = self.length * self.height
                delta_s = rect_area - self.area
                # x * x * tan(theta) = 2 * delta_s
                upper = math.sqrt(2 * delta_s / math.tan(math.radians(self.theta)))
                right = upper * math.tan(math.radians(self.theta))
                v = []
                v.append(utils.point(self.length - upper, 0, self.height))
                v.append(utils.point(0, 0, self.height))
                v.append(utils.point(0, 0, 0))
                v.append(utils.point(self.length, 0, 0))
                v.append(utils.point(self.length, 0, self.height - right))
                return utils.centroid_of_convex_polygon(v)
            else:
                print('ERROR', self.area)




if __name__ == '__main__':
    t = centroid_t_to_f(10, 10, 10, 125, 10)
    tmp = t.solve()
    print(tmp.getX(), tmp.getY(), tmp.getZ())


