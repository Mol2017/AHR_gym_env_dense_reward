import numpy as np
import vector as V


class Collision(object):

    @staticmethod
    def _resolve_circle_circle_velocity(bodies, normal, restitution):
        # 返回两个点的位置
        position_0_x, position_0_y = bodies[0].get_position()
        position_1_x, position_1_y = bodies[1].get_position()
        # 求碰撞处切平面向量t与法向量s
        s = np.array([position_1_x - position_0_x, position_1_y - position_0_y], dtype=np.float32)
        t = np.array([-position_1_y + position_0_y, position_1_x - position_0_x], dtype=np.float32)
        s = V.normalize(s)
        t = V.normalize(t)
        # 两个物体的速度
        velocity_0 = bodies[0].get_velocity()
        velocity_1 = bodies[1].get_velocity()
        # 先算v0（v0x, v0y)在s和t轴的投影值，分别设为v0s和v0t
        # 再算v1（v1x, v1y)在s和t轴的投影值，分别设为v1s和v1t
        v0s = velocity_0.dot(s)
        v0t = velocity_0.dot(t)
        v1s = velocity_1.dot(s)
        v1t = velocity_1.dot(t)
        # 返回两个物体的质量
        mass_0 = bodies[0].get_mass()
        mass_1 = bodies[1].get_mass()
        # 转换后于s向量上的弹性正碰撞。质量不等
        # 弹性正碰撞公式
        # v1' = [ (m1-m2)*v1 + 2*m2*v2 ] / (m1+m2)
        # v2' = [ (m2-m1)*v2 + 2*m1*v1 ] / (m1+m2)
        v0s_ = ((mass_0 - restitution * mass_1) * v0s + (1 + restitution) * mass_1 * v1s) / (mass_0 + mass_1)
        v1s_ = ((1 + restitution) * mass_0 * v0s - (restitution * mass_0 - mass_1) * v1s) / (mass_0 + mass_1)

        # # 相对速度
        # relative_velocity  = velocity_0
        # relative_velocity -= velocity_1
        # separating_velocity = relative_velocity.dot(normal)
        # # 已经有分开的趋势，即已经过了最大变形点，两个物体分离，则不改变速度
        # if separating_velocity >= 0.0: return
        # 设置分开的速度
        v0tvector = t * v0t
        v0svector = s * v0s_
        v1tvector = t * v1t
        v1svector = s * v1s_
        new_velocity_0 = v0tvector + v0svector
        new_velocity_1 = v1tvector + v1svector

        bodies[0].set_velocity(new_velocity_0)
        bodies[1].set_velocity(new_velocity_1)

    @staticmethod
    def _resolve_circle_circle_interpenetration(bodies, normal, penetration):
        # 将两个重叠的circle分开
        if penetration <= 0.0: return

        total_inverse_mass = bodies[0].get_inverse_mass()
        total_inverse_mass += bodies[1].get_inverse_mass()

        disposition_per_inverse_mass = normal * (penetration / total_inverse_mass)
        bodies[0].position += disposition_per_inverse_mass * bodies[0].get_inverse_mass()
        bodies[1].position += disposition_per_inverse_mass * -bodies[1].get_inverse_mass()

    @staticmethod
    def circle_circle(bodies, resolve=True):
        restitution = max(bodies[0].body_restitution, bodies[1].body_restitution)

        position_0 = bodies[0].position
        position_1 = bodies[1].position
        total_radius = bodies[0].radius + bodies[1].radius

        # 两个物体的距离如果没有相交，则返回false
        direction = position_0 - position_1
        distance = V.magnitude(direction)
        if distance <= 0.0 or distance >= (total_radius):
            return False

        # 两个物体的距离如果相交
        # 计算单位方向向量
        normal = V.normalize(direction)
        penetration = total_radius - distance

        if resolve:
            Collision._resolve_circle_circle_velocity(bodies, normal, restitution)
            Collision._resolve_circle_circle_interpenetration(bodies, normal, penetration)

        return True

    @staticmethod
    def circle_line(body, line, screen=None):
        # 计算circle与直线最近的点
        relative_position = body.position - line.p1
        projected_vector = line.direction * relative_position.dot(line.direction)
        closest_point = line.p1 + projected_vector

        # 记录参数
        cx, cy = closest_point
        lx1, ly1 = line.p1
        lx2, ly2 = line.p2

        # Make sure that closest point lies on the line
        if lx1 - lx2 > 0:
            cx = max(min(cx, lx1), lx2)
        else:
            cx = min(max(cx, lx1), lx2)
        if ly1 - ly2 > 0:
            cy = max(min(cy, ly1), ly2)
        else:
            cy = min(max(cy, ly1), ly2)
        closest_point[:] = cx, cy

        distance = V.magnitude(body.position - closest_point)

        collided = distance < body.radius
        if collided:
            # Resolve interpenetration
            orthogonal_vector = relative_position - projected_vector
            penetration = body.radius - V.magnitude(orthogonal_vector)
            disposition = V.normalize(orthogonal_vector) * penetration
            body.position += disposition

            # Resolve Velocity
            velocity = body.get_velocity() - line.normal * body.get_velocity().dot(line.normal) * (
                        1 + body.wall_restitution)
            body.set_velocity(velocity)

        return collided
