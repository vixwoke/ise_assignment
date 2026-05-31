import pygame
from config import (
    WIDTH, HEIGHT, FRAME_W, FRAME_H, PARTNER_HP, PARTNER_ANIM_SPEED,
    PARTNER_SHOT_INTERVAL, GRAVITY, JUMP_FORCE,
    PLAYER_CHAR_OFFSET_X, PLAYER_CHAR_OFFSET_Y,
    PLAYER_CHAR_HITBOX_W, PLAYER_CHAR_HITBOX_H
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

        # Partner Audio
        self.snd_shotgun = pygame.mixer.Sound("resources/audio/shotgun.wav")
        self.snd_shotgun.set_volume(0.4)
        self._shotgun_vol = 0.4

        # Gravity & Physics properties
        self.fall_speed = 0
        self.scale = 0.9
        self.on_ground = False

    @property
    def rect(self):
        # Character box matches player's hitbox dimensions
        return pygame.Rect(
            self.x, self.y,
            int(PLAYER_CHAR_HITBOX_W * self.scale),
            int(PLAYER_CHAR_HITBOX_H * self.scale),
        )

    def mute(self):
        self.snd_shotgun.set_volume(0)

    def unmute(self):
        self.snd_shotgun.set_volume(self._shotgun_vol)

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
        self.snd_shotgun.play()
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
            (int(FRAME_W * self.scale), int(FRAME_H * self.scale)),
        )
        # Offset drawing to align with top-left of hitbox
        frame_x = self.x - PLAYER_CHAR_OFFSET_X * self.scale
        frame_y = self.y - PLAYER_CHAR_OFFSET_Y * self.scale
        screen.blit(frame, (frame_x, frame_y))

    # Gravity
    def update_gravity(self, is_on_ground_fn):
        self.fall_speed += GRAVITY
        self.y += self.fall_speed

        feet_x = int(self.x + (FRAME_W / 2 - PLAYER_CHAR_OFFSET_X) * self.scale)
        feet_y = int(self.y + (FRAME_H - PLAYER_CHAR_OFFSET_Y) * self.scale)

        if is_on_ground_fn(feet_x, feet_y):
            while is_on_ground_fn(int(feet_x), int(feet_y)):
                feet_y -= 1
            self.y = feet_y - (FRAME_H - PLAYER_CHAR_OFFSET_Y) * self.scale
            self.fall_speed = 0
            self.on_ground = True
        else:
            self.on_ground = False

    def handle_jump(self, keys):
        if self.on_ground and keys[pygame.K_SPACE]:
            self.fall_speed = JUMP_FORCE
            self.set_animation("jump", self.anims["jump"])
            self.on_ground = False