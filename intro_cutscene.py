import pygame
import sys
from config import WIDTH, HEIGHT
from dialogue import NarrativeEngine


class IntroCutscene:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

        # Load narrative
        self.narrative = NarrativeEngine(self.screen, self.font)

        # Trigger first scene
        self.narrative.trigger_beat("prologue")

    def run(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Listen for SPACE/Clicks
                self.narrative.handle_events(event)

            # Draw black background
            self.screen.fill((5, 5, 8))

            # Draw text box
            self.narrative.draw()

            # Transition Logic
            if not self.narrative.is_active:
                # Move to next level
                return "start_game"

            pygame.display.flip()
            clock.tick(60)