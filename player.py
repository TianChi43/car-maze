import pygame
import math


class Player(pygame.sprite.Sprite):
    def __init__(self, center_x, center_y, forward_angle):
        super().__init__()
        self.width = 100
        self.height = 50
        self.forward_angle = forward_angle  # 在游戏坐标系中从顺时针转动的角度
        self.image_source = pygame.image.load("static/images/car.png").convert()
        self.image = pygame.transform.scale(self.image_source, (self.width, self.height))
        self.image = pygame.transform.rotate(self.image, -self.forward_angle)
        self.image.set_colorkey("black")
        self.rect = self.image.get_rect()
        self.rect.center = (center_x, center_y)
        self.last_time = pygame.time.get_ticks()  # 返回当前时刻,ticks()单位是毫秒
        self.delta_time = 0  # 相邻两帧之间的时间间隔

        self.move_velocity_limit = 220  # 移动速度的上限
        self.move_velocity = 0  # 当前的移动速度
        self.move_acc = 600  # 加速度 每秒增加600
        self.rotate_velocity_limit = 140  # 角速度的上限
        self.rotate_velocity = 0  # 角速度
        self.friction = 0.9  # 摩擦力

        self.crash_sound = pygame.mixer.Sound("static/sounds/crash.mp3")
        self.crash_sound.set_volume(0.1)
        self.move_sound = pygame.mixer.Sound("static/sounds/move.mp3")
        self.move_sound.set_volume(0.3)
        self.move_voice_channel = pygame.mixer.Channel(7)

    def update_delta_time(self):
        cur_time = pygame.time.get_ticks()
        self.delta_time = (cur_time - self.last_time) / 1000  # 转化成秒
        self.last_time = cur_time

    def input(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_UP]:
            self.move_velocity += self.move_acc * self.delta_time
            self.move_velocity = min(self.move_velocity_limit, self.move_velocity)
            if not self.move_voice_channel.get_busy():
                self.move_voice_channel.play(self.move_sound)
        elif key_pressed[pygame.K_DOWN]:
            self.move_velocity -= self.move_acc * self.delta_time
            self.move_velocity = max(-self.move_velocity_limit, self.move_velocity)
            if not self.move_voice_channel.get_busy():
                self.move_voice_channel.play(self.move_sound)
        else:
            self.move_velocity = int(self.move_velocity * self.friction)
            if self.move_voice_channel.get_busy():
                self.move_voice_channel.stop()
        sign = 1
        if self.move_velocity < 0:
            sign = -1
        if key_pressed[pygame.K_RIGHT]:
            self.rotate_velocity = self.rotate_velocity_limit * sign
        elif key_pressed[pygame.K_LEFT]:
            self.rotate_velocity = -self.rotate_velocity_limit * sign
        else:
            self.rotate_velocity = 0

    def rotate(self, direction=1):
        self.forward_angle += self.rotate_velocity * self.delta_time * direction
        self.image = pygame.transform.scale(self.image_source, (self.width, self.height))
        self.image = pygame.transform.rotate(self.image, -self.forward_angle)
        self.image.set_colorkey("black")
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def move(self, direction=1):
        if direction == 1 and abs(self.move_velocity) > 50:
            self.rotate()  # 只有车在前进或后退时，车身角度才会变化；原地不动打反向盘，车身是不变的
        vx = self.move_velocity * math.cos(math.pi * self.forward_angle / 180) * direction
        vy = self.move_velocity * math.sin(math.pi * self.forward_angle / 180) * direction
        self.rect.x += vx * self.delta_time
        self.rect.y += vy * self.delta_time
        if direction == -1 and abs(self.move_velocity) > 50:
            self.rotate()  # 只有车在前进或后退时，车身角度才会变化；原地不动打反向盘，车身是不变的

    def update(self):
        self.update_delta_time()
        self.input()
        self.move()

    def crash(self):  # 撞墙了
        self.crash_sound.play()
        self.move(-1)  # 让小车退回来
        if self.move_velocity >= 0:
            self.move_velocity = min(-self.move_velocity, -100)
        else:
            self.move_velocity = max(self.move_velocity, 100)
        self.rotate_velocity *= -1
