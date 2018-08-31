import pygame
import math
import random

# Constants
TITLE = "Pseudo-intelligent PingPong"

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
FRAMERATE = 60
BACKGROUND_COLOR = (16, 50, 56)
PLAYER_COLOR = (57, 127, 219)
ENEMY_COLOR = (193, 52, 27)
BALL_COLOR = (81, 114, 16)

SCORE_COLOR = (224, 109, 33)
SCORE_SIZE = 50
PLAYER_SCORE_POSITION = (SCREEN_WIDTH / 4, SCORE_SIZE / 2)
ENEMY_SCORE_POSITION  = (SCREEN_WIDTH * 3 / 4, SCORE_SIZE / 2)

MIDDLE_RECTS_COLOR = (175, 158, 22)

class PingPong:

    def __init__(self):
        self.middle_rects = self.create_middle_rects(5, 15)

        # Initialize entities
        self.player = Player(20, 20, 100, PLAYER_COLOR)
        self.enemy = Enemy(SCREEN_WIDTH - 20 - 20, 20, 100, ENEMY_COLOR)
        self.ball = Ball(12, 600)

        # Initialize fonts
        self.score_font = pygame.font.Font("8bit.ttf", SCORE_SIZE)
        self.player_score_label = self.score_font.render(str(self.player.score), True, SCORE_COLOR)
        self.enemy_score_label = self.score_font.render(str(self.enemy.score), True, SCORE_COLOR)

    def update(self, delta):
        # Update entities
        self.player.update(delta)
        self.enemy.update(delta)
        self.ball.update(delta)

        # Check if the ball collides with one of both paddles
        ball_collides_player = (self.ball.rect.colliderect(self.player.rect) and
                                self.ball.velocity.x < 0)
        ball_collides_enemy = (self.ball.rect.colliderect(self.enemy.rect) and
                                self.ball.velocity.x > 0)

        if ball_collides_player:
            self.ball.rect.x = self.player.rect.topright[0]

            # Clamp the value between 0 and player's height
            hit_relative_y = max(0, min(self.ball.rect.topleft[1] - self.player.rect.topright[1],
                                self.player.rect.height))

            self.ball.change_angle(hit_relative_y, self.player.rect.height)
            self.enemy.calculate_next_position(self.ball)
        elif ball_collides_enemy:
            self.ball.rect.x = self.enemy.rect.x - self.ball.radius * 2

            self.ball.velocity.x *= -1
            self.ball.predicted_y = -1

        # Increase score and update the label
        if self.ball.rect.topleft[0] <= 0:
            self.player.score += 1
            self.player_score_label = self.score_font.render(str(self.player.score), True, SCORE_COLOR)

            self.ball.reset()
        elif self.ball.rect.topright[0] >= SCREEN_WIDTH:
            self.enemy.score += 1
            self.enemy_score_label = self.score_font.render(str(self.enemy.score), True, SCORE_COLOR)

    def render(self, screen):
        # Render scores
        self.render_scores(screen)
        self.render_middle_rects(screen)

        # Render entities
        self.player.render(screen)
        self.enemy.render(screen)
        self.ball.render(screen)

    """ Returns an array of the rects that appear in the middle of the screen """
    def create_middle_rects(self, width, number):
        rects = []
        height = SCREEN_HEIGHT / number / 2

        for i in range(number):
            y = i * height * 2 + height / 2
            rect = pygame.Rect((SCREEN_WIDTH - width) / 2, y, width, height)
            rects.append(rect)

        return rects

    def render_middle_rects(self, screen):
        for rect in self.middle_rects:
            pygame.draw.rect(screen, MIDDLE_RECTS_COLOR, rect)

    def render_scores(self, screen):
        screen.blit(self.player_score_label, PLAYER_SCORE_POSITION)
        screen.blit(self.enemy_score_label, ENEMY_SCORE_POSITION)

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
        print(angle * 180 / math.pi)
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

def main():
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    game = PingPong()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.QUIT:
                 running = False

        # Time in seconds since the last call of tick
        delta = clock.tick(FRAMERATE) / 1000

        game.update(delta)
        screen.fill(BACKGROUND_COLOR)
        game.render(screen)

        # Update the window
        pygame.display.flip()

if __name__ == "__main__":
    main()
