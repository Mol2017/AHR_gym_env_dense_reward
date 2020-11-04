import numpy as np
import phy_const as P
import vector as V

'''
目前环境的各项参数(像素)：
窗口大小：270x480
冰球场地大小：246x378
击球器大小：15
球的大小：12
球门宽度：80
'''


class Dimensions(object):

    def __init__(self,
                 width=270,   # 450
                 height=480,  # 800
                 vertical_margin=51,  #85
                 horizontal_margin=12,  #20
                 goalpost_length=80,  # 160-80
                 arc_radius=30,  # 220
                 mallet_radius=15,  # 28
                 target_radius=30,  # 55
                 puck_radius = 12,
                 bezier_ratio=0.1,  # 0.05
                 scale=1):

        self.Black = (0, 0, 0, 1)
        self.White = (255, 255, 255, 1)
        self.Red = (255, 0, 0)
        # width 和 height 为游戏窗口大小, 注意要为int类型的数据
        self.width = int(width*scale)
        self.height = int(height*scale)

        # margin 为球桌边缘的厚度（垂直和水平方向）
        self.vertical_margin = vertical_margin*scale
        self.horizontal_margin = horizontal_margin*scale

        self.goalpost_length = goalpost_length*scale
        self.arc_radius = arc_radius*scale
        self.mallet_radius = int(mallet_radius*scale)
        self.puck_radius = int(puck_radius)
        self.target_radius = int(target_radius*scale)

        # 用于控制生成的贝塞尔曲线插值点的个数
        self.bezier_ratio = bezier_ratio

        # 一个系数，乘在force上
        self.puck_offset_multiplier = 5
        self.mallet_offset_multiplier = 2

        # table 为窗口， rink 为冰球场地， 窗口左上角为坐标原点，向下为x，向右为y
        self.table_top = 0
        self.table_bottom = self.height
        self.table_left = 0
        self.table_right = self.width

        self.center = np.array([self.width // 2, self.height // 2], dtype=np.float32)

        self.rink_top = self.table_top + self.vertical_margin
        self.rink_bottom = self.table_bottom - self.vertical_margin
        self.rink_left = self.table_left + self.horizontal_margin
        self.rink_right = self.table_right - self.horizontal_margin
        self.rink_width = self.rink_right - self.rink_left
        self.rink_height = self.rink_bottom - self.rink_top

        self.center_left = np.array([self.rink_left, self.center[1]], dtype=np.float32)
        self.center_right = np.array([self.rink_right, self.center[1]], dtype=np.float32)

        # 用来算四个边角弧的起点，终点，中点
        self.arc_top_left_start = np.array([self.rink_left + self.arc_radius, self.rink_top], dtype=np.float32)
        self.arc_top_left_center = np.array([self.rink_left, self.rink_top], dtype=np.float32)
        self.arc_top_left_end = np.array([self.rink_left, self.rink_top + self.arc_radius], dtype=np.float32)
        self.arc_bottom_left_start = np.array([self.rink_left, self.rink_bottom - self.arc_radius], dtype=np.float32)
        self.arc_bottom_left_center = np.array([self.rink_left, self.rink_bottom], dtype=np.float32)
        self.arc_bottom_left_end = np.array([self.rink_left + self.arc_radius, self.rink_bottom], dtype=np.float32)
        self.arc_bottom_right_start = np.array([self.rink_right - self.arc_radius, self.rink_bottom], dtype=np.float32)
        self.arc_bottom_right_center = np.array([self.rink_right, self.rink_bottom], dtype=np.float32)
        self.arc_bottom_right_end = np.array([self.rink_right, self.rink_bottom - self.arc_radius], dtype=np.float32)
        self.arc_top_right_start = np.array([self.rink_right, self.rink_top + self.arc_radius], dtype=np.float32)
        self.arc_top_right_center = np.array([self.rink_right, self.rink_top], dtype=np.float32)
        self.arc_top_right_end = np.array([self.rink_right - self.arc_radius, self.rink_top], dtype=np.float32)

        self.arc_top_left = [self.arc_top_left_start, self.arc_top_left_center, self.arc_top_left_end]
        self.arc_top_right = [self.arc_top_right_start, self.arc_top_right_center, self.arc_top_right_end]
        self.arc_bottom_left = [self.arc_bottom_left_start, self.arc_bottom_left_center, self.arc_bottom_left_end]
        self.arc_bottom_right = [self.arc_bottom_right_start, self.arc_bottom_right_center, self.arc_bottom_right_end]

        # 球门柱坐标
        self.half_goalpost_length = goalpost_length // 2
        self.post_top_left = np.array([self.center[0] - self.half_goalpost_length, self.rink_top], dtype=np.float32)
        self.post_top_right = np.array([self.center[0] + self.half_goalpost_length, self.rink_top], dtype=np.float32)
        self.post_bottom_left = np.array([self.center[0] - self.half_goalpost_length, self.rink_bottom],
                                         dtype=np.float32)
        self.post_bottom_right = np.array([self.center[0] + self.half_goalpost_length, self.rink_bottom],
                                          dtype=np.float32)

        self.top_mallet_position = np.array(
            [self.center[0], self.rink_top + self.mallet_offset_multiplier * self.mallet_radius], dtype=np.float32)
        self.bottom_mallet_position = np.array(
            [self.center[0], self.rink_bottom - self.mallet_offset_multiplier * self.mallet_radius], dtype=np.float32)

        self.top_goal = self.rink_top - self.mallet_radius
        self.bottom_goal = self.rink_bottom + self.mallet_radius

    # 随机生成位置
    def random_position(self, obj, top, bottom):
        return np.array([
            np.random.randint(
                self.rink_left + obj.radius+1,
                self.rink_right - obj.radius-1
            ),
            np.random.randint(
                top + obj.radius+1,
                bottom - obj.radius-1
            )])

    # 随机生成冰球的初始位置（在指定的水平线上）
    def random_puck_position(self, obj, bottom):
        return np.array([
            np.random.randint(
                self.rink_left + obj.radius,
                self.rink_right - obj.radius
            ),
            bottom]
        )

    # 随机生成冰球的初始速度 向下，速度在0.5-1max之间
    @staticmethod
    def random_puck_velocity():
        speed_vector = np.array([np.random.uniform(-1, 1), np.random.uniform(1, 2)])
        # 单位化速度向量
        speed_vector = V.normalize(speed_vector)
        # 速度系数（让其不一定是最大速度）
        speed_coefficient = np.random.uniform(0.5, 1)
        # 初始速度
        initial_speed = speed_vector.dot(P.puck_maximum_speed).dot(speed_coefficient)
        return initial_speed
