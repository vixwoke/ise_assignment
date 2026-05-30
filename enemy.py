import math
import pygame
from config import (
    WIDTH, HEIGHT, FRAME_W, FRAME_H, ENEMY_HP, ENEMY_MAX_HP, ENEMY_SPEED,
    ENEMY_ANIM_SPEED, ENEMY_ATTACK_INTERVAL, ENEMY_ATTACK_DAMAGE,
    ENEMY_PARTNER_DAMAGE, ENEMY_REGEN_INTERVAL, ENEMY_REGEN_AMOUNT,
    ESCAPE_SPEED, GRAVITY,
    ENEMY_CHAR_OFFSET_X, ENEMY_CHAR_OFFSET_Y,
    ENEMY_CHAR_HITBOX_W, ENEMY_CHAR_HITBOX_H,
)


class Enemy:
    def __init__(self, normal_anims, wounded_anims):
        self.x = WIDTH // 2 + ENEMY_CHAR_OFFSET_X
        self.y = HEIGHT // 2 + ENEMY_CHAR_OFFSET_Y
        self.facing_right = True

        self.hp = ENEMY_HP
        self.max_hp = ENEMY_MAX_HP
        self.dead = False
        self.wounded = False

        self.normal_anims = normal_anims
        self.wounded_anims = wounded_anims
        self.anims = dict(normal_anims)

        self.action = "idle"
        self.animation = self.anims["idle"]
        self.frame_index = 0.0

        self.attack_timer = 0
        self.regen_timer = 0
        self.has_hit_partner = False

        self.march = False
        self.locked = False
        self.escape = False

        self.waiting_after_civic = False

        # OPTIONAL: cleaner phase control
        self.phase = 0  # 0 = civic, 1 = partner

        self.fall_speed = 0
        self.on_ground = False

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, ENEMY_CHAR_HITBOX_W, ENEMY_CHAR_HITBOX_H)

    def set_animation(self, action, frames):
        self.action = action
        self.animation = frames
        self.frame_index = 0.0
        self.has_hit_partner=False

    def make_wounded(self):
        if self.wounded:
            return
        self.wounded = True
        self.anims = dict(self.wounded_anims)
        self.animation = self.anims["hurt"]
        self.frame_index = 0.0

    def make_normal(self):
        if not self.wounded:
            return
        self.wounded = False
        self.anims = dict(self.normal_anims)
        self.action = "idle"
        self.animation = self.anims["idle"]
        self.frame_index = 0.0

    def hurt_from_damage(self):
        self.hp -= 1
        if self.hp < 1:
            self.hp = 1
        if self.hp < self.max_hp:
            self.make_wounded()
        self.set_animation("hurt", self.anims["hurt"])

    # -------------------------
    # GRAVITY
    # -------------------------
    def update_gravity(self, is_on_ground_fn, scale):
        self.fall_speed += GRAVITY
        self.y += self.fall_speed

        feet_x = int(self.x + (FRAME_W / 2 - ENEMY_CHAR_OFFSET_X) * scale)
        feet_y = int(self.y + (FRAME_H - ENEMY_CHAR_OFFSET_Y) * scale)

        if is_on_ground_fn(feet_x, feet_y):
            while is_on_ground_fn(int(feet_x), int(feet_y)):
                feet_y -= 1
            self.y = feet_y - (FRAME_H - ENEMY_CHAR_OFFSET_Y) * scale
            self.fall_speed = 0
            self.on_ground = True
        else:
            self.on_ground = False

    # -------------------------
    # MAIN AI
    # -------------------------
    def update_march(self, now, partner_x, partner_y, partner_dead,
                     civic_x, civic_y, target_partner, civic_hit, scale):

        if not self.march or self.dead or self.locked:
            return civic_x, civic_y, target_partner, civic_hit

        # switch phase after civic hit
        if self.waiting_after_civic:
            self.phase = 1
            target_partner = True
            self.waiting_after_civic = False

        # escape
        if self.escape:
            self.x -= ESCAPE_SPEED
            self.set_animation("run", self.anims["run"])
            self.facing_right = False
            return civic_x, civic_y, target_partner, civic_hit

        # partner dead
        if partner_dead:
            if now - self.attack_timer >= ENEMY_ATTACK_INTERVAL:
                self.attack_timer = now
                self.set_animation("attack", self.anims["attack"])
                self.has_hit_partner = False
            return civic_x, civic_y, target_partner, civic_hit

        # -------------------------
        # TARGETING (FIXED: X ONLY)
        # -------------------------
        if self.phase == 1:
            tx = partner_x
        else:
            tx = civic_x

        dx = tx - self.x
        distance = abs(dx)

        # MOVE ONLY X
        if distance > 60:
            self.x += ENEMY_SPEED if dx > 0 else -ENEMY_SPEED
            self.action = "walk"
            self.animation = self.anims["walk"]
            self.facing_right = dx > 0

        else:
                if self.action != "attack":
                    self.set_animation("attack", self.anims["attack"])

                current_frame = int(self.frame_index)
                if current_frame == 4 and not civic_hit:
                    civic_x += 100
                    civic_y += 100
                    civic_hit = True
                    self.waiting_after_civic = True

        return civic_x, civic_y, target_partner, civic_hit

    # -------------------------
    # DAMAGE PLAYER
    # -------------------------
    def damage_player(self, player, now):
        if self.action != "attack" or player.action == "hurt":
            return
        frame = int(self.frame_index)
        if not (4 <= frame <= 5):
            return

        if self.facing_right:
            attack_rect = pygame.Rect(self.x + 20, self.y - 20, 20, 50)
        else:
            attack_rect = pygame.Rect(self.x - 70, self.y - 20, 30, 50)

        if attack_rect.colliderect(player.rect):
            player.take_damage(ENEMY_ATTACK_DAMAGE, now)

    # -------------------------
    # DAMAGE PARTNER
    # -------------------------
    def damage_partner(self, partner, now):
        if not partner or partner.dead:
            return

        frame = int(self.frame_index)
        partner_rect = pygame.Rect(partner.x + 35, partner.y + 30, 90, 70)

        if self.action == "attack" and frame == 4 and not self.has_hit_partner:
            attack_rect = pygame.Rect(self.x + 20, self.y - 20, 60, 70)

            if attack_rect.colliderect(partner_rect):
                partner.hp -= ENEMY_PARTNER_DAMAGE
                self.has_hit_partner = True

                if partner.hp > 0:
                    partner.set_animation("hurt", partner.anims["hurt"])
                else:
                    partner.hp = 0
                    partner.dead = True
                    partner.set_animation("dead", partner.anims["dead"])

    # -------------------------
    # OTHER SYSTEMS (UNCHANGED)
    # -------------------------
    def update_auto_attack(self, now):
        if self.dead or self.march or self.locked:
            return
        if self.action != "attack" and now - self.attack_timer >= ENEMY_ATTACK_INTERVAL:
            self.attack_timer = now
            self.set_animation("attack", self.anims["attack"])

    def update_regen(self, now):
        if now - self.regen_timer >= ENEMY_REGEN_INTERVAL:
            self.regen_timer = now
            if not self.dead:
                self.hp += ENEMY_REGEN_AMOUNT
                if self.hp > self.max_hp:
                    self.hp = self.max_hp
                if self.hp == self.max_hp:
                    self.make_normal()

    def update_animation(self):
        self.frame_index += ENEMY_ANIM_SPEED

        if self.frame_index >= len(self.animation):
            if self.action == "attack":
                self.action = "idle"
                self.animation = self.anims["idle"]
                self.frame_index = 0.0
            elif self.action == "hurt":
                self.action = "idle"
                self.animation = self.anims["idle"]
                self.frame_index = 0.0
            elif self.action == "dead":
                self.frame_index = len(self.animation) - 1
            else:
                self.frame_index = 0.0

    def draw(self, screen, scale):
        frame = self.animation[int(self.frame_index)]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        frame = pygame.transform.scale(
            frame,
            (int(FRAME_W * scale), int(FRAME_H * scale)),
        )

        screen.blit(
            frame,
            (
                self.x - ENEMY_CHAR_OFFSET_X * scale,
                self.y - ENEMY_CHAR_OFFSET_Y * scale
            )
        )