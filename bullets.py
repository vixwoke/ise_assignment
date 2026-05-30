import math
import pygame
from config import BULLET_SPEED, PARTNER_BULLET_SPEED, WIDTH, HEIGHT, PARTNER_SPREAD_ANGLES


class BulletManager:
    def __init__(self):
        self.player_bullets = []
        self.partner_bullets = []

    def add_player_bullet(self, x, y, facing_right):
        direction = 1 if facing_right else -1
        self.player_bullets.append([x, y, direction])

    def add_partner_bullets(self, px, py, target_x, target_y):
        for angle in PARTNER_SPREAD_ANGLES:
            dx = target_x - px
            dy = target_y - py
            distance = math.sqrt(dx * dx + dy * dy)
            if distance == 0:
                distance = 1
            dir_x = dx / distance
            dir_y = dy / distance
            radians = math.radians(angle)
            spread_x = dir_x * math.cos(radians) - dir_y * math.sin(radians)
            spread_y = dir_x * math.sin(radians) + dir_y * math.cos(radians)
            self.partner_bullets.append([px, py, spread_x, spread_y])

    def update_player_bullets(self, enemy_rect):
        hit = False
        to_remove = []
        for bullet in self.player_bullets:
            bullet[0] += BULLET_SPEED * bullet[2]
            bullet_rect = pygame.Rect(bullet[0], bullet[1], 12, 12)
            if bullet_rect.colliderect(enemy_rect):
                to_remove.append(bullet)
                hit = True
        self.player_bullets = [
            b for b in self.player_bullets
            if b not in to_remove and 0 <= b[0] <= WIDTH
        ]
        return hit

    def update_partner_bullets(self, enemy_rect):
        hit = False
        to_remove = []
        for bullet in self.partner_bullets:
            bullet[0] += bullet[2] * PARTNER_BULLET_SPEED
            bullet[1] += bullet[3] * PARTNER_BULLET_SPEED
            bullet_rect = pygame.Rect(bullet[0], bullet[1], 10, 10)
            if bullet_rect.colliderect(enemy_rect):
                to_remove.append(bullet)
                hit = True
            elif (bullet[0] < -50 or bullet[0] > WIDTH + 50
                  or bullet[1] < -50 or bullet[1] > HEIGHT + 50):
                to_remove.append(bullet)
        for bullet in to_remove:
            if bullet in self.partner_bullets:
                self.partner_bullets.remove(bullet)
        return hit

    def draw_player_bullets(self, screen):
        for bullet in self.player_bullets:
            pygame.draw.circle(screen, (255, 220, 50), (int(bullet[0]), int(bullet[1])), 4)

    def draw_partner_bullets(self, screen):
        for bullet in self.partner_bullets:
            pygame.draw.circle(screen, (50, 200, 255), (int(bullet[0]), int(bullet[1])), 5)

    def draw(self, screen):
        self.draw_player_bullets(screen)
        self.draw_partner_bullets(screen)
