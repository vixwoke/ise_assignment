import pygame
import sys
from game import Game
from menu import MainMenu
from config import WIDTH, HEIGHT
from intro_cutscene import IntroCutscene
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("WAKING DEMON")

    while True:
        # 1. Boot the Main Menu
        menu = MainMenu(screen)
        action = menu.run()

        # 2. If   hit Start run the Game
        if action == "PLAY":
            # Load and play the Intro Cutscene first
            intro = IntroCutscene(screen, pygame.font.Font(None, 36))
            next_scene = intro.run()

            # When the cutscene finishes, start the actual game
            if next_scene == "start_game":
                game = Game()
                game.run() # When the player dies or quits loop  back to the menu