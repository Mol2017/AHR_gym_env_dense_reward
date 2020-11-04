import numpy as np
import phy_const as P
from gym_airhockey_data import DataProcessor


class AI(object):
    def __init__(self, mallet, puck, mode, dim):
        self.mallet = mallet
        self.puck = puck
        self.mode = mode
        self.dim = dim
        self._force = np.zeros(2, dtype=np.float32)
        self.acce_x = P.mallet_max_acce_x
        self.acce_y = P.mallet_max_acce_y

    def ai_where_to_go(self, where):
        self.processor = DataProcessor()
        accelerated_speed = self.processor.actions
        velocity_future = [self.mallet.get_velocity()] + accelerated_speed
        position_future = [self.mallet.position] + velocity_future
        distance_future = np.linalg.norm(position_future - where, axis=1, keepdims=True)
        return np.argmin(distance_future)

    def move(self):
        # # 击球器的位置和速度
        # px, py = self.mallet.position
        # vx, vy = self.mallet.get_velocity()

        # 冰球的位置和速度
        puck_px, puck_py = self.puck.position
        puck_vx, puck_vy = self.puck.get_velocity()

        # if self.mode is 'top':
        #     goal_px, goal_py = (self.dim.center[0], self.dim.rink_top + 55)
        # elif self.mode == 'bottom':
        #     goal_px, goal_py = (self.dim.center[0], self.dim.rink_bottom - 55)

        # 判断冰球是不是在击球器能够移动的范围内
        if self.mode is 'top':
            reachable = self.dim.rink_top <= puck_py <= self.dim.center[1]
        elif self.mode == 'bottom':
            reachable = self.dim.center[1] <= puck_py <= self.dim.rink_bottom

        too_fast = np.linalg.norm([puck_vx, puck_vy]) > 0.6 * P.puck_maximum_speed
        if not reachable or too_fast:
            # 如果球在击球器不能到达的范围
            if self.mode is 'top':
                target_position = [self.dim.center[0], self.dim.rink_top + 40]
            elif self.mode == 'bottom':
                target_position = [self.dim.center[0], self.dim.rink_bottom - 40]
        else:
            # 如果球在击球器能到达的范围,将击球器向冰球靠近
            target_position = [puck_px, puck_py]

        return self.ai_where_to_go(target_position)
