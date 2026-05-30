import pygame
import random
from config import (
    WIDTH, HEIGHT, FRAME_W, FRAME_H, PLAYER_SPEED, PLAYER_HP, PLAYER_MAX_HP,
    PLAYER_HIT_COOLDOWN, PLAYER_REGEN_INTERVAL, PLAYER_REGEN_AMOUNT,
    PLAYER_RAGE_REGEN_AMOUNT, MAX_SHOTS, RECHARGE_TIME,
    LEAP_SPEED, NORMAL_ANIM_SPEED, JUMP_ANIM_SPEED, RAGE_SCALE, DEFAULT_SCALE,
    GRAVITY, JUMP_FORCE,
    PLAYER_CHAR_OFFSET_X, PLAYER_CHAR_OFFSET_Y,
    PLAYER_CHAR_HITBOX_W, PLAYER_CHAR_HITBOX_H,
)


class Player:
    def __init__(self, anims, rage_anims):
        self.x = WIDTH // 4 + PLAYER_CHAR_OFFSET_X
        self.y = HEIGHT // 2 + PLAYER_CHAR_OFFSET_Y
        self.speed = PLAYER_SPEED
        self.facing_right = True

        self.hp = PLAYER_HP
        self.max_hp = PLAYER_MAX_HP
        self.dead = False

        self.anims = anims
        self.rage_anims = rage_anims
        self.action = "idle"
        self.animation = anims["idle"]
        self.frame_index = 0.0

        self.rage_mode = False
        self.scale = DEFAULT_SCALE

        self.shots = MAX_SHOTS
        self.recharging = False
        self.recharge_start = 0

        self.leaping = False
        self.leap_dx = 0
        self.leap_dy = 0

        self.attack_has_hit = False

        self.regen_timer = 0
        self.last_hit_time = 0

        # Gravity
        self.fall_speed = 0
        self.on_ground = True

    # Action predicates
    def can_walk(self):
        return self.action not in ["shoot", "attack", "recharge", "hurt", "dead"]

    def can_shoot(self):
        return self.action not in ["shoot", "attack", "recharge", "jump", "hurt", "dead"]

    def can_attack(self):
        return self.action not in ["shoot", "attack", "jump", "hurt", "dead"]

    def set_animation(self, action, frames):
        if self.action != action:
            self.action = action
            self.animation = frames
            self.frame_index = 0.0

    def interrupt_to_hurt(self):
        self.leaping = False
        self.leap_dx = 0
        self.leap_dy = 0
        self.recharging = False
        self.set_animation("hurt", self.anims["hurt"])

    def activate_rage(self):
        self.rage_mode = True
        self.anims["idle"] = self.rage_anims["idle"]
        self.anims["walk"] = self.rage_anims["walk"]
        self.anims["jump"] = self.rage_anims["jump"]
        self.anims["attack"] = self.rage_anims["attack"]
        self.anims["hurt"] = self.rage_anims["hurt"]
        self.anims["dead"] = self.rage_anims["dead"]
        self.anims["shoot"] = self.rage_anims["shoot"]
        self.scale = RAGE_SCALE
        self.set_animation("attack", self.anims["attack"])

    @property
    def regen_amount(self):
        return PLAYER_RAGE_REGEN_AMOUNT if self.rage_mode else PLAYER_REGEN_AMOUNT

    @property
    def rect(self):
        return pygame.Rect(
            self.x, self.y,
            int(PLAYER_CHAR_HITBOX_W * self.scale),
            int(PLAYER_CHAR_HITBOX_H * self.scale),
        )

    def clamp_to_screen(self):
        char_scaled_w = PLAYER_CHAR_HITBOX_W * self.scale
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - char_scaled_w:
            self.x = WIDTH - char_scaled_w
        if self.y < 0:
            self.y = 0
        if self.y > HEIGHT:
            self.dead = True

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
        if self.can_walk() and keys[pygame.K_SPACE] and self.on_ground:
            self.fall_speed = JUMP_FORCE
            self.set_animation("jump", self.anims["jump"])
            self.on_ground = False

    # Input handling
    def handle_movement(self, keys):
        if not self.can_walk():
            return
        dx = 0
        moving = False
        if keys[pygame.K_a]:
            dx = -self.speed
            moving = True
            self.facing_right = False
        if keys[pygame.K_d]:
            dx = self.speed
            moving = True
            self.facing_right = True
        self.x += dx
        if self.action not in ["attack", "shoot", "hurt", "dead", "recharge", "jump"]:
            if moving:
                self.set_animation("walk", self.anims["walk"])
            else:
                self.set_animation("idle", self.anims["idle"])

    def handle_shoot(self, bullet_manager, moving):
        if not self.rage_mode:
            if self.can_shoot() and not moving:
                if self.shots <= 0:
                    self.recharging = True
                    self.recharge_start = pygame.time.get_ticks()
                    self.set_animation("recharge", self.anims["recharge"])
                else:
                    self.shots -= 1
                    self.set_animation("shoot", self.anims["shoot"])
                    bullet_manager.add_player_bullet(
                        self.x + 40, self.y + 35, self.facing_right
                    )
        else:
            if self.can_attack():
                self.recharging = False
                self.attack_has_hit = False
                self.set_animation("shoot", self.anims["shoot"])
                self.leaping = True
                self.leap_dx = LEAP_SPEED if self.facing_right else -LEAP_SPEED
                self.leap_dy = 0

    def handle_attack(self):
        if not self.can_attack():
            return
        self.recharging = False
        self.attack_has_hit = False
        if self.rage_mode:
            chosen = random.choice(self.rage_anims["attack_list"])
            self.set_animation("attack", chosen)
        else:
            self.set_animation("attack", self.anims["attack"])

    # Per-frame updates
    def update_leap(self, enemy_rect):
        if self.leaping:
            future = pygame.Rect(self.x + self.leap_dx, self.y - 30 + self.leap_dy, 50, 70)
            if future.colliderect(enemy_rect):
                self.leap_dx = 0
                self.leap_dy = 0
            self.x += self.leap_dx
            self.y += self.leap_dy

    def update_recharge(self, now):
        if self.recharging and now - self.recharge_start >= RECHARGE_TIME:
            self.recharging = False
            self.shots = MAX_SHOTS
            if self.action == "recharge":
                self.set_animation("idle", self.anims["idle"])

    def update_regen(self, now):
        if now - self.regen_timer >= PLAYER_REGEN_INTERVAL:
            self.regen_timer = now
            if self.hp > 0:
                self.hp += self.regen_amount
                if self.hp > self.max_hp:
                    self.hp = self.max_hp

    def take_damage(self, damage, now):
        if now - self.last_hit_time < PLAYER_HIT_COOLDOWN:
            return False
        self.last_hit_time = now
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            self.leaping = False
            self.leap_dx = self.leap_dy = 0
            self.recharging = False
            self.set_animation("dead", self.anims["dead"])
        else:
            self.interrupt_to_hurt()
        return True

    def get_attack_rect(self):
        if self.facing_right:
            return pygame.Rect(self.x + 80, self.y - 30, 20, 50)
        return pygame.Rect(self.x - 10, self.y - 30, 20, 50)

    def get_leap_rect(self):
        if self.facing_right:
            return pygame.Rect(self.x + 40, self.y - 40, 140, 90)
        return pygame.Rect(self.x - 90, self.y - 40, 140, 90)

    def update_animation(self):
        if self.action == "jump":
            self.frame_index += JUMP_ANIM_SPEED
        else:
            self.frame_index += NORMAL_ANIM_SPEED

        if self.frame_index >= len(self.animation):
            if self.action in ["idle", "walk"]:
                self.frame_index = 0
            elif self.action == "jump":
                self.set_animation("idle", self.anims["idle"])
            elif self.action == "shoot":
                self.leaping = False
                self.leap_dx = self.leap_dy = 0
                self.set_animation("idle", self.anims["idle"])
            elif self.action == "dead":
                self.frame_index = len(self.animation) - 1
            elif self.action == "hurt":
                self.set_animation("idle", self.anims["idle"])
            else:
                self.set_animation("idle", self.anims["idle"])

    def draw(self, screen):
        frame = self.animation[int(self.frame_index)]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        frame = pygame.transform.scale(
            frame,
            (int(FRAME_W * self.scale), int(FRAME_H * self.scale)),
        )
        frame_x = self.x - PLAYER_CHAR_OFFSET_X * self.scale
        frame_y = self.y - PLAYER_CHAR_OFFSET_Y * self.scale
        screen.blit(frame, (frame_x, frame_y))
