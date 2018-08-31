import pygame
import random
import math

from constants import *

class Paddle:
    """ Base class for a paddle """

    def __init__(self, x_pos, width, height, speed, color):
        self.rect = pygame.Rect((x_pos, (SCREEN_HEIGHT - height) / 2), (width, height))
        self.color = color
        self.speed = speed
        self.velocity = pygame.math.Vector2(0, 1)

        self.score = 0

    def update(self, delta):
        pass

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class Player(Paddle):

    def __init__(self, x_pos, width, height, color):
        super().__init__(x_pos, width, height, 500, color)

    def update(self, delta):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.move_ip(self.velocity * self.speed * delta)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.move_ip(-self.velocity * self.speed * delta)

        # Clamp the y value between 0 and the window's width
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

    def update_score(self, font):
        self.score += 1
        self.text_score = font.render(str(self.score), True, (255, 0, 0))


class Enemy(Paddle):

    def __init__(self, x_pos, width, height, color):
        super().__init__(x_pos, width, height, 500, color)

        # Where the paddle has to move in the y axis
        self.predicted_y = (SCREEN_HEIGHT - height) / 2
        # The place where the ball collides with the paddle
        self.hit_location = 0

    def update(self, delta):
        if self.predicted_y - self.hit_location < self.rect.y:
            self.rect.move_ip(-self.velocity * self.speed * delta)
        if self.predicted_y - self.hit_location > self.rect.y:
            self.rect.move_ip(self.velocity * self.speed * delta)

    def calculate_next_position(self, ball):
        vx, vy = ball.velocity
        cx, cy = ball.rect.topright

        collision_x = 0
        while collision_x < self.rect.x:
            target_y = 0 if vy < 0 else SCREEN_HEIGHT - ball.radius * 2
            collision_x = cx + vx * (target_y - cy) / vy

            cx, cy = collision_x, target_y
            vy *= -1

        self.predicted_y = cy - vy * (self.rect.x - cx) / vx
        self.hit_location = random.randint(10, self.rect.height - 10)


class Ball:

    def __init__(self, radius, speed):
        appear_y = random.randint(SCREEN_HEIGHT / 4, SCREEN_HEIGHT * 3 / 4)
        self.rect = pygame.Rect(SCREEN_WIDTH / 2 - radius, appear_y - radius,
                                radius * 2, radius * 2)

        self.position = pygame.math.Vector2(SCREEN_WIDTH / 2 - radius, SCREEN_HEIGHT / 2 - radius)
        self.radius = radius
        self.speed = speed

        # Calculate velocity's angle
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        # print(angle * 180 / math.pi)
        #angle = math.radians(35)#math.pi / 4
        self.velocity = pygame.math.Vector2(math.cos(angle) * -1, -math.sin(angle))

    def update(self, delta):
        self.position += self.velocity * self.speed * delta
        self.update_position()

        if self.rect.y < 0:
            self.rect.y = 0
            self.velocity.y *= -1

        elif self.rect.y > SCREEN_HEIGHT - self.radius * 2:
            self.rect.y = SCREEN_HEIGHT - self.radius * 2
            self.velocity.y *= -1

    def render(self, screen):
        pygame.draw.rect(screen, BALL_COLOR, self.rect)

    """ Prepares the ball for a new match """
    def reset(self, direction=-1):
        # Put the ball in the middle
        self.position.x = SCREEN_WIDTH / 2 - self.radius
        self.position.y = random.randint(SCREEN_HEIGHT / 4, SCREEN_HEIGHT * 3 / 4) - self.radius
        self.update_position()

        # Set the angle
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        self.velocity.x = math.cos(angle) * direction
        self.velocity.y = -math.sin(angle)

    """ Changes the velocity angle depending on the part hitted by the ball """
    def change_angle(self, hit_position, height):
        angle = math.pi / 2 * hit_position / height - math.pi / 4

        self.velocity.x = math.cos(angle)
        self.velocity.y = math.sin(angle)

        if self.velocity.y == 0:
            self.velocity.y = math.sin(angle + 0.02)


    def update_position(self):
        self.rect.x = self.position.x
        self.rect.y = self.position.y
