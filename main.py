import pygame
import sys
from game import Game
from menu import MainMenu
from config import WIDTH, HEIGHT, FONT_NAME
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
            intro = IntroCutscene(screen, pygame.font.Font(f"resources/fonts/{FONT_NAME}.ttf", 18))
            next_scene = intro.run()

            # TRAPS the game in a loop so Play Again bypasses the menu
            while next_scene in ["start_game", "play_again"]:
                game = Game()
                next_scene = game.run()