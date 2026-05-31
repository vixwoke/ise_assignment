import pygame
import sys
from config import WIDTH, HEIGHT, BG_MENU_PATH, FONT_NAME


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.bg_color = (30, 30, 30)
        self.state = "MAIN"  # States: MAIN, STORY, CONTROLS

        try:
            self.bg_image = pygame.image.load(BG_MENU_PATH).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))
        except FileNotFoundError:
            self.bg_image = None

        try:
            self.title_font = pygame.font.Font(f"resources/fonts/{FONT_NAME}.ttf", 100)
            self.button_font = pygame.font.Font(f"resources/fonts/{FONT_NAME}.ttf", 45)
            self.text_font = pygame.font.Font(f"resources/fonts/{FONT_NAME}.ttf", 25)
        except FileNotFoundError:
            self.title_font = pygame.font.SysFont(None, 100)
            self.button_font = pygame.font.SysFont(None, 45)
            self.text_font = pygame.font.SysFont(None, 25)

        # Main Menu Buttons
        self.start_btn = pygame.Rect(WIDTH // 2 - 150, 280, 300, 50)
        self.story_btn = pygame.Rect(WIDTH // 2 - 150, 350, 300, 50)
        self.controls_btn = pygame.Rect(WIDTH // 2 - 150, 420, 300, 50)
        self.quit_btn = pygame.Rect(WIDTH // 2 - 150, 490, 300, 50)

        # Sub-Menu Back Button
        self.back_btn = pygame.Rect(WIDTH // 2 - 150, 600, 300, 50)
        # UI Audio
        self.snd_click = pygame.mixer.Sound("resources/audio/ui_click.wav")
        self.snd_click.set_volume(0.6)
        # Menu Background Music
        try:
            pygame.mixer.music.load("resources/audio/musics/menu_theme.wav")
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except FileNotFoundError:
            pass

    def draw_text_center(self, text, font, color, y_pos):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, y_pos))
        self.screen.blit(text_surface, text_rect)

    def draw_button(self, rect, text, mouse_pos, clicked):

        if rect.collidepoint(mouse_pos):
            self.draw_text_center(f"> {text} <", self.button_font, (255, 255, 255), rect.centery)
            if clicked:
                self.snd_click.play()
                return True
        else:
            self.draw_text_center(text, self.button_font, (200, 200, 200), rect.centery)
        return False

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:

            # Draw Background & Overlay
            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(150)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))
            else:
                self.screen.fill(self.bg_color)

            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_clicked = True

            self.draw_text_center("WAKING DEMON", self.title_font, (255, 50, 50), 150)

            # ---------------------------------------------------------
            # STATE: MAIN MENU
            # ---------------------------------------------------------
            if self.state == "MAIN":
                if self.draw_button(self.start_btn, "START GAME", mouse_pos, mouse_clicked):
                    return "PLAY"
                if self.draw_button(self.story_btn, "STORY", mouse_pos, mouse_clicked):
                    self.state = "STORY"
                if self.draw_button(self.controls_btn, "CONTROLS", mouse_pos, mouse_clicked):
                    self.state = "CONTROLS"
                if self.draw_button(self.quit_btn, "QUIT", mouse_pos, mouse_clicked):
                    pygame.quit()
                    sys.exit()

            # ---------------------------------------------------------
            # STATE: STORY
            # ---------------------------------------------------------
            elif self.state == "STORY":
                story_text = [
                    "During a routine investigation of a strange pink moon phenomenon,",
                    "John blacks out. He awakens in a nightmare where his own body",
                    "betrays him. With his partner fighting by his side, John must",
                    "survive the horde while fighting the beast within himself.",
                    "Will you resist the rage, or let it consume you?"
                ]
                y_offset = 300
                for line in story_text:
                    self.draw_text_center(line, self.text_font, (200, 200, 255), y_offset)
                    y_offset += 40

                if self.draw_button(self.back_btn, "BACK", mouse_pos, mouse_clicked):
                    self.state = "MAIN"

            # ---------------------------------------------------------
            # STATE: CONTROLS
            # ---------------------------------------------------------
            elif self.state == "CONTROLS":
                controls_text = [
                    "W A S D - Move Character",
                    "SPACE - Evade / Leap",
                    "LEFT CLICK (Auto) - Shoot / Attack",
                    "RAGE MODE: Triggered automatically upon death."
                ]
                y_offset = 300
                for line in controls_text:
                    self.draw_text_center(line, self.text_font, (255, 200, 200), y_offset)
                    y_offset += 40

                if self.draw_button(self.back_btn, "BACK", mouse_pos, mouse_clicked):
                    self.state = "MAIN"



            pygame.display.flip()
            clock.tick(60)