import pygame
from config import FRAME_W, FRAME_H, PLAYER_PATH, RAGE_PATH, ENEMY_PATH, WOUNDED_ENEMY_PATH, PARTNER_PATH


def load_sheet(path, frame_width=FRAME_W, frame_height=FRAME_H):
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    sheet_width = sheet.get_width()
    for x in range(0, sheet_width, frame_width):
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (x, 0, frame_width, frame_height))
        frames.append(frame)
    return frames


# Player animations
def load_player_anims():
    p = PLAYER_PATH
    return {
        "idle": load_sheet(p + "Idle.png"),
        "walk": load_sheet(p + "Walk.png"),
        "jump": load_sheet(p + "Jump.png"),
        "attack": load_sheet(p + "Attack.png"),
        "hurt": load_sheet(p + "Hurt.png"),
        "dead": load_sheet(p + "Dead.png"),
        "recharge": load_sheet(p + "Recharge.png"),
        "shoot": load_sheet(p + "Shot_1.png"),
    }


# Rage player animations
def load_rage_anims():
    p = RAGE_PATH
    attacks = [
        load_sheet(p + "Attack_1.png"),
        load_sheet(p + "Attack_2.png"),
        load_sheet(p + "Attack_3.png"),
    ]
    return {
        "idle": load_sheet(p + "Idle.png"),
        "walk": load_sheet(p + "Walk.png"),
        "jump": load_sheet(p + "Jump.png"),
        "attack": attacks[0],
        "attack2": attacks[1],
        "attack3": attacks[2],
        "attack_list": attacks,
        "hurt": load_sheet(p + "Hurt.png"),
        "dead": load_sheet(p + "Dead.png"),
        "shoot": load_sheet(p + "Leap_Attack.png"),
    }


# Enemy animations (normal + wounded variants)
def load_enemy_anims():
    n = ENEMY_PATH
    w = WOUNDED_ENEMY_PATH
    normal = {
        "attack": load_sheet(n + "Attack_1.png"),
        "hurt": load_sheet(n + "Hurt.png"),
        "idle": load_sheet(n + "Idle.png"),
        "dead": load_sheet(w + "Dead.png"),
        "walk": load_sheet(n + "Walk.png"),
        "run": load_sheet(n + "Run.png"),
    }
    wounded = {
        "attack": load_sheet(w + "Attack_1.png"),
        "hurt": load_sheet(w + "Hurt.png"),
        "idle": load_sheet(w + "Idle.png"),
        "dead": load_sheet(w + "Dead.png"),
        "walk": load_sheet(w + "Walk.png"),
        "run": load_sheet(w + "Run.png"),
    }
    return normal, wounded


# Partner animations
def load_partner_anims():
    p = PARTNER_PATH
    return {
        "idle": load_sheet(p + "Idle.png"),
        "hurt": load_sheet(p + "Hurt.png"),
        "shoot": load_sheet(p + "Shot.png"),
        "dead": load_sheet(p + "Dead.png"),
    }


# Civic image
def load_civic_img():
    img = pygame.image.load(PARTNER_PATH + "civic.png").convert_alpha()
    return pygame.transform.scale(img, (90, 90))
