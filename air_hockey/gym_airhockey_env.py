import math
from abc import ABC

import gym
from gym.utils import seeding
import numpy as np

from air_hockey import AirHockey
import phy_const as P
from dimensions import Dimensions
from gym_airhockey_data import DataProcessor

default_use_object = {'arm': False,
                      'puck': True,
                      'top_mallet': False}


class Air_hockey_gym(gym.Env):
    # 和图像渲染相关的参数
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 50
    }

    def __init__(self, use_object=default_use_object):
        self.game = AirHockey(use_object)
        self.processor = DataProcessor()

        self.dim = Dimensions()

        self.action_space = gym.spaces.Discrete(len(self.processor.actions))
        self.n_actions = 4
        self.reward_range = (-1.0, 1.0)
        self.observation_space = gym.spaces.Box(self.processor.low, self.processor.high, dtype=np.float32)
        self.n_features = 8
        self.seed()
        self.viewer = None
        self.state = None

        self.steps_beyond_done = None

        self.use_object = use_object
        self.mallet_average_v = 0
        self.time_accumulation = 0
        self.tol_reward = 0
        self.step_per_episode = 0
        self.ini_distance = 0

    def render(self):
        self.game.render()

    def reset(self):
        game_info = self.game.reset()
        # Fill in the current_state
        stand_action = self.processor.process_action(0)
        self.ini_distance = np.linalg.norm(game_info.puck_position - game_info.bottom_mallet_position)
        # state = np.concatenate(
        #     (game_info.puck_position,
        #      game_info.puck_velocity,
        #      game_info.bottom_mallet_position,
        #      game_info.bottom_mallet_velocity,
        #      game_info.top_mallet_position,
        #      game_info.top_mallet_velocity))

        state = np.concatenate(
            (game_info.puck_position,
             game_info.puck_velocity,
             game_info.bottom_mallet_position,
             game_info.bottom_mallet_velocity))

        self.tol_reward = 0
        self.step_per_episode = 0
        return state

    def step(self, action=None):
        # assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
        # 根据action的值得到下一步状态, 保存在game_info这个类中

        if action is None:
            robot_action = None
        else:
            action_label = action
            robot_action = self.processor.process_action(action_label)

        game_info = self.game.step(robot_action=robot_action, human_action=None)
        self.time_accumulation += game_info.time_iter
        mallet_v_norm = np.linalg.norm(game_info.bottom_mallet_velocity)

        # 提取平均速度并作相应修正
        if self.mallet_average_v == 0:
            self.mallet_average_v = mallet_v_norm
        else:
            self.mallet_average_v = (mallet_v_norm + self.mallet_average_v) / 2

        # done = game_info.scored is not None # or (self.time_accumulation > 1500)
        # ————————————————————————————————————————————————————————————————————————
        # done和reward的计算
        reward = 0
        # 从game_info提取需要的信息
        puck_pos = game_info.puck_position
        bottom_line = self.dim.rink_bottom - self.dim.puck_radius - 10
        if puck_pos[1] >= bottom_line:
            done = 1
        else:
            if game_info.puck_was_hit == 1:
                reward += 10
                # print('Puck was hit')

            top_line = self.dim.rink_top + self.dim.puck_radius + 10

            if puck_pos[1] <= top_line or game_info.score_flag != 0:
                done = 1
                if game_info.score_flag != -1:
                    # print('done')
                    center_reward = (110 - abs(puck_pos[0] - self.dim.center[0])) / 2
                    reward += center_reward
                    # print('center reward', center_reward)
                    velocity_reward = np.linalg.norm(game_info.puck_velocity)
                    reward += velocity_reward
                    # print('velocity reward', velocity_reward)
                    # print('step_reward', reward)
                    # print('------------------------')
                else:
                    reward -= 5
            else:
                done = 0
                reward -= 0.01

            if np.linalg.norm(game_info.puck_velocity) < 1e-6:
                dis = np.linalg.norm(game_info.puck_position - game_info.bottom_mallet_position)
                if game_info.puck_position[1] < game_info.bottom_mallet_position[1]:
                    distance_reward = (self.ini_distance - dis) * 0.01
                    distance_reward = np.clip(distance_reward, -1, 1)
                    reward += distance_reward
                # print('distance reward', distance_reward)
        # 当前位置 当前位置的速度（Markov 过程）

        # state = np.concatenate(
        #     (game_info.puck_position,
        #      game_info.puck_velocity,
        #      game_info.bottom_mallet_position,
        #      game_info.bottom_mallet_velocity,
        #      game_info.top_mallet_position,
        #      game_info.top_mallet_velocity))
        state = np.concatenate(
            (game_info.puck_position,
             game_info.puck_velocity,
             game_info.bottom_mallet_position,
             game_info.bottom_mallet_velocity))
        # print('------------------------------------')
        # print('puck_pos', game_info.puck_position)
        # print('puck_v', game_info.puck_velocity)
        # # print('top_pos', game_info.bottom_mallet_position)
        # # print('top_v', game_info.bottom_mallet_velocity)
        # print('bottom_pos', game_info.bottom_mallet_position)
        # print('bottom_v', game_info.bottom_mallet_velocity)
        # print('reward', reward)

        self.state = state
        self.tol_reward += reward
        self.step_per_episode += 1

        return np.array(self.state), reward, done, {}


if __name__ == "__main__":
    use_object = {'arm': False,
                  'puck': True,
                  'top_mallet': False}

    env = Air_hockey_gym(use_object=use_object)

    while True:
        action = 14
        state, reward, done, _ = env.step(action)
        env.render()
