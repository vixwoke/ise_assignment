from timeline import TimelineManager
import pygame
import random
import sys
from config import (
    WIDTH, HEIGHT, FPS, FRAME_W, FRAME_H,
    ENDING_TIME, ESCAPE_TIME, ENDGAME_TIME, ENEMY_TARGET_TIME, MUSIC_PATH,
    MUSIC_VOLUME, FONT_NAME, FONT_SIZE, DEBUG, PARTNER_DEATH_PAUSE,
    ESCAPE_SPEED,RAGE_TRIGGER_TIME, RAGE_SCALE,ENEMY_PHASE_1_TIME,
    BG_SKY_PATH, BG_MOON_PATH, BG_CLOUDS_PATH, BG_ROCKS_PATH, BG_GROUND_PATH,
    MOON_X, MOON_Y, MOON_SCALE_W,
    PLAYER_CHAR_OFFSET_X, PLAYER_CHAR_OFFSET_Y,
    PLAYER_CHAR_HITBOX_W, PLAYER_CHAR_HITBOX_H,
    ENEMY_CHAR_OFFSET_X, ENEMY_CHAR_OFFSET_Y,
    ENEMY_CHAR_HITBOX_W, ENEMY_CHAR_HITBOX_H,
    DEFAULTBLUE, DEFAULTGREEN, DEFAULTRED, DEFAULTWHITE,
    GRID_COLOR, GRID_SPACING, GRID_ALPHA,
)
from sprites import (
    load_player_anims, load_rage_anims, load_enemy_anims,
    load_partner_anims, load_civic_img,
)
from player import Player
from enemy import Enemy
from partner import Partner
from bullets import BulletManager
from end_screen import EndScreen

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("maingame.py")
        try:
            pygame.mixer.music.load("resources/audio/musics/waking demon.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except FileNotFoundError:
            pass
        self.clock = pygame.time.Clock()
        try:
            self.font = pygame.font.Font("resources/fonts/" + FONT_NAME + ".ttf", FONT_SIZE)
            self.debug_font = pygame.font.Font("resources/fonts/" + FONT_NAME + ".ttf", 14)
            self.debug_info_font = pygame.font.Font("resources/fonts/" + FONT_NAME + ".ttf", 16)
        except FileNotFoundError:
            self.font = pygame.font.SysFont(None, FONT_SIZE)
            self.debug_font = pygame.font.SysFont(None, 14)
            self.debug_info_font = pygame.font.SysFont(None, 16)

        # Backgrounds (layered)
        self.bg_sky = self._load_bg(BG_SKY_PATH, (20, 20, 40))
        self.bg_clouds = self._load_bg(BG_CLOUDS_PATH, None, alpha=True)
        self.bg_rocks = self._load_bg(BG_ROCKS_PATH, None, alpha=True)
        self.bg_ground = self._load_bg(BG_GROUND_PATH, None, alpha=True)

        moon_raw = pygame.image.load(BG_MOON_PATH).convert_alpha()
        scale = MOON_SCALE_W / moon_raw.get_width()
        self.moon_w = int(moon_raw.get_width() * scale)
        self.moon_h = int(moon_raw.get_height() * scale)
        self.bg_moon_original = pygame.transform.scale(moon_raw, (self.moon_w, self.moon_h))
        self.bg_moon = self.bg_moon_original.copy()

        # Originals for lightning flash effect
        self.bg_sky_original = self.bg_sky.copy()
        self.bg_clouds_original = self.bg_clouds.copy()

        # Load assets
        player_normal, player_wounded = load_player_anims()
        rage_normal, rage_wounded = load_rage_anims()
        enemy_normal, wounded_shoot, wounded_scar = load_enemy_anims()
        partner_anims = load_partner_anims()
        self.civic_img = load_civic_img()

        # Entities

        self.player = Player(
            player_normal,
            player_wounded,
            rage_normal,
            rage_wounded
        )
        self.enemy = Enemy(
            enemy_normal,
            wounded_shoot,
            wounded_scar
        )
        self.partner = Partner(partner_anims)
        self.bullets = BulletManager()
        self.timeline = TimelineManager(self)

        # Civic
        self.civic_x = self.partner.x + 60
        self.civic_y = self.partner.y + 55
        self.civic_hit = False
        self.target_partner = False

        # Timing
        self.start_time = pygame.time.get_ticks()
        self.enemy_start_time = self.start_time
        self.player.regen_timer = self.start_time
        self.player.last_hit_time = 0
        self.enemy.attack_timer = self.start_time
        self.enemy.regen_timer = self.start_time
        self.partner.last_shot = self.start_time

        #Transition
        self.fade_alpha = 0
        self.fade_state = "none" # Options: "none", "fading_out", "black", "fading_in"
        self.fade_timer = 0
        self.enemy_fleeing = False
        self.interlude_pending = False

        # Debug moon toggle with smooth transition
        self.moon_is_red = True
        self.moon_red(True)
        self.moon_red(False, ENEMY_PHASE_1_TIME)
        self.moon_btn_rect = pygame.Rect(WIDTH - 150, 55, 160, 30)

        # Lightning animation (sky & clouds flash)
        self.lightning_state = "idle"
        self.lightning_state_timer = self.start_time + random.randint(3000, 8000)
        self.lightning_sky_intensity = 0.0
        self.lightning_clouds_intensity = 0.0
        self.lightning_remaining_flashes = 0
        self.lightning_cloud_delay = 0

        # Level tracking
        self.level = 1
        # Partner death tracking
        self.partner_death_handled = False
        self.partner_death_time = 0

        # Ending
        self.ending_triggered = False
        self.can_kill = False
        self.kill = False
        self.game_end = False
        self.game_result = ""
        # Pause Functionality
        self.paused = False
        self.pause_start_time = 0
        self.total_paused_time = 0
        self.return_to_menu = False
        self.muted = False
        self.debug_enabled = DEBUG
        self.resume_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 50)
        self.menu_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 50)
        # Pause button on HUD during gameplay
        self.pause_btn = pygame.Rect(WIDTH - 140, 10, 130, 35)
        # Pause UI Audio
        self.snd_ui = pygame.mixer.Sound("resources/audio/ui_click.wav")
        self.snd_ui.set_volume(0.6)
        # End Screen
        self.end_screen = EndScreen(self.screen, self.font)
        self.damage_flash_alpha = 0

        # 1. Rain System
        self.rain_drops = []
        for _ in range(120):  # Create 120 raindrops
            rx = random.randint(-200, WIDTH)
            ry = random.randint(-HEIGHT, HEIGHT)
            speed = random.randint(15, 25)
            self.rain_drops.append([rx, ry, speed])

        # 2. Screen Shake Tracker
        self.shake_frames = 0
    @staticmethod
    def _load_bg(path, fallback_color=None, alpha=False):
        """Load a background image, falling back to a solid surface if missing."""
        try:
            img = pygame.image.load(path)
            return img.convert_alpha() if alpha else img.convert()
        except FileNotFoundError:
            surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA if alpha else 0)
            if fallback_color:
                surf.fill(fallback_color)
            return surf

    def _apply_moon_color(self, t):
        self.bg_moon = self.bg_moon_original.copy()
        gb = int(255 * (1 - t))
        gb = max(0, min(255, gb))
        self.bg_moon.fill((255, gb, gb), None, pygame.BLEND_RGB_MULT)

    def moon_red(self, enable, duration=0):
        if enable:
            if duration <= 0:
                self.moon_current_t = 1.0
                self._apply_moon_color(1.0)
                self.moon_transition_duration = 0
            else:
                self.moon_transition_start = pygame.time.get_ticks()
                self.moon_transition_duration = duration
                self.moon_start_t = self.moon_current_t
                self.moon_target_t = 1.0
        else:
            if duration <= 0:
                self.moon_current_t = 0.0
                self._apply_moon_color(0.0)
                self.moon_transition_duration = 0
            else:
                self.moon_transition_start = pygame.time.get_ticks()
                self.moon_transition_duration = duration
                self.moon_start_t = self.moon_current_t
                self.moon_target_t = 0.0

    def _update_moon_transition(self, now):
        if self.moon_transition_duration <= 0:
            return
        elapsed = now - self.moon_transition_start
        progress = min(elapsed / self.moon_transition_duration, 1.0)
        self.moon_current_t = self.moon_start_t + (self.moon_target_t - self.moon_start_t) * progress
        self._apply_moon_color(self.moon_current_t)
        if progress >= 1.0:
            self.moon_transition_duration = 0

    def _update_lightning(self, now):
        if self.lightning_state == "idle":
            if now >= self.lightning_state_timer:
                self.lightning_remaining_flashes = random.randint(1, 3)
                self.lightning_state = "sky_flash"
                self.lightning_state_timer = now + 120
                self.lightning_sky_intensity = 1.0
        elif self.lightning_state == "sky_flash":
            remaining = self.lightning_state_timer - now
            if remaining <= 0:
                self.lightning_sky_intensity = 0.0
                self.lightning_cloud_delay = random.randint(0, 1000)
                self.lightning_state = "cloud_wait"
                self.lightning_state_timer = now + self.lightning_cloud_delay
            else:
                self.lightning_sky_intensity = min(remaining / 120.0, 1.0)
        elif self.lightning_state == "cloud_wait":
            if now >= self.lightning_state_timer:
                self.lightning_clouds_intensity = 1.0
                self.lightning_state = "cloud_flash"
                self.lightning_state_timer = now + 120
        elif self.lightning_state == "cloud_flash":
            remaining = self.lightning_state_timer - now
            if remaining <= 0:
                self.lightning_clouds_intensity = 0.0
                self.lightning_remaining_flashes -= 1
                if self.lightning_remaining_flashes > 0:
                    self.lightning_state = "sky_flash"
                    self.lightning_sky_intensity = 1.0
                    self.lightning_state_timer = now + 120
                else:
                    self.lightning_state = "idle"
                    self.lightning_state_timer = now + random.randint(3000, 8000)
            else:
                self.lightning_clouds_intensity = min(remaining / 120.0, 1.0)

        # Apply flash to sky surface
        if self.lightning_sky_intensity > 0:
            self.bg_sky = self.bg_sky_original.copy()
            c = int(255 * self.lightning_sky_intensity)
            self.bg_sky.fill((c, c, c), None, pygame.BLEND_RGB_ADD)
        else:
            self.bg_sky = self.bg_sky_original

        # Apply flash to clouds surface
        if self.lightning_clouds_intensity > 0:
            self.bg_clouds = self.bg_clouds_original.copy()
            c = int(255 * self.lightning_clouds_intensity)
            self.bg_clouds.fill((c, c, c), None, pygame.BLEND_RGB_ADD)
        else:
            self.bg_clouds = self.bg_clouds_original

    # Ground detection
    def is_on_ground(self, px, py):
        if 0 <= px < WIDTH and 0 <= py < HEIGHT:
            return self.bg_ground.get_at((int(px), int(py))).a > 0
        # If off screen bottom, treat as ground (prevents falling forever)
        if py >= HEIGHT:
            return True
        return False

    # Ending / execution system (Now delegated to self.timeline)
    def update_endings(self, now):
        return self.timeline.update(now)

    def check_execution(self):
        p = self.player
        e = self.enemy
        if not (p.rage_mode and self.ending_triggered):
            return False

        if not self.can_kill:
            self.can_kill = True
            e.locked = True
            e.set_animation("idle", e.anims["idle"])
            return True

        if self.can_kill and not self.kill:
            self.kill = True
            e.dead = True
            e.set_animation("dead", e.anims["dead"])
            self.game_end = True
            self.game_result = "ENEMY EXECUTED"
            return True

        return False

    def handle_player_attack_hit(self):
        p = self.player
        e = self.enemy
        if p.action != "attack":
            return
        attack_rect = p.get_attack_rect()
        if self.debug_enabled:
            pygame.draw.rect(self.screen, (255, 0, 0), attack_rect, 2)
        if not attack_rect.colliderect(e.rect) or p.attack_has_hit:
            return
        p.attack_has_hit = True
        p.snd_melee.play()
        if e.dead or e.action == "hurt":
            return
        if not self.check_execution():
            e.hurt_from_damage()

    def handle_leap_attack_hit(self):
        p = self.player
        e = self.enemy
        if p.action != "shoot" or not p.rage_mode:
            return
        leap_rect = p.get_leap_rect()
        if not leap_rect.colliderect(e.rect) or p.attack_has_hit:
            return
        p.attack_has_hit = True
        p.snd_melee.play()
        if e.dead or e.action == "hurt":
            return
        if not self.check_execution():
            e.hurt_from_damage()

    def handle_events(self):
        keys = pygame.key.get_pressed()
        moving = False
        if self.player.can_walk():
            if keys[pygame.K_a] or keys[pygame.K_d]:
                moving = True

        mute_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 50)
        debug_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle Esc Key for Pausing
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.paused:
                        self.paused = True
                        self.pause_start_time = pygame.time.get_ticks()
                    else:
                        self.paused = False
                        self.total_paused_time += (pygame.time.get_ticks() - self.pause_start_time)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.paused:
                    if self.resume_btn.collidepoint(mouse_pos):
                        self.paused = False
                        self.total_paused_time += (pygame.time.get_ticks() - self.pause_start_time)
                    elif self.menu_btn.collidepoint(mouse_pos):
                        self.snd_ui.play()
                        self.return_to_menu = True
                    elif mute_btn.collidepoint(mouse_pos):
                        self.muted = not self.muted
                        self.snd_ui.play()
                        if self.muted:
                            pygame.mixer.music.set_volume(0.0)
                            self.snd_ui.set_volume(0.0)
                            self.player.mute()
                            self.partner.mute()
                        else:
                            pygame.mixer.music.set_volume(0.5)
                            self.snd_ui.set_volume(0.6)
                            self.player.unmute()
                            self.partner.unmute()
                    elif debug_btn.collidepoint(mouse_pos):
                        self.debug_enabled = not self.debug_enabled
                        self.snd_ui.play()
                else:
                    if self.pause_btn.collidepoint(mouse_pos):
                        self.paused = True
                        self.pause_start_time = pygame.time.get_ticks()
                    else:
                        if event.button == 1:
                            if self.debug_enabled and self.moon_btn_rect.collidepoint(event.pos):
                                self.moon_is_red = not self.moon_is_red
                                self.moon_red(self.moon_is_red, 1000)
                            else:
                                self.player.handle_shoot(self.bullets, moving)
                        if event.button == 3:
                            self.player.handle_attack()
        return True

    def update(self, now):
        # 1. Environmental and transition tick updates
        self._update_lightning(now)
        self._update_moon_transition(now)

        # 2. Handle first scene scripted flee sequence
        if self.enemy_fleeing:
            self.enemy.x += ESCAPE_SPEED
            
            # Safeguard: Ensures set_animation runs only once, preventing frozen frame indexes
            if self.enemy.action != "run":
                self.enemy.set_animation("run", self.enemy.anims["run"])
            self.enemy.facing_right = True

            # Initiate screen fade-out once the enemy is fully off-screen right
            if self.enemy.x > WIDTH + 150 and self.fade_state == "none":
                self.fade_state = "fading_out"
                self.fade_timer = now

        # 3. Handle black screen fade transitions
        if self.fade_state == "fading_out":
            elapsed = now - self.fade_timer
            self.fade_alpha = min(255, int((elapsed / 1000.0) * 255))
            if elapsed >= 1000:
                self.fade_state = "black"
                self.fade_timer = now
                self.interlude_pending = True

        elif self.fade_state == "fading_in":
            elapsed = now - self.fade_timer
            self.fade_alpha = max(0, 255 - int((elapsed / 1000.0) * 255))
            if elapsed >= 1000:
                self.fade_state = "none"
                self.fade_alpha = 0

        # 5. Physics, movement, and player input loop
        keys = pygame.key.get_pressed()
        self.player.handle_movement(keys)
        self.player.handle_jump(keys)
        self.player.update_leap(self.enemy.rect)
        self.player.update_gravity(self.is_on_ground)
        self.player.clamp_to_screen()
        self.player.update_regen(now)

        # Player death criteria
        if self.player.dead:
            if self.player.frame_index >= len(self.player.animation) - 1:
                self.game_end = True
                self.game_result = "YOU DIED"

        # Screen damage flash intensity
        if now - self.player.last_hit_time < 150 and self.player.hp > 0:
            self.damage_flash_alpha = 100
            self.shake_frames = 10
        else:
            self.damage_flash_alpha = max(0, self.damage_flash_alpha - 5)

        # Ambient rain calculation
        for drop in self.rain_drops:
            drop[0] += drop[2] // 4
            drop[1] += drop[2]
            if drop[1] > HEIGHT or drop[0] > WIDTH:
                drop[0] = random.randint(-200, WIDTH)
                drop[1] = random.randint(-200, 0)

        # 6. Combat Projectiles and Hitboxes
        if self.bullets.update_player_bullets(self.enemy.rect):
            if not self.enemy.dead:
                self.enemy.hurt_from_damage()

        self.handle_player_attack_hit()
        self.handle_leap_attack_hit()

        # 7. Enemy Behavior Loop
        self.enemy.update_gravity(self.is_on_ground, self.player.scale)
        self.enemy.update_auto_attack(now)
        self.civic_x, self.civic_y, self.target_partner, self.civic_hit = \
            self.enemy.update_march(
                now,
                self.partner.x, self.partner.y, self.partner.dead,
                self.civic_x, self.civic_y, self.target_partner, self.civic_hit,
                self.player.scale,
                self.player.x,
            )

        # Check for enemy victory condition
        if self.enemy.escape and self.enemy.x < -200:
            self.game_end = True
            self.game_result = "ENEMY ESCAPED"

        # Combat calculations
        self.enemy.damage_player(self.player, now)
        if self.target_partner:
            self.enemy.damage_partner(self.partner, now)

        self.enemy.update_regen(now)

        # 8. Partner Behavior Loop
        self.partner.try_shoot(now, self.bullets, self.enemy.x, self.enemy.y)
        if self.bullets.update_partner_bullets(self.enemy.rect):
            if not self.enemy.dead:
                self.enemy.hurt_from_damage()

        # Manage partner state transition delays upon defeat
        if self.partner.dead and not self.partner_death_handled:
            self.partner_death_handled = True
            self.partner_death_time = now

        if self.partner.dead and self.partner_death_handled \
                and now - self.partner_death_time >= PARTNER_DEATH_PAUSE \
                and self.target_partner:
            self.target_partner = False
            self.enemy.phase = 0

        # 9. Sprite Sheet and Animation ticks (exactly once per loop cycle)
        self.enemy.update_wounded_sprite(self.player.rage_mode)
        self.player.update_wounded_sprite()
        self.player.update_animation()
        self.enemy.update_animation()
        self.partner.update_animation()
    
    def run_interlude(self):
        interlude_lines = [
            "The beast escaped into the darkness...",
            "But John knows it will return.",
            "ONE MONTH LATER..."
        ]
        try:
            big_font = pygame.font.Font("resources/fonts/" + FONT_NAME + ".ttf", 50)
        except FileNotFoundError:
            big_font = pygame.font.SysFont(None, 50)
        try:
            btn_font = pygame.font.Font("resources/fonts/" + FONT_NAME + ".ttf", 35)
        except FileNotFoundError:
            btn_font = pygame.font.SysFont(None, 35)
        continue_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 120, 200, 50)

        for line in interlude_lines:
            waiting = True
            while waiting:
                self.clock.tick(FPS)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if continue_btn.collidepoint(event.pos):
                            waiting = False
                self.draw(pygame.time.get_ticks() - self.total_paused_time)
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(100)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))
                lines = line.split("\n")
                for i, l in enumerate(lines):
                    surf = big_font.render(l, True, (255, 255, 255))
                    rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50 + i * 60))
                    self.screen.blit(surf, rect)
                mouse_pos = pygame.mouse.get_pos()
                btn_color = (80, 80, 80) if not continue_btn.collidepoint(mouse_pos) else (130, 130, 130)
                pygame.draw.rect(self.screen, btn_color, continue_btn)
                pygame.draw.rect(self.screen, (255, 255, 255), continue_btn, 2)
                cont_surf = btn_font.render("CONTINUE", True, (255, 255, 255))
                self.screen.blit(cont_surf, cont_surf.get_rect(center=continue_btn.center))
                pygame.display.flip()

    def transition_to_next_scene(self):
        """Resets combat states and positions entities for Phase 2 without activating Rage Mode yet."""
        now = pygame.time.get_ticks() - self.total_paused_time

        # 1. Restore Player vitals without triggering Rage Mode prematurely
        self.player.hp = self.player.max_hp
        self.player.dead = False
        if self.player.action == "dead":
            self.player.set_animation("idle", self.player.anims["idle"])

        # 2. Reset and configure the enemy for the second fight
        self.enemy_fleeing = False
        self.enemy.locked = False
        self.enemy.escape = False
        self.enemy.hp = self.enemy.max_hp
        self.enemy.make_normal()

        # Re-position entities
        self.enemy.x = WIDTH - 200
        self.enemy.y = HEIGHT // 2 + ENEMY_CHAR_OFFSET_Y
        self.enemy.facing_right = False
        self.enemy.set_animation("idle", self.enemy.anims["idle"])

        self.player.x = WIDTH // 4 + PLAYER_CHAR_OFFSET_X
        self.player.facing_right = True

        self.level = 2
        # Reset moon to white for Scene 2
        self.moon_is_red = False
        self.moon_red(False)

        # Clean active projectiles
        self.bullets.player_bullets = []
        self.bullets.partner_bullets = []

        # 3. Position timeline clock right after the first phase transition
        # This permits 10 seconds of normal combat before Rage Mode naturally triggers at 84 seconds (RAGE_TRIGGER_TIME)
        self.start_time = now - ENEMY_PHASE_1_TIME

        # 4. Initiate fade-in
        self.fade_state = "fading_in"
        self.fade_timer = now

    def draw(self, now):
        # Layered backgrounds: sky → moon → clouds → rocks → ground
        self.screen.blit(self.bg_sky, (0, 0))
        self.screen.blit(self.bg_moon, (MOON_X, MOON_Y))
        self.screen.blit(self.bg_clouds, (0, 0))
        self.screen.blit(self.bg_rocks, (0, 0))
        self.screen.blit(self.bg_ground, (0, 0))

        self.enemy.draw(self.screen, self.player.scale)
        self.player.draw(self.screen)
        self.bullets.draw_player_bullets(self.screen)
        self.screen.blit(self.civic_img, (self.civic_x, self.civic_y))
        self.partner.draw(self.screen)
        self.bullets.draw_partner_bullets(self.screen)

        # 1. DRAW DAMAGE FLASH
        if self.damage_flash_alpha > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT))
            flash_surf.fill((255, 0, 0))
            flash_surf.set_alpha(self.damage_flash_alpha)
            self.screen.blit(flash_surf, (0, 0))

        #  2. DRAW HEALTH blur
        # As HP drops, the screen gets darker and more claustrophobic
        if self.player.hp > 0:
            hp_percent = self.player.hp / self.player.max_hp
            vignette_alpha = int(180 * (1.0 - hp_percent))  # Max darkness is 180
            if vignette_alpha > 0:
                vig_surf = pygame.Surface((WIDTH, HEIGHT))
                vig_surf.fill((0, 0, 0))
                vig_surf.set_alpha(vignette_alpha)
                self.screen.blit(vig_surf, (0, 0))

        # 3. DRAW RAIN
        for drop in self.rain_drops:
            pygame.draw.line(self.screen, (150, 150, 180), (drop[0], drop[1]), (drop[0] + drop[2] // 4, drop[1] + 30),
                             2)

        # 4 SCREEN SHAKE
        if self.shake_frames > 0:
            self.shake_frames -= 1
            # Copy the screen, black it out, and paste it back slightly offset!
            shake_offset_x = random.randint(-8, 8)
            shake_offset_y = random.randint(-8, 8)
            shake_copy = self.screen.copy()
            self.screen.fill((0, 0, 0))
            self.screen.blit(shake_copy, (shake_offset_x, shake_offset_y))

        # 5 Draw the black fade-to-black transition overlay
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((WIDTH, HEIGHT))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surf, (0, 0))


        if self.debug_enabled:
            self.draw_debug_grid()
            self.draw_debug_ui(now)
            self.draw_debug_rects()
        else:
            self.draw_ui(now)

        # Draw pause button on HUD during gameplay
        if not self.paused and not self.game_end:
            pygame.draw.rect(self.screen, (60, 60, 60), self.pause_btn)
            pygame.draw.rect(self.screen, (200, 200, 200), self.pause_btn, 2)
            pause_label = self.font.render("PAUSE", True, (255, 255, 255))
            self.screen.blit(pause_label, pause_label.get_rect(center=self.pause_btn.center))

        # Draw the pause menu
        if self.paused:
            self.draw_pause_menu()

        if self.debug_enabled:
            btn_color = (255, 100, 100) if self.moon_is_red else (200, 200, 200)
            pygame.draw.rect(self.screen, btn_color, self.moon_btn_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), self.moon_btn_rect, 2)
            self.screen.blit(self.debug_font.render("Test moon switch 1s", True, (0, 0, 0)),
                   (self.moon_btn_rect.x + 6, self.moon_btn_rect.y + 8))
        pygame.display.flip()

    def draw_ui(self, now):
        p = self.player
        s = self.screen
        f = self.font

        # PLAYER VITALS
        name_label = self.debug_info_font.render("JOHN HP", True, (200, 200, 200))
        s.blit(name_label, (20, 15))

        pygame.draw.rect(s, (50, 50, 50), (20, 35, 200, 20))
        if p.hp > 0:
            hp_ratio = p.hp / p.max_hp
            color = (50, 255, 50) if hp_ratio > 0.3 else (255, 50, 50)
            pygame.draw.rect(s, color, (20, 35, int(200 * hp_ratio), 20))
        pygame.draw.rect(s, (200, 200, 200), (20, 35, 200, 20), 2)

        if p.rage_mode:
            s.blit(f.render("RAGE MODE", True, (255, 40, 40)), (20, 90))
        else:
            # AMMOLabel
            s.blit(self.debug_info_font.render("AMMO:", True, (200, 200, 200)), (20, 90))
            for i in range(12):
                color = (255, 200, 50) if i < p.shots else (100, 100, 100)
                # Shifted the bullets slightly right to make room for the label
                pygame.draw.rect(s, color, (80 + (i * 15), 90, 10, 15))

            # Flashing RELOADINGAlert
            if p.shots == 0 and int(now / 250) % 2 == 0:
                s.blit(self.debug_info_font.render("RELOADING...", True, (255, 50, 50)), (270, 90))

        # SURVIVAL BOSS BAR
        elapsed = now - self.start_time
        if elapsed < ENDING_TIME:
            progress = elapsed / ENDING_TIME
            bar_w = 400
            bar_x = WIDTH // 2 - bar_w // 2

            title = self.debug_info_font.render("MOON INFLUENCE (SURVIVE!)", True, (200, 200, 200))
            s.blit(title, (WIDTH // 2 - title.get_width() // 2, 15))

            pygame.draw.rect(s, (30, 30, 30), (bar_x, 35, bar_w, 15))
            pygame.draw.rect(s, (150, 50, 100), (bar_x, 35, int(bar_w * progress), 15))
            pygame.draw.rect(s, (150, 150, 150), (bar_x, 35, bar_w, 15), 2)

        else:
            if int(now / 500) % 2 == 0:
                exec_text = f.render("EXECUTE THE BEAST!", True, (255, 50, 50))
                s.blit(exec_text, (WIDTH // 2 - exec_text.get_width() // 2, 20))

        #  PARTNER STATUS & GAME OVER
        if not self.partner.dead:
            s.blit(self.debug_info_font.render("PARTNER HP:", True, (200, 200, 200)), (20, HEIGHT - 40))
            for i in range(int(self.partner.hp)):
                pygame.draw.rect(s, (255, 50, 50), (120 + (i * 25), HEIGHT - 40, 15, 15))

        if self.game_end:
            text = f.render(self.game_result, True, (255, 50, 50))
            s.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

        # ENEMY HP
        enemy_hp_text = f"BEAST HP: {int(self.enemy.hp)}"
        enemy_hp_surf = self.debug_info_font.render(enemy_hp_text, True, (255, 100, 100))
        s.blit(enemy_hp_surf, (WIDTH - enemy_hp_surf.get_width() - 20, 15))

        # LEVEL indicator below enemy HP
        level_label = f.render(f"LEVEL {self.level}", True, (200, 200, 200))
        s.blit(level_label, (WIDTH // 2 - level_label.get_width() // 2, 50))



        if p.rage_mode:
            s.blit(f.render("RAGE MODE", True, (255, 40, 40)), (20, 220))

        if self.game_end:
            text = self.font.render(self.game_result, True, (255, 50, 50))
            s.blit(text, (WIDTH // 2, HEIGHT // 2))

    def draw_debug_ui(self, now):
        p = self.player
        e = self.enemy
        s = self.screen
        f = self.font

        s.blit(f.render(f"Shots: {p.shots}/{12}", True, (255, 255, 255)), (20, 20))
        s.blit(f.render(f"Action: {p.action}", True, (255, 255, 0)), (20, 60))
        s.blit(f.render(f"Enemy: {e.action}", True, (255, 100, 100)), (20, 100))
        s.blit(f.render(f"Player HP: {int(p.hp)}", True, (100, 255, 100)), (20, 140))
        s.blit(f.render(f"Enemy HP: {e.hp:.1f}", True, (255, 100, 100)), (20, 180))

        if now - self.start_time >= ENDING_TIME:
            s.blit(f.render(f"Can Kill: {bool(self.can_kill)}", True, (255, 100, 100)), (20, 240))

        s.blit(f.render(f"Time: {int(now)}", True, (255, 100, 100)), (20, 280))

        if p.rage_mode:
            s.blit(f.render("RAGE MODE", True, (255, 40, 40)), (20, 220))

        if self.game_end:
            s.blit(f.render(self.game_result, True, (255, 50, 50)), (WIDTH // 2, HEIGHT // 2))

    def draw_debug_grid(self):
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        color = (*GRID_COLOR, GRID_ALPHA)
        for x in range(0, WIDTH, GRID_SPACING):
            pygame.draw.line(surf, color, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SPACING):
            pygame.draw.line(surf, color, (0, y), (WIDTH, y))
        self.screen.blit(surf, (0, 0))
        for x in range(0, WIDTH, GRID_SPACING):
            self.screen.blit(self.debug_font.render(str(x), True, (255, 255, 255)), (x + 2, 2))
        for y in range(0, HEIGHT, GRID_SPACING):
            self.screen.blit(self.debug_font.render(str(y), True, (255, 255, 255)), (2, y + 2))

    def draw_debug_rects(self):
        p = self.player
        e = self.enemy
        s = self.screen
        scale = p.scale

        pf_rect = pygame.Rect(
            int(p.x - PLAYER_CHAR_OFFSET_X * scale),
            int(p.y - PLAYER_CHAR_OFFSET_Y * scale),
            int(FRAME_W * scale),
            int(FRAME_H * scale),
        )
        ef_rect = pygame.Rect(
            int(e.x - ENEMY_CHAR_OFFSET_X * scale),
            int(e.y - ENEMY_CHAR_OFFSET_Y * scale),
            int(FRAME_W * scale),
            int(FRAME_H * scale),
        )

        DBG_PF = (255, 255, 0)      # Player Frame: Yellow
        DBG_PC = (0, 255, 0)        # Player Char: Green
        DBG_EF = (255, 0, 255)      # Enemy Frame: Magenta
        DBG_EC = (255, 0, 0)        # Enemy Char: Red

        for rect, color, label in [
            (pf_rect, DBG_PF, "Player Frame"),
            (p.rect, DBG_PC, "Player Char"),
            (ef_rect, DBG_EF, "Enemy Frame"),
            (e.rect, DBG_EC, "Enemy Char"),
        ]:
            pygame.draw.rect(s, color, rect, 2)
            s.blit(self.debug_font.render(label, True, color), (rect.x + 2, rect.y + 2))
            for cx, cy in [
                (rect.x, rect.y),
                (rect.right - 1, rect.y),
                (rect.x, rect.bottom - 1),
                (rect.right - 1, rect.bottom - 1),
            ]:
                pygame.draw.circle(s, color, (cx, cy), 4)

        # Info panel at top-right
        info_y = 20
        for rect, color, label in [
            (pf_rect, DBG_PF, "Player Frame"),
            (p.rect, DBG_PC, "Player Char"),
            (ef_rect, DBG_EF, "Enemy Frame"),
            (e.rect, DBG_EC, "Enemy Char"),
        ]:
            s.blit(self.debug_info_font.render(
                f"{label}: ({rect.x},{rect.y}) {rect.w}x{rect.h}",
                True, color,
            ), (WIDTH - 450, info_y))
            info_y += 22

    def draw_pause_menu(self):
        # Draw dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Title
        title_surf = self.font.render("PAUSED", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 180))
        self.screen.blit(title_surf, title_rect)

        mouse_pos = pygame.mouse.get_pos()

        mute_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 50)
        debug_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 50)

        # Mute / Unmute Button
        mute_text = "UNMUTE" if self.muted else "MUTE"
        mute_color = (200, 200, 200) if not mute_btn.collidepoint(mouse_pos) else (255, 255, 255)
        mute_surf = self.font.render(mute_text, True, mute_color)
        self.screen.blit(mute_surf, mute_surf.get_rect(center=mute_btn.center))

        # Resume Button
        res_color = (255, 255, 255) if self.resume_btn.collidepoint(mouse_pos) else (200, 200, 200)
        res_surf = self.font.render("RESUME", True, res_color)
        self.screen.blit(res_surf, res_surf.get_rect(center=self.resume_btn.center))

        # Main Menu Button
        menu_color = (255, 50, 50) if self.menu_btn.collidepoint(mouse_pos) else (200, 50, 50)
        menu_surf = self.font.render("MAIN MENU", True, menu_color)
        self.screen.blit(menu_surf, menu_surf.get_rect(center=self.menu_btn.center))

        # Debug Toggle Button
        debug_text = f"DEBUG: {'ON' if self.debug_enabled else 'OFF'}"
        debug_color = (200, 200, 200) if not debug_btn.collidepoint(mouse_pos) else (255, 255, 255)
        debug_surf = self.font.render(debug_text, True, debug_color)
        self.screen.blit(debug_surf, debug_surf.get_rect(center=debug_btn.center))



    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            raw_now = pygame.time.get_ticks()

            self.handle_events()

            # Break the loop and return to main.py if player clicked MAIN MENU
            if self.return_to_menu:
                pygame.mixer.music.stop()
                return

                # Calculate frozen time
            frozen_now = raw_now - self.total_paused_time

            # Only update characters and endings if the game is NOT paused
            if not self.paused:
                if not self.update_endings(frozen_now):
                    break
                self.update(frozen_now)

            # Always draw the background game
            self.draw(frozen_now)

            # Interlude between Scene 1 and Scene 2
            if self.interlude_pending:
                self.run_interlude()
                self.interlude_pending = False
                now = pygame.time.get_ticks() - self.total_paused_time
                self.transition_to_next_scene()

            # ---  END SCREEN  ---
            if self.game_end:
                pygame.mixer.music.stop()  # Stop the intense Scene 2 music

                # Figure out if they won, lost, or died
                if "EXECUTED" in self.game_result:
                    result_type = "victory"
                elif "ESCAPED" in self.game_result:
                    result_type = "defeat"
                else:
                    result_type = "game_over"

                # Run the screen and return their choice (play_again or main_menu)
                choice = self.end_screen.run(result_type)
                return choice

            # If the timeline completely times out, fallback to menu
        pygame.mixer.music.stop()
        return "main_menu"


        # If the game naturally ends (death/escape) stop music and return to menu
        pygame.mixer.music.stop()
        return

        pygame.quit()
        sys.exit()
