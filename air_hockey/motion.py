import pygame
import numpy as np
from abc import ABC, abstractmethod
import phy_const as P


class MotionRegistry(object):
    # class Registry的成员是两个class
    # 一个body（puck/mallet）
    # 一个motion_generator(更新运动)
    # 相当与 把智能体和它的运动控制策略一起存在self.registrations里
    class Registry(object):
        def __init__(self, body, motion_generator):
            self.body = body
            self.motion_generator = motion_generator

    def __init__(self):
        # 创建一个空的组合set
        self.registrations = set()

    def add(self, body, motion_generator):
        self.registrations.add(self.Registry(body, motion_generator))

    def remove(self, body, motion_generator):
        for registration in self.registrations:
            if registration.particle == body and registration.motion_generator == motion_generator:
                self.np.random.normal(loc=0.0, scale=1.0)(registration)
                break

    def update_motions(self):
        for registration in self.registrations:
            registration.motion_generator.update_motion(registration.body)
    def clear_all_motions(self):
        for registration in self.registrations:
            registration.motion_generator.clear_motion(registration.body)
    
    def clear(self):
        self.registrations = {}


class MotionGenerator(ABC):
    def __init__(self, factor=P.puck_friction):
        self.factor = factor

    @abstractmethod
    def update_motion(self, body):
        pass

    @abstractmethod
    def clear_motion(self, body):
        pass


class ControlledMotion(MotionGenerator):
    def __init__(self):
        super().__init__()
        self.motion = np.zeros(2, dtype=np.float32)

    def clear_motion(self, body):
        pass
    
    def set_motion(self, motion):
        self.motion[:] = motion

    def update_motion(self, body):
        if body.__class__.__name__ == 'Puck':
            body.add_velocity(self.motion * self.factor)
        elif body.__class__.__name__ == 'Top_Mallet' or \
             body.__class__.__name__ == 'Bottom_Mallet':
            body.add_velocity(self.motion)


class RandomMotion(MotionGenerator):
    def __init__(self, factor=P.motion_multiplier):
        super().__init__(factor)
        self.count = 0
        self.limit = 50
        self.motion = np.array([0, 0], dtype=np.float32)
        self.speed = P.top_mallet_speed
        
    def clear_motion(self, body):
        self.count = 0
        self.limit = P.top_constant_limit
        self.motion = np.array([0, 0], dtype=np.float32)
        body.add_velocity(self.motion)
    
    def update_motion(self, body):
        import random
        if self.count < self.limit:
            self.limit = P.top_constant_limit
            # self.motion[:] = random.randrange(-1, 2, 1) * self.factor, random.randrange(-1, 2, 1) * self.factor
            self.count += 1
            self.motion[0] = self.speed
            self.motion[1] = 0
        else:
            self.limit = 0
            self.count -= 1
            self.motion[0] = -self.speed
            self.motion[1] = 0
            
        body.add_velocity(self.motion)


class PlayerMotion(MotionGenerator):
    def __init__(self, factor=P.motion_multiplier, player=0):
        super().__init__(factor)
        self.player = player
        self.motion = np.array([0, 0], dtype=np.float32)
        self.prev_x, self.prev_y = 0, 0

    def clear_motion(self, body):
        pass
    
    def update_motion(self, body):
        if self.player == 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                x = -1
            elif keys[pygame.K_d]:
                x = 1
            else:
                x = 0
            if keys[pygame.K_w]:
                y = -1
            elif keys[pygame.K_s]:
                y = 1
            else:
                y = 0
        elif self.player == 1:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                x = -1
            elif keys[pygame.K_RIGHT]:
                x = 1
            else:
                x = 0
            if keys[pygame.K_UP]:
                y = -1
            elif keys[pygame.K_DOWN]:
                y = 1
            else:
                y = 0

        self.motion[:] = x * self.factor, y * self.factor
        body.add_velocity(self.motion)