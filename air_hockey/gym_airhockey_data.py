import numpy as np
import phy_const as P
from dimensions import Dimensions


class DataProcessor(object):
    def __init__(self, mode='rgb'):
        acce_x_max = P.mallet_max_acce_x
        acce_y_max = P.mallet_max_acce_y
        # 加入不同的变化量，离散化
        # 从[0,1]开始逆时针，注意y向下为正
        # self.actions = np.array([
        #                     [0, 0],
        #                     [0, acce_y_max],
        #                     [0, acce_y_max*0.6],
        #                     [-acce_x_max, acce_y_max],
        #                     [-acce_x_max * 0.6, acce_y_max * 0.6],
        #                     [-acce_x_max, 0],
        #                     [-acce_x_max * 0.6, 0],
        #                     [-acce_x_max, -acce_y_max],
        #                     [-acce_x_max * 0.6, -acce_y_max * 0.6],
        #                     [0, -acce_y_max],
        #                     [0, -acce_y_max * 0.6],
        #                     [acce_x_max, -acce_y_max],
        #                     [acce_x_max * 0.6, -acce_y_max * 0.6],
        #                     [acce_x_max, 0],
        #                     [acce_x_max * 0.6, 0],
        #                     [acce_x_max, acce_y_max],
        #                     [0.6*acce_x_max, 0.6*acce_y_max],
        #                     ],
        #                     dtype=np.float32)
        self.actions = np.array([
                            [0, acce_y_max],
                            [-acce_x_max, 0],
                            [0, -acce_y_max],
                            [acce_x_max, 0],
                            ],
                            dtype=np.float32)
        
        self.metrics = []
        self.metrics_names = []

        self.mode = mode
        self.dim = Dimensions()
        self.puck_max_speed = P.puck_max_speed_sep
        self.mallet_max_speed = P.mallet_max_speed_sep
        self.puck_x_min = 0
        self.puck_y_min = 0
        self.puck_x_max = self.dim.width
        self.puck_y_max = self.dim.height
        self.mallet_x_min = 0
        self.mallet_y_min = 0
        self.mallet_x_max = self.dim.width
        self.mallet_y_max = self.dim.height

        # self.low = np.array([
        #     self.puck_x_min, self.puck_y_min, -self.puck_max_speed, -self.puck_max_speed, self.mallet_x_min, self.mallet_y_min,
        #     -self.mallet_max_speed, -self.mallet_max_speed,
        #     self.mallet_x_min, self.mallet_y_min,
        #     -self.mallet_max_speed, -self.mallet_max_speed
        # ])
        #
        # self.high = np.array([
        #     self.puck_x_max, self.puck_y_max, self.puck_max_speed, self.puck_max_speed,
        #     self.mallet_x_max, self.mallet_y_max, self.mallet_max_speed, self.mallet_max_speed,
        #     self.mallet_x_max, self.mallet_y_max, self.mallet_max_speed, self.mallet_max_speed
        # ])


        self.low = np.array([
            self.puck_x_min, self.puck_y_min, -self.puck_max_speed, -self.puck_max_speed, self.mallet_x_min, self.mallet_y_min,
            -self.mallet_max_speed, -self.mallet_max_speed,
        ])

        self.high = np.array([
            self.puck_x_max, self.puck_y_max, self.puck_max_speed, self.puck_max_speed,
            self.mallet_x_max, self.mallet_y_max, self.mallet_max_speed, self.mallet_max_speed,
        ])

        self.state_buffersize = 1000
        self.state_buffer = np.zeros((1, self.state_buffersize, len(self.low)), dtype=np.float32)

    def process_step(self, observation, reward, done, info):
        observation = self.process_observation(observation)
        reward = self.process_reward(reward)
        info = self.process_info(info)
        return observation, reward, done, info

    def process_observation(self, observation):
        pass

    def process_reward(self, reward):
        return np.clip(reward, -1.0, 1.0)

    def process_info(self, info):
        return info

    def process_action(self, action_label):
        if action_label is None:
            return None
        else:
            return self.actions[action_label]

    def process_state_batch(self, batch):
        _, depth, height, width = batch[0].shape
        batch = np.array(batch).reshape(len(batch), depth, height, width)
        return batch

    # Used to generate labels for the neural network
    def action_to_label(self, action):
        return int(action[0]*3 + action[1] + 4)