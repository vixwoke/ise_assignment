import pygame
import sys
from config import WIDTH, HEIGHT


class EndScreen:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

        # Create a dark, semi-transparent overlay
        self.bg_overlay = pygame.Surface((WIDTH, HEIGHT))
        self.bg_overlay.set_alpha(210)
        self.bg_overlay.fill((10, 10, 15))

        # Setup Button Dimensions
        button_width = 300
        button_height = 60
        center_x = WIDTH // 2 - button_width // 2

        # Create Button Hitboxes
        self.btn_play_again = pygame.Rect(center_x, HEIGHT // 2 + 50, button_width, button_height)
        self.btn_main_menu = pygame.Rect(center_x, HEIGHT // 2 + 130, button_width, button_height)

        # Load UI Audio
        try:
            self.snd_click = pygame.mixer.Sound("resources/audio/ui_click.wav")
            self.snd_click.set_volume(0.6)
        except FileNotFoundError:
            self.snd_click = None

    def draw_text_center(self, text, font, color, y):

        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(WIDTH // 2, y))
        self.screen.blit(surface, rect)

    def draw_button(self, rect, text, mouse_pos):
         
        color = (150, 50, 50) if rect.collidepoint(mouse_pos) else (50, 50, 50)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)  # Silver border
        self.draw_text_center(text, self.font, (255, 255, 255), rect.centery)

    def run(self, result):

        clock = pygame.time.Clock()

        while True:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.btn_play_again.collidepoint(mouse_pos):
                        if self.snd_click: self.snd_click.play()
                        return "play_again"
                    if self.btn_main_menu.collidepoint(mouse_pos):
                        if self.snd_click: self.snd_click.play()
                        return "main_menu"

            # 1. Draw the dark overlay on top of the frozen game
            self.screen.blit(self.bg_overlay, (0, 0))

            # 2. Draw the Dynamic Titles
            if result == "victory":
                self.draw_text_center("ENEMY EXECUTED", self.font, (50, 255, 50), HEIGHT // 2 - 120)
                self.draw_text_center("The forest is safe... for now.", self.font, (200, 200, 200), HEIGHT // 2 - 40)
            elif result == "defeat":
                self.draw_text_center("ENEMY ESCAPED", self.font, (255, 50, 50), HEIGHT // 2 - 120)
                self.draw_text_center("John was too late.", self.font, (200, 200, 200), HEIGHT // 2 - 40)

            # 3. Draw the Buttons
            self.draw_button(self.btn_play_again, "PLAY AGAIN", mouse_pos)
            self.draw_button(self.btn_main_menu, "MAIN MENU", mouse_pos)

            pygame.display.flip()
            clock.tick(60)