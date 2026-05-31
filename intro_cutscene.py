import pygame
import sys
from dialogue import NarrativeEngine
from config import WIDTH, HEIGHT


class IntroCutscene:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.engine = NarrativeEngine(screen, font)

        # UI Font for the "Press Enter" prompt
        self.prompt_font = pygame.font.Font(None, 24)

        self.scenes = [
            {"image": "intro_storyboard.jpg", "beat": "intro"},
            {"image": "find_car.jpg", "beat": "find_car"},
            {"image": "blackout.jpg", "beat": "blackout"},
            {"image": "panic.jpg", "beat": "panic"}
        ]
        self.current_beat_index = 0

        # Load images
        self.images = {}
        for s in self.scenes:
            path = f"resources/image/background/{s['image']}"
            try:
                img = pygame.image.load(path).convert()
                self.images[s['image']] = pygame.transform.scale(img, (WIDTH, HEIGHT))
            except:
                self.images[s['image']] = pygame.Surface((WIDTH, HEIGHT))
                self.images[s['image']].fill((10, 10, 15))

        # Setup Music
        try:
            pygame.mixer.music.load("resources/audio/musics/intro_theme.wav")
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except:
            print("Warning: Intro music file not found.")

        self.engine.trigger_beat(self.scenes[0]["beat"])

    def run(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit();
                    sys.exit()

                # -INPUT CONTROLS -
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        return "main_menu"

                    # Advance dialogue with ENTER or SPACE
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.engine.next_line()


                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.engine.next_line()

            # Logic to swap scenes
            if not self.engine.is_active:
                self.current_beat_index += 1
                if self.current_beat_index >= len(self.scenes):
                    pygame.mixer.music.stop()
                    return "start_game"
                else:
                    self.engine.trigger_beat(self.scenes[self.current_beat_index]["beat"])

            # DRAWING
            current_image = self.images[self.scenes[self.current_beat_index]["image"]]
            self.screen.blit(current_image, (0, 0))

            # Draw dialogue
            self.engine.draw()

            # - TEXT ---
            prompt_surf = self.prompt_font.render("Press ENTER/SPACE to continue", True, (200, 200, 200))
            self.screen.blit(prompt_surf, (WIDTH - 260, HEIGHT - 40))

            pygame.display.flip()
            clock.tick(60)