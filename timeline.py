import pygame
from config import (
    ENEMY_TARGET_TIME, ENEMY_PHASE_1_TIME, RAGE_TRIGGER_TIME, ENDING_TIME, ESCAPE_TIME, ENDGAME_TIME
)

class TimelineEvent:
    def __init__(self, trigger_time, callback, run_once=True):
        self.trigger_time = trigger_time
        self.callback = callback
        self.run_once = run_once
        self.triggered = False

    def check_and_trigger(self, elapsed, game):
        if self.run_once and self.triggered:
            return False
        if elapsed >= self.trigger_time:
            self.callback(game)
            self.triggered = True
            return True
        return False


class TimelineManager:
    def __init__(self, game):
        self.game = game
        self.events = []
        self._setup_events()

    def _setup_events(self):
        def trigger_enemy_march(game):
            game.enemy.mode = "chase"
            game.enemy.phase = 0

        def trigger_enemy_phase_1(game):
            game.enemy.mode = "march"
            game.enemy.phase = 1
            game.target_partner = True
        
        def trigger_enemy_flee_transition(game):
            # Trigger the flee sequence
            game.enemy_fleeing = True
            game.enemy.locked = True  # Locks pathfinding AI to allow scripted flee logic
            game.enemy.facing_right = True
            game.enemy.set_animation("run", game.enemy.anims["run"])

        def trigger_rage_mode(game):
            if not game.player.rage_mode:
                game.player.activate_rage()
                game.enemy.hp = game.enemy.max_hp
                game.enemy.make_normal()
                game.player.hp = game.player.max_hp

        def trigger_ending(game):
            if not game.ending_triggered:
                game.ending_triggered = True
                game.enemy.locked = False

        def trigger_enemy_escape(game):
            if game.ending_triggered and not game.enemy.dead:
                game.enemy.escape = True
                game.enemy.locked = False
                game.enemy.set_animation("run", game.enemy.anims["run"])
                game.enemy.facing_right = False

        self.events.append(TimelineEvent(ENEMY_TARGET_TIME, trigger_enemy_march))
        self.events.append(TimelineEvent(ENEMY_PHASE_1_TIME, trigger_enemy_phase_1))
        self.events.append(TimelineEvent(ENEMY_PHASE_1_TIME, trigger_enemy_flee_transition))
        def trigger_moon_red_before_rage(game):
            if not game.moon_is_red:
                game.moon_is_red = True
                game.moon_red(True, 2000)

        self.events.append(TimelineEvent(RAGE_TRIGGER_TIME - 2000, trigger_moon_red_before_rage))
        self.events.append(TimelineEvent(RAGE_TRIGGER_TIME, trigger_rage_mode))
        self.events.append(TimelineEvent(ENDING_TIME, trigger_ending))
        self.events.append(TimelineEvent(ESCAPE_TIME, trigger_enemy_escape))

    def update(self, now):
        elapsed = now - self.game.start_time

        if elapsed >= ENDGAME_TIME:
            return False

        for event in self.events:
            event.check_and_trigger(elapsed, self.game)

        return True