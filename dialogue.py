import pygame
from config import WIDTH, HEIGHT


class NarrativeEngine:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

        # The Scene 1 Script
        # The Scene 1 Script (Safe and isolated!)
        self.script = {
            "intro": [
                "John: The radio signal died somewhere around here.",
                "John: It's too quiet. Even the crickets are dead.",
                "John: The air feels heavy... metallic. Like copper.",
                "John: I shouldn't have let her come out to these woods alone.",
                "John: I need to find the Civic. Hopefully, she's still waiting inside.",
                "John: Keep it together, John. Just find the car and get out."
            ],
            "find_car": [
                "John: The Civic... the doors are completely shredded.",
                "John: These claw marks ripped right through the steel. A bear couldn't do this.",
                "John: There's a blood trail leading deeper into the woods. I have to hurry."
            ],
            "blackout": [
                "John: The moon... why is it glowing pink?",
                "John: Ugh, my head... my blood feels like it's boiling!",
                "John: Something is under my skin... ARGHHH!"
            ],
            "panic": [
                "John: It's happening again... I can't stop it.",
                "John: The darkness... it's taking over everything!"
            ]
        }

        self.active_beat = None
        self.line_index = 0
        self.is_active = False

    def trigger_beat(self, beat_id):

        if beat_id in self.script and not self.is_active:
            self.active_beat = beat_id
            self.line_index = 0
            self.is_active = True

    def next_line(self):

        if not self.is_active:
            return

        self.line_index += 1

        # Check if the conversation is over
        if self.line_index >= len(self.script[self.active_beat]):
            self.is_active = False
            self.active_beat = None

    def handle_events(self, event):

        if not self.is_active:
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.next_line()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.next_line()

    def draw(self):
        if not self.is_active:
            return


        smaller_font = pygame.font.Font(None, 28)


        current_text = self.script[self.active_beat][self.line_index]


        shadow_surf = smaller_font.render(current_text, True, (255, 255, 255))
        text_surf = smaller_font.render(current_text, True, (139, 0, 0))


        text_rect = text_surf.get_rect(center=(WIDTH // 2, 50))
        shadow_rect = shadow_surf.get_rect(center=(WIDTH // 2 + 2, 52))  # Slight offset


        self.screen.blit(shadow_surf, shadow_rect)
        self.screen.blit(text_surf, text_rect)


        prompt_surf = smaller_font.render("Press SPACE to continue", True, (200, 200, 200))
        self.screen.blit(prompt_surf, (WIDTH - 250, HEIGHT - 30))