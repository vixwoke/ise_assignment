import pygame
import sys
from config import WIDTH, HEIGHT
from dialogue import NarrativeEngine


class IntroCutscene:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

        # Load your narrative engine
        self.narrative = NarrativeEngine(self.screen, self.font)

        # Automatically trigger the first story beat
        self.narrative.trigger_beat("prologue")

    def run(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Let your narrative engine listen for SPACE/Clicks
                self.narrative.handle_events(event)

            # 1. Draw a cinematic, pitch-black background
            self.screen.fill((5, 5, 8))

            # 2. Draw your text box
            self.narrative.draw()

            # 3. The Transition Logic
            # If the text box closes, the cutscene is over!
            if not self.narrative.is_active:
                # Tell main.py to move to the next level
                return "start_game"

            pygame.display.flip()
            clock.tick(60)