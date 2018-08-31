import pygame

from entities import Player, Enemy, Ball
from constants import *

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
