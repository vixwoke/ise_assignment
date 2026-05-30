import pygame
from config import (
    WIDTH, HEIGHT, FRAME_W, FRAME_H, PARTNER_HP, PARTNER_ANIM_SPEED,
    PARTNER_SHOT_INTERVAL,
)


class Partner:
    def __init__(self, anims):
        self.x = 30
        self.y = HEIGHT // 1.9
        self.hp = PARTNER_HP
        self.dead = False

        self.anims = anims
        self.action = "idle"
        self.animation = anims["idle"]
        self.frame_index = 0.0

        self.last_shot = 0

    def set_animation(self, action, frames):
        if self.action != action:
            self.action = action
            self.animation = frames
            self.frame_index = 0.0

    def try_shoot(self, now, bullet_manager, enemy_x, enemy_y):
        if self.dead or self.action == "hurt":
            return
        if now - self.last_shot < PARTNER_SHOT_INTERVAL:
            return

        self.last_shot = now
        self.set_animation("shoot", self.anims["shoot"])
        bullet_manager.add_partner_bullets(
            self.x + 90, self.y + 70,
            enemy_x + 20, enemy_y - 5,
        )

    def update_animation(self):
        self.frame_index += PARTNER_ANIM_SPEED

        if self.frame_index >= len(self.animation):
            if self.action == "shoot":
                self.set_animation("idle", self.anims["idle"])
            elif self.action == "hurt":
                if not self.dead:
                    self.set_animation("idle", self.anims["idle"])
            elif self.action == "dead":
                self.frame_index = len(self.animation) - 1
            else:
                self.frame_index = 0.0

    def draw(self, screen):
        frame = self.animation[int(self.frame_index)]
        frame = pygame.transform.scale(
            frame,
            (int(FRAME_W * 0.9), int(FRAME_H * 0.9)),
        )
        screen.blit(frame, (self.x, self.y))



