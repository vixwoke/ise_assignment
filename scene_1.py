import pygame
from config import (
    WIDTH, HEIGHT, PLAYER_SPEED, ENEMY_SPEED, ESCAPE_SPEED,
    PLAYER_CHAR_OFFSET_X, ENEMY_CHAR_OFFSET_X
)

class Scene1Manager:
    def __init__(self, game):
        self.game = game
        self.phase = "intro_walk"
        self.start_time = pygame.time.get_ticks()
        self.phase_timer = self.start_time
        self.combat_start_time = None

        # Start positions off-screen
        self.game.player.x = -150
        self.game.partner.x = -250
        self.game.enemy.x = WIDTH + 300

        # Reset any active bullets
        self.game.bullets.player_bullets = []
        self.game.bullets.partner_bullets = []

        # Create screen overlay for fading
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surface.fill((0, 0, 0))
        self.fade_alpha = 0

    def update(self, now):
        # 30-second countdown check starting specifically after interactive combat begins
        if self.phase == "combat" and self.combat_start_time:
            if now - self.combat_start_time >= 30000:
                self.phase = "enemy_escape"
                self.phase_timer = now
                self.game.enemy.march = False

        if self.phase == "intro_walk":
            target_player_x = WIDTH // 4 + PLAYER_CHAR_OFFSET_X
            target_partner_x = 30

            player_reached = False
            partner_reached = False

            # Move Player
            if self.game.player.x < target_player_x:
                self.game.player.x += PLAYER_SPEED
                self.game.player.set_animation("walk", self.game.player.anims["walk"])
                self.game.player.facing_right = True
            else:
                self.game.player.set_animation("idle", self.game.player.anims["idle"])
                player_reached = True

            # Move Partner
            if self.game.partner.x < target_partner_x:
                self.game.partner.x += PLAYER_SPEED
                self.game.partner.set_animation("walk", self.game.partner.anims["walk"])
            else:
                self.game.partner.set_animation("idle", self.game.partner.anims["idle"])
                partner_reached = True

            self.game.enemy.x = WIDTH + 300

            if player_reached and partner_reached:
                self.phase = "intro_idle"
                self.phase_timer = now

        elif self.phase == "intro_idle":
            self.game.player.set_animation("idle", self.game.player.anims["idle"])
            self.game.partner.set_animation("idle", self.game.partner.anims["idle"])
            self.game.enemy.x = WIDTH + 300

            if now - self.phase_timer >= 2000:
                self.phase = "enemy_walk"
                self.game.enemy.x = WIDTH + 150

        elif self.phase == "enemy_walk":
            target_enemy_x = WIDTH // 2 + ENEMY_CHAR_OFFSET_X

            # Move Enemy left
            if self.game.enemy.x > target_enemy_x:
                self.game.enemy.x -= ENEMY_SPEED
                self.game.enemy.set_animation("walk", self.game.enemy.anims["walk"])
                self.game.enemy.facing_right = False
            else:
                self.game.enemy.set_animation("idle", self.game.enemy.anims["idle"])
                self.phase = "enemy_idle"
                self.phase_timer = now

        elif self.phase == "enemy_idle":
            self.game.player.set_animation("idle", self.game.player.anims["idle"])
            self.game.partner.set_animation("idle", self.game.partner.anims["idle"])
            self.game.enemy.set_animation("idle", self.game.enemy.anims["idle"])

            if now - self.phase_timer >= 3000:
                self.phase = "combat"
                self.combat_start_time = now
                self.game.enemy.march = True

        elif self.phase == "combat":
            pass

        elif self.phase == "enemy_escape":
            # Enemy runs away to the right
            self.game.enemy.x += ESCAPE_SPEED
            self.game.enemy.set_animation("run", self.game.enemy.anims["run"])
            self.game.enemy.facing_right = True

            self.game.player.set_animation("idle", self.game.player.anims["idle"])
            self.game.partner.set_animation("idle", self.game.partner.anims["idle"])

            if self.game.enemy.x > WIDTH + 150:
                self.phase = "fade_out"
                self.phase_timer = now
                self.fade_alpha = 0

        elif self.phase == "fade_out":
            elapsed = now - self.phase_timer
            self.fade_alpha = min(255, int((elapsed / 1000.0) * 255))

            self.game.player.set_animation("idle", self.game.player.anims["idle"])
            self.game.partner.set_animation("idle", self.game.partner.anims["idle"])

            if elapsed >= 1000:
                self.fade_alpha = 255
                self.game.reset_for_combat()
                self.phase = "fade_in"
                self.phase_timer = pygame.time.get_ticks()

        elif self.phase == "fade_in":
            elapsed = now - self.phase_timer
            self.fade_alpha = max(0, 255 - int((elapsed / 1000.0) * 255))

            if elapsed >= 1000:
                self.fade_alpha = 0
                self.game.current_scene = "combat"

    def draw_fade(self, screen):
        self.fade_surface.set_alpha(self.fade_alpha)
        screen.blit(self.fade_surface, (0, 0))