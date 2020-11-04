import numpy as np


class GameInfo(object):
    def __init__(self,
                 frame,
                 puck_position=None,
                 puck_velocity=None,
                 bottom_mallet_position=None,
                 bottom_mallet_velocity=None,
                 top_mallet_position = None,
                 top_mallet_velocity = None,
                 robot_action=None,
                 human_action=None,
                 scored=None,
                 score_flag=None,
                 puck_was_hit=False,
                 puck_is_at_the_bottom=False,
                 distance_decreased=False,
                 hit_the_border=False,
                 in_the_target=False,
                 time_iter=None,
                 puck_position_mode=None):
        
        self.frame = np.copy(frame)
        self.top_mallet_position = np.copy(top_mallet_position)
        self.top_mallet_velocity = np.copy(top_mallet_velocity)
        
        if robot_action is None:
            self.robot_action = np.zeros(2, dtype=np.float32)
        else:
            self.robot_action = np.copy(robot_action)
            
        if human_action is None:
            self.human_action = np.zeros(2, dtype=np.float32)
        else:
            self.human_action = np.copy(human_action)
            
        if puck_position is None:
            self.puck_position = np.zeros(2, dtype=np.float32)
        else:
            self.puck_position = np.copy(puck_position)

        if puck_velocity is None:
            self.puck_velocity = np.zeros(2, dtype=np.float32)
        else:
            self.puck_velocity = np.copy(puck_velocity)

        if bottom_mallet_position is None:
            self.bottom_mallet_position = np.zeros(2, dtype=np.float32)
        else:
            self.bottom_mallet_position = np.copy(bottom_mallet_position)

        if bottom_mallet_velocity is None:
            self.bottom_mallet_velocity = np.zeros(2, dtype=np.float32)
        else:
            self.bottom_mallet_velocity = np.copy(bottom_mallet_velocity)

        if score_flag is None:
            self.score_flag = np.zeros(1, dtype=np.float32)
        else:
            self.score_flag = np.copy(score_flag)

        if time_iter is None:
            self.time_iter = np.zeros(1, dtype=np.float32)
        else:
            self.time_iter = np.copy(time_iter)
            
        if puck_position_mode is None:
            self.puck_position_mode = np.zeros(1, dtype=np.float32)
        else:
            self.puck_position_mode = np.copy(puck_position_mode)

        self.puck_was_hit = puck_was_hit
        self.scored = scored
        self.puck_is_at_the_bottom = puck_is_at_the_bottom
        self.distance_decreased = distance_decreased
        self.hit_the_border = bool(hit_the_border)
        self.in_the_target = in_the_target