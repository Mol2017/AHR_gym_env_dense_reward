import pygame
import numpy as np

from dimensions import Dimensions
from circle import Puck, Top_Mallet, Bottom_Mallet, Target
from motion import MotionRegistry, ControlledMotion

from collision import Collision
from ai_new import AI
from line import Line
from score import Score
from game_info import GameInfo
import vector as V
import phy_const as P

default_use_object = {'arm': False,
                      'puck': True,
                      'top_mallet': True}


class AirHockey(object):
    def __init__(self, use_object=default_use_object, dim=Dimensions(), video_file=None):

        self.dim = dim
        self.use_object = use_object
        self.fclock = pygame.time.Clock()
        self.fps = 60
        # Add Walls
        # Arcs and Lines have to be passed in an anti-clockwise order with respect to the self.dim.center
        # 创建一个Line类，用于记录两点、方向向量、法向向量,这个类有两个成员p1 p2 都是np.array,两点坐标
        top_wall = Line(self.dim.arc_top_left_start, self.dim.arc_top_right_end)
        bottom_wall = Line(self.dim.arc_bottom_left_end, self.dim.arc_bottom_right_start)
        left_wall = Line(self.dim.arc_top_left_end, self.dim.arc_bottom_left_start)
        right_wall = Line(self.dim.arc_top_right_start, self.dim.arc_bottom_right_end)

        top_left_wall = Line(self.dim.arc_top_left_start, self.dim.post_top_left)
        top_right_wall = Line(self.dim.post_top_right, self.dim.arc_top_right_end)
        bottom_left_wall = Line(self.dim.arc_bottom_left_end, self.dim.post_bottom_left)
        bottom_right_wall = Line(self.dim.post_bottom_right, self.dim.arc_bottom_right_start)

        self.center_line = Line(self.dim.center_left, self.dim.center_right)

        # Add Corners
        top_left_corner = Line.generate_bezier_curve(self.dim.arc_top_left, self.dim.bezier_ratio)
        top_right_corner = Line.generate_bezier_curve(self.dim.arc_top_right, self.dim.bezier_ratio)
        bottom_left_corner = Line.generate_bezier_curve(self.dim.arc_bottom_left, self.dim.bezier_ratio)
        bottom_right_corner = Line.generate_bezier_curve(self.dim.arc_bottom_right, self.dim.bezier_ratio)

        # 记录围成边界的线段
        self.borders = [top_left_wall, top_right_wall, bottom_left_wall, bottom_right_wall, left_wall, right_wall] + \
                       top_left_corner + top_right_corner + bottom_left_corner + bottom_right_corner
        # 记录组成球门柱的线段
        self.goal_borders = [top_left_wall, top_right_wall, bottom_left_wall, bottom_right_wall]

        # 用Puck（Circle）类记录冰球参数，冰球的border是整个桌面
        self.puck = Puck(self.dim.center, self.dim.puck_radius, self.borders)
        # 用Mallet（Circle）类记录top方位击球器参数，top击球器的border是半个桌面
        self.top_mallet = Top_Mallet(self.dim.top_mallet_position, self.dim.mallet_radius,
                                     [top_wall, self.center_line, left_wall,
                                      right_wall] + top_left_corner + top_right_corner)
        # 用Mallet（Circle）类记录bottom方位击球器参数，bottom击球器的border是半个桌面
        self.bottom_mallet = Bottom_Mallet(self.dim.bottom_mallet_position, self.dim.mallet_radius,
                                           [self.center_line, bottom_wall, left_wall,
                                            right_wall] + bottom_left_corner + bottom_right_corner)
        # bodies 记录一个冰球和两个击球器类
        self.bodies = [self.puck, self.top_mallet, self.bottom_mallet]

        # 目标,一个圆圈暂不知道用处
        self.bottom_target = Target([self.dim.center[0], self.dim.rink_bottom - 55], self.dim.target_radius)

        # 绘制界面
        pygame.init()
        # 创建一个窗口, 设置字体和标题
        self.screen = pygame.display.set_mode((self.dim.width, self.dim.height))
        self.font = pygame.font.SysFont("monospace", 30)
        pygame.display.set_caption('Air Hockey')
        # 绘制桌面
        self.screen.fill(self.dim.Black)
        for line in self.borders:
            pygame.draw.aalines(self.screen, self.dim.White, 0, (line.p1, line.p2), 1)
        pygame.draw.aalines(self.screen, self.dim.White, 0, (self.center_line.p1, self.center_line.p2), 1)
        # 设置AI
        # self.bottom_ai_motion = PlayerMotion()
        self.bot_mallet_motion = ControlledMotion()
        # self.top_ai_motion = RandomMotion()
        self.top_mallet_motion = ControlledMotion()

        # 配对击球器和相应的运动产生器
        self.motions = MotionRegistry()
        self.motions.add(self.bottom_mallet, self.bot_mallet_motion)
        self.motions.add(self.top_mallet, self.top_mallet_motion)

        # 记录进球数与现在的状态
        self.score = Score(self.dim)

        # 加入AI
        self.bottom_ai = AI(self.bottom_mallet, self.puck, mode='bottom', dim=self.dim)
        self.top_ai = AI(self.top_mallet, self.puck, mode='top', dim=self.dim)

        # # Initialize a video writer
        # self.writer = None
        # if video_file is not None:
        #     if os.path.isfile(video_file): os.remove(video_file)
        #     # VideoWriter(filename, fourcc, fps, frameSize, isColor)
        #     # 第一个参数保存文件的路径，第二个参数fourcc指定编码器，fps帧率，frameSize图像的大小，isColor是否为彩色
        #     self.writer = cv2.VideoWriter(video_file, cv2.VideoWriter_fourcc(*'PIM1'), 30,
        #                                   (self.dim.width, self.dim.height - self.dim.vertical_margin * 2))
        #
        # # Allocate memory for frame
        # self.frame = np.zeros((self.dim.width, self.dim.height, 3), dtype=np.uint8)
        # # 裁剪一下
        # self.cropped_frame = np.zeros((self.dim.height - 2 * self.dim.vertical_margin, self.dim.width, 3),
        #                               dtype=np.uint8)

        self.distance = P.max_distance
        # 重置游戏
        self.reset()

    def _draw(self, puck, top_mallet, bottom_mallet):

        draw_puck = self.use_object['puck']
        draw_top_mallet = self.use_object['top_mallet']

        # 绘制桌面
        self.screen.fill(self.dim.Black)
        for line1 in self.borders:
            pygame.draw.aalines(self.screen, self.dim.White, 0, (line1.p1, line1.p2), 1)
        pygame.draw.aalines(self.screen, self.dim.White, 0, (self.center_line.p1, self.center_line.p2), 1)
        # 绘制球和底部的击球器和击球器标志线
        # Draw robot that controls bottom mallet
        pygame.draw.line(self.screen, (184, 184, 184),
                         [self.dim.table_left, bottom_mallet[1]],
                         [self.dim.table_right, bottom_mallet[1]], 1)
        pygame.draw.circle(self.screen, (0, 0, 139), self.bottom_target.position, self.bottom_target.radius, 1)
        pygame.draw.circle(self.screen, self.dim.White, self.bottom_mallet.get_position(), self.dim.mallet_radius, 0)

        if draw_top_mallet:
            pygame.draw.circle(self.screen, (0, 0, 139), self.top_mallet.get_position(), self.dim.mallet_radius, 0)
            pass
            # self.screen.blit(self.sprites['top_mallet'], top_mallet - self.dim.mallet_radius)

        if draw_puck:
            pygame.draw.circle(self.screen, self.dim.Red, self.puck.get_position(), self.dim.puck_radius, 0)
            pass

        # if self.writer:
        #     self.writer.write(self.cropped_frame[:, :, ::-1])

    def render(self, debug=False):
        self._draw(self.puck.position, self.top_mallet.position, self.bottom_mallet.position)
        self.screen.blit(self.font.render('%4d' % self.score.get_top(), 1, (200, 0, 0)), (0, 10))
        self.screen.blit(self.font.render('%4d' % self.score.get_bottom(), 1, (0, 200, 0)),
                         (0, self.dim.rink_bottom + 10))
        pygame.display.update()
        self.fclock.tick(self.fps)
        # self.frame[:] = pygame.surfarray.array3d(self.screen)
        # self.cropped_frame[:] = self.frame[:, self.dim.vertical_margin:-self.dim.vertical_margin, :].transpose(
        #     (1, 0, 2))

    def reset(self,
              scored=False,
              puck_was_hit=False,
              puck_is_at_the_bottom=False,
              distance_decreased=False,
              hit_the_border=False):

        draw_puck = self.use_object['puck']
        draw_top_mallet = self.use_object['top_mallet']

        # 重置冰球、两个击球器的位置
        if draw_puck:
            # self.puck.reset(self.dim, self.dim.rink_top, self.dim.center[1])
            # self.puck.reset(self.dim, self.dim.center[1], self.dim.rink_bottom-self.dim.mallet_radius-10) # 将冰球置于中线以下
            self.puck.reset(self.dim,self.dim.rink_top+self.dim.mallet_radius+10,self.dim.center[1] )
            # self.puck.reset(self.dim, self.dim.rink_top - self.dim.mallet_radius , self.dim.rink_top - self.dim.mallet_radius+1)
            self.bottom_mallet.reset(self.dim, self.dim.center[1], self.dim.rink_bottom)

        if draw_top_mallet:
            self.top_mallet.reset(self.dim, self.dim.rink_top, self.dim.center[1])

        self.motions.clear_all_motions()

        # Resolve possible interpenetration
        Collision.circle_circle([self.puck, self.top_mallet])
        Collision.circle_circle([self.top_mallet, self.bottom_mallet])
        # 计算小球是否在bottom_target这个圆圈里
        in_the_target = Collision.circle_circle([self.bottom_mallet, self.bottom_target], resolve=False)

        # 读取贴图
        # self.sprites, self.dominant_arm = load_sprites()
        # 画图
        self.render()

        puck_position = self.puck.get_position()
        puck_velocity = V.address_data(self.puck.get_velocity())
        bottom_mallet_position = self.bottom_mallet.get_position()
        bottom_mallet_velocity = V.address_data(self.bottom_mallet.get_velocity())
        top_mallet_position = self.top_mallet.get_position()
        top_mallet_velocity = V.address_data(self.top_mallet.get_velocity())

        puck_position_mode = bool(self.dim.center[1] <= puck_position[1] <= self.dim.rink_bottom)
        game_info = GameInfo([],
                             puck_position,
                             puck_velocity,
                             bottom_mallet_position,
                             bottom_mallet_velocity,
                             top_mallet_position,
                             top_mallet_velocity,
                             puck_was_hit,
                             puck_is_at_the_bottom,
                             distance_decreased,
                             hit_the_border,
                             in_the_target,
                             puck_position_mode)

        return game_info


    def step(self,
             robot_action=None,
             human_action=None,
             debug=False,
             n_steps=4):

        dt = 0.25  # dt is randomly in interval [1, 2)
        time_iter = dt * n_steps

        # 记录上一步的游戏状态
        past_bottom_pos = self.bottom_mallet.get_position()

        # 如果输入参数是None，就使用AI move
        if robot_action is None:
            if self.use_object['puck']:
                # robot_action = self.bottom_ai.move()
                robot_action = [0, 0]
            else:
                robot_action = [0, 0]
        if human_action is None:
            if self.use_object['top_mallet']:
                human_action = self.top_ai.move()
                # human_action = [0, 0]
            elif not self.use_object['puck']:
                human_action = [0, 0]
            else:
                human_action = [0, 0]

        self.bot_mallet_motion.set_motion(robot_action)
        self.top_mallet_motion.set_motion(self.top_ai.move())
        # self.bottom_ai_motion.update_motion(robot_action)

        # 用数组来储存n_steps循环中
        # puck_was_hit 和 border_was_hit 和 scored 的值

        n_puck_was_hit = np.zeros(n_steps, dtype=np.float32)
        n_hit_the_border = np.zeros(n_steps, dtype=np.float32)
        n_score_flag = np.zeros(n_steps, dtype=np.float32)

        for k in range(n_steps):

            # Clear forces from last frame
            for body in self.bodies:
                body.clear_accumulated_v()

            self.motions.update_motions()

            # Move bodies
            for body in self.bodies:
                body.speed_position_update(dt)

            # Check collisions between all possible pairs of bodies
            if self.use_object['top_mallet']:
                Collision.circle_circle([self.puck, self.top_mallet])

            Collision.circle_circle([self.top_mallet, self.bottom_mallet])

            if self.use_object['puck']:
                n_puck_was_hit[k] = bool(Collision.circle_circle([self.puck, self.bottom_mallet]))
            else:
                n_puck_was_hit[k] = False

            in_the_target = Collision.circle_circle([self.bottom_mallet, self.bottom_target], resolve=False)

            # Make sure all bodies are within their borders
            collided = [False, False, False]
            for i, body in enumerate(self.bodies):
                for border in body.borders:
                    if Collision.circle_line(body, border):
                        collided[i] = True
            n_hit_the_border[k] = collided[2]

            puck_is_at_the_bottom = self.puck.position[1] > self.dim.center[1]

            distance_decreased = False
            if puck_is_at_the_bottom:
                distance = V.magnitude(self.puck.position - self.bottom_mallet.position)
                distance_decreased = distance < self.distance
                self.distance = distance
            else:
                self.distance = P.max_distance

            _, n_score_flag[k] = self.score.update(self.puck)

        puck_position = self.puck.get_position()
        puck_velocity = V.address_data(self.puck.get_velocity())
        bottom_mallet_position = self.bottom_mallet.get_position()
        bottom_mallet_velocity = V.address_data(self.bottom_mallet.get_velocity())
        for i in range(len(past_bottom_pos)):
            if np.linalg.norm(past_bottom_pos[i] - self.bottom_mallet.get_position()[i]) < 1e-5:
                bottom_mallet_velocity[i] = 0
            else:
                pass
        top_mallet_position = self.top_mallet.get_position()
        top_mallet_velocity = V.address_data(self.top_mallet.get_velocity())
        puck_was_hit = np.any(n_puck_was_hit == 1)
        hit_the_border = np.any(n_hit_the_border == 1)

        scored = None
        score_flag = 0
        if np.any(n_score_flag == 1):
            score_flag = 1
            self.score.add_bottom()
            scored = 'bottom'
        elif np.any(n_score_flag == -1):
            score_flag = -1
            self.score.add_top()
            scored = 'top'

        puck_position_mode = bool(self.dim.center[1] <= puck_position[1] <= self.dim.rink_bottom)
        game_info = GameInfo([],
                             puck_position,
                             puck_velocity,
                             bottom_mallet_position,
                             bottom_mallet_velocity,
                             top_mallet_position,
                             top_mallet_velocity,
                             robot_action,
                             human_action,
                             scored,
                             score_flag,
                             puck_was_hit,
                             puck_is_at_the_bottom,
                             distance_decreased,
                             hit_the_border,
                             in_the_target,
                             time_iter,
                             puck_position_mode)

        return game_info


if __name__ == "__main__":
    air_hockey = AirHockey()
    while True:
        if any([event.type == pygame.QUIT for event in pygame.event.get()]): break
        air_hockey.step()
    pygame.quit()
