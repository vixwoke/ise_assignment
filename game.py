from timeline import TimelineManager
import pygame
import sys
from config import (
    WIDTH, HEIGHT, FPS, FRAME_W, FRAME_H, RAGE_TRIGGER_TIME,
    ENDING_TIME, ESCAPE_TIME, ENDGAME_TIME, ENEMY_TARGET_TIME, MUSIC_PATH,
    MUSIC_VOLUME, FONT_NAME, FONT_SIZE, DEBUG,
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


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("maingame.py")
        try:
            pygame.mixer.music.load(MUSIC_PATH)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
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

        # Load assets
        player_anims = load_player_anims()
        rage_anims = load_rage_anims()
        enemy_normal, enemy_wounded = load_enemy_anims()
        partner_anims = load_partner_anims()
        self.civic_img = load_civic_img()

        # Entities
        self.player = Player(player_anims, rage_anims)
        self.enemy = Enemy(enemy_normal, enemy_wounded)
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

        # Debug moon toggle with smooth transition
        self.moon_is_red = False
        self.moon_current_t = 0.0
        self.moon_transition_start = 0
        self.moon_transition_duration = 0
        self.moon_start_t = 0.0
        self.moon_target_t = 0.0
        self.moon_btn_rect = pygame.Rect(WIDTH - 150, 20, 160, 30)

        # Ending
        self.ending_triggered = False
        self.can_kill = False
        self.kill = False
        self.game_end = False
        self.game_result = ""

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
        if DEBUG:
            pygame.draw.rect(self.screen, (255, 0, 0), attack_rect, 2)
        if not attack_rect.colliderect(e.rect) or p.attack_has_hit:
            return
        p.attack_has_hit = True
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if DEBUG and self.moon_btn_rect.collidepoint(event.pos):
                        self.moon_is_red = not self.moon_is_red
                        self.moon_red(self.moon_is_red, 1000)
                    else:
                        self.player.handle_shoot(self.bullets, moving)
                if event.button == 3:
                    self.player.handle_attack()
        return True

    def update(self, now):
        self._update_moon_transition(now)
        keys = pygame.key.get_pressed()
        self.player.handle_movement(keys)
        self.player.handle_jump(keys)
        self.player.update_leap(self.enemy.rect)
        self.player.update_gravity(self.is_on_ground)
        self.player.clamp_to_screen()
        self.player.update_recharge(now)
        self.player.update_regen(now)

        # Player bullets
        if self.bullets.update_player_bullets(self.enemy.rect):
            if not self.enemy.dead:
                self.enemy.hurt_from_damage()

        # Attack / leap damage
        self.handle_player_attack_hit()
        self.handle_leap_attack_hit()

        # Enemy AI
        self.enemy.update_gravity(self.is_on_ground, self.player.scale)
        self.enemy.update_auto_attack(now)
        self.civic_x, self.civic_y, self.target_partner, self.civic_hit = \
            self.enemy.update_march(
                now, self.partner.x, self.partner.y, self.partner.dead,
                self.civic_x, self.civic_y, self.target_partner, self.civic_hit,
                self.player.scale,
            )

        # Enemy escape end
        if self.enemy.escape and self.enemy.x < -200:
            self.game_end = True
            self.game_result = "ENEMY ESCAPED"

        # Enemy damage
        self.enemy.damage_player(self.player, now)
        if self.target_partner:
            self.enemy.damage_partner(self.partner, now)

        self.enemy.update_regen(now)

        # Partner
        self.partner.try_shoot(now, self.bullets, self.enemy.x, self.enemy.y)
        if self.bullets.update_partner_bullets(self.enemy.rect):
            if not self.enemy.dead:
                self.enemy.hurt_from_damage()

        # Animations
        self.player.update_animation()
        self.enemy.update_animation()
        self.partner.update_animation()

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

        if DEBUG:
            self.draw_debug_grid()
            self.draw_debug_ui(now)
            self.draw_debug_rects()
        else:
            self.draw_ui(now)

        pygame.display.flip()

    def draw_ui(self, now):
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

        # Debug moon toggle button (top-right)
        btn_color = (255, 100, 100) if self.moon_is_red else (200, 200, 200)
        pygame.draw.rect(s, btn_color, self.moon_btn_rect)
        pygame.draw.rect(s, (255, 255, 255), self.moon_btn_rect, 2)
        s.blit(self.debug_font.render("Test moon switch 1s", True, (0, 0, 0)),
               (self.moon_btn_rect.x + 6, self.moon_btn_rect.y + 8))

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

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            now = pygame.time.get_ticks()

            if not self.update_endings(now):
                break

            if not self.handle_events():
                break

            self.update(now)
            self.draw(now)

        pygame.quit()
        sys.exit()