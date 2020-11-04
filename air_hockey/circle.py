import numpy as np
import vector as V
import phy_const as P
from abc import ABC, abstractmethod


class Circle(ABC):
    def __init__(self, position, radius, borders,
                 mass, maximum_speed, friction,
                 body_restitution, wall_restitution):
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.zeros(2, dtype=np.float32)
        self.maximum_speed = maximum_speed

        if mass == 0.0:
            raise ValueError('Mass cannot be zero')
        self._mass = float(mass)
        self._inverse_mass = 1 / float(mass)

        self.friction = friction
        # self.accumulated_forces = np.zeros(2, dtype=np.float32)
        self.accumulated_velocity = np.zeros(2, dtype=np.float32)
        self.radius = radius
        self.borders = borders
        self.body_restitution = body_restitution
        self.wall_restitution = wall_restitution

    def set_velocity(self, velocity):
        magnitude = V.magnitude(velocity)
        # Limit velocity to prevent the body from escaping its borders
        if magnitude > self.maximum_speed:
            velocity *= self.maximum_speed/magnitude
        velocity = V.address_data(velocity)
        self.velocity[:] = velocity

    # 返回速度self._velocity
    def get_velocity(self):
        return np.copy(self.velocity)

    # 返回位置
    def get_position(self):
        return np.copy(self.position)

    def get_mass(self):
        return np.copy(self._mass)

    def get_inverse_mass(self):
        return np.copy(self._inverse_mass)

    # 增加速度
    def add_velocity(self, velocity):
        self.accumulated_velocity += velocity
        self.velocity += velocity

    # 清空
    def clear_accumulated_v(self):
        self.accumulated_velocity = 0

    def speed_position_update(self, dt):
        velocity = self.velocity
        # velocity *= self.friction
        self.set_velocity(velocity)
        self.velocity = velocity
        # print(self.__class__.__name__, 'update velocity = ', self.velocity)
        self.position += self.velocity * dt

    # 清空合力、随机设置位置、速度
    @abstractmethod
    def reset(self, dim, top, bottom):
        pass


class Target(Circle):
    def __init__(self, position, radius):
        super().__init__(position, radius, None, 1.0, 0, 0, 0, 0)

    def reset(self, dim, top, bottom):
        pass


class Puck(Circle):
    def __init__(self, position, radius, borders):
        super().__init__(position, radius, borders, P.puck_mass,
                         P.puck_maximum_speed, P.puck_friction, P.mallet_mallet_restitution, P.puck_wall_restitution)

    def reset(self, dim, top, bottom):
        self.clear_accumulated_v()
        # self.position[:] = dim.random_puck_position(self, bottom)
        self.position[:] = dim.random_position(self, top, bottom)
        # self._velocity[:] = dim.random_puck_velocity()
        # self.velocity[:] = dim.random_puck_velocity()
        # self.velocity[:] = np.zeros(2, dtype=np.float32) # 初速度为0
        self.velocity[:] = dim.random_puck_velocity()
class Top_Mallet(Circle, ABC):
    def __init__(self, position, radius, borders):
        super().__init__(position, radius, borders, P.mallet_mass,
                         P.mallet_maximum_speed, P.mallet_friction, P.puck_mallet_restitution,
                         P.mallet_wall_restitution)

    def reset(self, dim, top, bottom):
        self.clear_accumulated_v()
        # self.position[:] = dim.random_puck_position(self, bottom)
        self.position[:] = [dim.center[0], dim.rink_top + 2 * dim.mallet_radius]
        # self._velocity[:] = dim.random_puck_velocity()
        self.velocity[:] = np.zeros(2, dtype=np.float32)


class Bottom_Mallet(Circle, ABC):
    def __init__(self, position, radius, borders):
        super().__init__(position, radius, borders, P.mallet_mass,
                         P.mallet_maximum_speed, P.mallet_friction, P.puck_mallet_restitution,
                         P.mallet_wall_restitution)

    def reset(self, dim, top, bottom):
        self.clear_accumulated_v()
        # self.position[:] = dim.random_puck_position(self, bottom)
        self.position[:] = [dim.center[0], dim.rink_bottom - 2 * dim.mallet_radius]
        # self._velocity[:] = dim.random_puck_velocity()
        self.velocity[:] = np.zeros(2, dtype=np.float32)