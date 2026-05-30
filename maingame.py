import pygame
import sys
import numpy as np
import cv2
import pyaudio
import wave
from pyscreenrecorder import ScreenRecorder
import math
import random
pygame.init()
pygame.mixer.init()

# -----------------------------
# LOAD SOUND EFFECTS
# -----------------------------
snd_gun = pygame.mixer.Sound("audio/gun.wav")
snd_shotgun = pygame.mixer.Sound("audio/shotgun.wav")
snd_reload = pygame.mixer.Sound("audio/reload.wav")
snd_howl = pygame.mixer.Sound("audio/howl.wav")
snd_melee = pygame.mixer.Sound("audio/melee_hit.wav")

# Optional: lower the volume of the gunshots so they don't blow out your speakers
snd_gun.set_volume(0.4)
snd_howl.set_volume(0.8)


# -----------------------------
# SCREEN
# -----------------------------
WIDTH = 1200
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top Down Character")
pygame.mixer.music.load("waking demon.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
clock = pygame.time.Clock()

# -----------------------------
# LOAD BACKGROUND
# -----------------------------
bgGrassGround = pygame.image.load("background/grass-ground-1.png")

# -----------------------------
# LOAD SPRITESHEET
# -----------------------------

def load_sheet(path, frame_width, frame_height):
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    sheet_width = sheet.get_width()
    for x in range(0, sheet_width, frame_width):
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (x, 0, frame_width, frame_height))
        frames.append(frame)
    return frames

# -----------------------------
# FRAME SIZE
# -----------------------------
FRAME_W = 128
FRAME_H = 128

# -----------------------------
# SCALE
# -----------------------------
scale_multiplier = 1.0

# -----------------------------
# LOAD PLAYER ANIMATIONS
# -----------------------------
path = "maincharacter/"
idle_frames = load_sheet(path + "Idle.png", FRAME_W, FRAME_H)
walk_frames = load_sheet(path + "Walk.png", FRAME_W, FRAME_H)
jump_frames = load_sheet(path + "Jump.png", FRAME_W, FRAME_H)
attack_frames = load_sheet(path + "Attack.png", FRAME_W, FRAME_H)
hurt_frames = load_sheet(path + "Hurt.png", FRAME_W, FRAME_H)
dead_frames = load_sheet(path + "Dead.png", FRAME_W, FRAME_H)
recharge_frames = load_sheet(path + "Recharge.png", FRAME_W, FRAME_H)
shot_frames = load_sheet(path + "Shot_1.png", FRAME_W, FRAME_H)

# -----------------------------
# LOAD RAGE PLAYER ANIMATIONS
# -----------------------------
rageMainCharacterPath = "rageCharacter/"
rage_idle_frames = load_sheet(rageMainCharacterPath + "Idle.png", FRAME_W, FRAME_H)
rage_walk_frames = load_sheet(rageMainCharacterPath + "Walk.png", FRAME_W, FRAME_H)
rage_jump_frames = load_sheet(rageMainCharacterPath + "Jump.png", FRAME_W, FRAME_H)
rage_attack_frames = load_sheet(rageMainCharacterPath + "Attack_1.png", FRAME_W, FRAME_H)
rage_attack2_frames = load_sheet(rageMainCharacterPath + "Attack_2.png", FRAME_W, FRAME_H)
rage_attack3_frames = load_sheet(rageMainCharacterPath + "Attack_3.png", FRAME_W, FRAME_H)
rage_hurt_frames = load_sheet(rageMainCharacterPath + "Hurt.png", FRAME_W, FRAME_H)
rage_dead_frames = load_sheet(rageMainCharacterPath + "Dead.png", FRAME_W, FRAME_H)
rage_shot_frames = load_sheet(rageMainCharacterPath + "Leap_Attack.png", FRAME_W, FRAME_H)
rage_attack_list = [
    rage_attack_frames,
    rage_attack2_frames,
    rage_attack3_frames
]

# -----------------------------
# LOAD NORMAL ENEMY ANIMATIONS
# -----------------------------
enemyPath = "enemy/"
woundedEnemyPath = "woundedEnemy/"
enemyAttack_frames = load_sheet(enemyPath + "Attack_1.png", FRAME_W, FRAME_H)
enemyHurt_frames = load_sheet(enemyPath + "Hurt.png", FRAME_W, FRAME_H)
enemyIdle_frames = load_sheet(enemyPath + "Idle.png", FRAME_W, FRAME_H)
enemyDead_frames = load_sheet(woundedEnemyPath + "Dead.png", FRAME_W, FRAME_H)
enemyWalk_frames = load_sheet(enemyPath + "Walk.png", FRAME_W, FRAME_H)
enemyRun_frames = load_sheet(enemyPath + "Run.png", FRAME_W, FRAME_H)
# SAVE NORMAL ENEMY ANIMATIONS
normalAttack_frames = enemyAttack_frames
normalHurt_frames = enemyHurt_frames
normalIdle_frames = enemyIdle_frames
normalWalk_frames=enemyWalk_frames
normalRun_frames=enemyRun_frames

# -----------------------------
# LOAD WOUNDED ENEMY ANIMATIONS
# -----------------------------
woundedAttack_frames = load_sheet(woundedEnemyPath + "Attack_1.png", FRAME_W, FRAME_H)
woundedHurt_frames = load_sheet(woundedEnemyPath + "Hurt.png", FRAME_W, FRAME_H)
woundedIdle_frames = load_sheet(woundedEnemyPath + "Idle.png", FRAME_W, FRAME_H)
woundedWalk_frames = load_sheet(woundedEnemyPath + "Walk.png", FRAME_W, FRAME_H)
woundedRun_frames = load_sheet(woundedEnemyPath + "Run.png", FRAME_W, FRAME_H)

# -----------------------------
# PLAYER
# -----------------------------
x = WIDTH // 4
y = HEIGHT // 2
speed = 5
facing_right = True

# -----------------------------
# PLAYER HP
# -----------------------------
player_hp = 100.0
max_player_hp = 100.0

# -----------------------------
# ENEMY HP
# -----------------------------
enemy_hp = 100
max_enemy_hp = 100
enemy_dead = False
enemy_wounded = False
enemy_facing_right = True

# -----------------------------
# REGEN SYSTEM
# -----------------------------
player_regen_timer = pygame.time.get_ticks()
enemy_regen_timer = pygame.time.get_ticks()
player_regen_interval = 3000
enemy_regen_interval = 5000
player_regen_amount = 10
enemy_regen_amount = 1

# -----------------------------
# RAGE MODE
# -----------------------------
rage_mode = False
rage_start_time = pygame.time.get_ticks()
rage_trigger_time = 89000 #1.29minute

# -----------------------------
# SHOOT SYSTEM
# -----------------------------
fullMag = 12
shots = fullMag
recharging = False
recharge_start = 0
recharge_time = 1300

# -----------------------------
# BULLETS
# -----------------------------
bullets = []
bullet_speed = 12

# -----------------------------
# STATES
# -----------------------------
dead = False

# -----------------------------
# EVADE SYSTEM
# -----------------------------
evading = False
evade_dx = 0
evade_dy = 0

# -----------------------------
# LEAP ATTACK SYSTEM
# -----------------------------
leaping = False
leap_dx = 0
leap_dy = 0

# -----------------------------
# PLAYER ANIMATION
# -----------------------------
current_animation = idle_frames
current_action = "idle"
frame_index = 0.0
normal_animation_speed = 0.15
jump_animation_speed = 0.25

# -----------------------------
# ENEMY
# -----------------------------
enemy_x = WIDTH // 2
enemy_y = HEIGHT // 2
enemy_animation = enemyIdle_frames
enemy_action = "idle"
enemy_frame_index = 0.0
enemy_attack_timer = pygame.time.get_ticks()
enemy_attack_interval = 3000
enemy_animation_speed = 0.15
enemy_partner_damage = 1

# -----------------------------
# ENEMY MARCH SYSTEM
# -----------------------------
enemy_march = False
enemy_speed = 2
enemy_target_time = 74000  # 1.15minute
enemy_start_time = pygame.time.get_ticks()
civic_hit = False

# -----------------------------
# DAMAGE SYSTEM
# -----------------------------
last_player_hit = 0
player_hit_cooldown = 1000
enemy_attack_damage = 30
target_partner = False

# -----------------------------
# Ending SYSTEM
# -----------------------------
can_kill=False
kill=False
attack_has_hit = False
enemy_locked = False
ending_time=118000 #2.18minute
escape_time=148000 #2.29minute
endgame_time=160300 #2.40minute
ending_triggered = False
enemy_escape = False
game_end = False
game_result = ""

# -----------------------------
# LOAD PARTNER ANIMATIONS
# -----------------------------
partnerPath = "partner/"
partner_idle_frames = load_sheet(partnerPath + "Idle.png", FRAME_W, FRAME_H)
partner_hurt_frames = load_sheet(partnerPath + "Hurt.png", FRAME_W, FRAME_H)
partner_shot_frames = load_sheet(partnerPath + "Shot.png", FRAME_W, FRAME_H)
partner_dead_frames = load_sheet(partnerPath + "Dead.png", FRAME_W, FRAME_H)

# -----------------------------
# PARTNER
# -----------------------------
partner_hp = 3
partner_dead = False
enemy_has_hit_partner = False
partner_x = 30
partner_y = HEIGHT - 180
partner_animation = partner_idle_frames
partner_action = "idle"
partner_frame_index = 0.0
partner_animation_speed = 0.15
partner_last_shot = pygame.time.get_ticks()
partner_shot_interval = 3000
partner_bullets = []
partner_bullet_speed = 10
# CIVIC POSITION
civic_x = partner_x + 60
civic_y = partner_y + 55

# -----------------------------
# PRINT FORMATTER
# -----------------------------
def draw_text(surface, text, color, dest, font_name=None, font_size=35):
    if font_name:
        font = pygame.font.Font("fonts/" + font_name + ".ttf", font_size)
    else:
        font = pygame.font.SysFont(None, font_size)
    surface.blit(font.render(text, True, color), dest)


# =========================================================
# PARTNER ANIMATION FUNCTION
# =========================================================

def change_partner_animation(action, frames):
    global partner_action
    global partner_animation
    global partner_frame_index
    if partner_action != action:
        partner_action = action
        partner_animation = frames
        partner_frame_index = 0.0

# -----------------------------
# CHANGE PLAYER ANIMATION
# -----------------------------

def change_animation(new_action, new_frames):
    global current_action
    global current_animation
    global frame_index
    if current_action != new_action:
        current_action = new_action
        current_animation = new_frames
        frame_index = 0.0
civic_img = pygame.image.load("partner/civic.png").convert_alpha()
civic_img = pygame.transform.scale(civic_img, (90, 90))

# -----------------------------
# ACTIVATE RAGE MODE
# -----------------------------

def activate_rage_mode():
    global rage_mode
    global idle_frames
    global walk_frames
    global jump_frames
    global attack_frames
    global hurt_frames
    global dead_frames
    global shot_frames
    global player_regen_amount
    global scale_multiplier
    snd_howl.play()
    rage_mode = True
    idle_frames = rage_idle_frames
    walk_frames = rage_walk_frames
    jump_frames = rage_jump_frames
    attack_frames = rage_attack_frames
    hurt_frames = rage_hurt_frames
    dead_frames = rage_dead_frames
    shot_frames = rage_shot_frames
    player_regen_amount = 30
    scale_multiplier = 1.2
    change_animation("attack", attack_frames)

# -----------------------------
# CHANGE ENEMY TO WOUNDED
# -----------------------------

def make_enemy_wounded():
    global enemy_wounded
    global enemyIdle_frames
    global enemyAttack_frames
    global enemyHurt_frames
    global enemy_animation
    global enemy_frame_index
    global enemyWalk_frames
    global enemyRun_frames
    if not enemy_wounded:
        enemy_wounded = True
        enemyIdle_frames = woundedIdle_frames
        enemyAttack_frames = woundedAttack_frames
        enemyHurt_frames = woundedHurt_frames
        enemyWalk_frames =woundedWalk_frames
        enemyRun_frames=woundedRun_frames
        enemy_animation = enemyHurt_frames
        enemy_frame_index = 0.0

# -----------------------------
# CHANGE ENEMY TO NORMAL
# -----------------------------

def make_enemy_normal():
    global enemy_wounded
    global enemyIdle_frames
    global enemyAttack_frames
    global enemyHurt_frames
    global enemy_animation
    global enemy_action
    global enemy_frame_index
    global enemyWalk_frames
    global enemyRun_frames
    if enemy_wounded:
        enemy_wounded = False
        enemyIdle_frames = normalIdle_frames
        enemyAttack_frames = normalAttack_frames
        enemyHurt_frames = normalHurt_frames
        enemyWalk_frames=normalWalk_frames
        enemyRun_frames=normalRun_frames
        enemy_action = "idle"
        enemy_animation = enemyIdle_frames
        enemy_frame_index = 0.0

# -----------------------------
# HURT INTERRUPT
# -----------------------------

def interrupt_to_hurt():
    global evading
    global evade_dx
    global evade_dy
    global leaping
    global leap_dx
    global leap_dy
    global recharging
    evading = False
    evade_dx = 0
    evade_dy = 0
    leaping = False
    leap_dx = 0
    leap_dy = 0
    recharging = False
    change_animation("hurt", hurt_frames)

# -----------------------------
# ACTION RULES
# -----------------------------

def can_walk():
    return current_action not in [
        "shoot",
        "attack",
        "recharge",
        "jump",
        "hurt",
        "dead"
    ]

def can_shoot():
    return current_action not in [
        "shoot",
        "attack",
        "recharge",
        "jump",
        "hurt",
        "dead"
    ]

def can_attack():
    return current_action not in [
        "shoot",
        "attack",
        "jump",
        "hurt",
        "dead"
    ]

def can_evade():
    return current_action not in [
        "shoot",
        "attack",
        "jump",
        "hurt",
        "dead"
    ]

# -----------------------------
# GAME LOOP
# -----------------------------
running = True
while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()
    moving = False
    dx = 0
    dy = 0
    now = pygame.time.get_ticks()
    # -----------------------------
    # ENDING TIMER CHECK
    # -----------------------------
    if now>=endgame_time:
        running=False
    if not ending_triggered:
        if now - rage_start_time >= ending_time:
            ending_triggered = True
            # Final phase starts
            # Enemy keeps fighting normally
            enemy_locked = False
    # -----------------------------
    # ESCAPE TIMER
    # -----------------------------
    if (
            ending_triggered
            and not enemy_dead
            and now - rage_start_time >= escape_time
    ):
        enemy_escape = True
        enemy_locked = False
        enemy_action = "run"
        enemy_animation = enemyRun_frames
        enemy_frame_index = 0.0
        enemy_facing_right = False
    # -----------------------------
    # ENEMY STARTS WALKING TO CIVIC
    # -----------------------------
    if not enemy_march:
        if now - enemy_start_time >= enemy_target_time:
            enemy_march = True
    # -----------------------------
    # RAGE TIMER
    # -----------------------------
    if not rage_mode:
        if now - rage_start_time >= rage_trigger_time:
            activate_rage_mode()
    # -----------------------------
    # EVENTS
    # -----------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # -----------------------------
        # MOUSE
        # -----------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            # LEFT CLICK
            if event.button == 1:
                # NORMAL MODE SHOOT
                if not rage_mode:
                    if can_shoot() and not moving:
                        if shots <= 0 :
                            recharging = True
                            snd_reload.play()
                            recharge_start = pygame.time.get_ticks()
                            change_animation("recharge", recharge_frames)
                        else:
                            shots -= 1
                            snd_gun.play()
                            change_animation("shoot", shot_frames)
                            bullet_x = x + FRAME_W // 2
                            bullet_y = y + 90
                            direction = 1 if facing_right else -1
                            bullets.append([
                                bullet_x,
                                bullet_y,
                                direction
                            ])
                # RAGE MODE LEAP ATTACK
                else:
                    if can_attack():
                        recharging = False
                        attack_has_hit = False  # RESET HERE
                        change_animation("shoot", shot_frames)
                        leaping = True
                        if facing_right:
                            leap_dx = 6
                        else:
                            leap_dx = -6
                        leap_dy = 0
            # RIGHT CLICK ATTACK
            if event.button == 3:
                if can_attack():
                    recharging = False
                    attack_has_hit = False  # RESET HERE
                    # RANDOM RAGE ATTACK
                    if rage_mode:
                        random_attack = random.choice(rage_attack_list)
                        change_animation("attack", random_attack)
                    else:
                        change_animation("attack", attack_frames)
        # -----------------------------
        # EVADE
        # -----------------------------
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if can_evade():
                    recharging = False
                    evading = True
                    if facing_right:
                        evade_dx = -6
                    else:
                        evade_dx = 6
                    evade_dy = 0
                    change_animation("jump", jump_frames)
    # -----------------------------
    # PLAYER MOVEMENT
    # -----------------------------
    if can_walk():
        if keys[pygame.K_a]:
            dx = -speed
            moving = True
            facing_right = False
        if keys[pygame.K_d]:
            dx = speed
            moving = True
            facing_right = True
        if keys[pygame.K_w]:
            dy = -speed
            moving = True
        if keys[pygame.K_s]:
            dy = speed
            moving = True
        x += dx
        y += dy
    # -----------------------------
    # EVADE MOVEMENT
    # -----------------------------
    if evading:
        x += evade_dx
        y += evade_dy
    # -----------------------------
    # LEAP MOVEMENT
    # -----------------------------
    if leaping:
        # CHECK NEXT POSITION
        future_rect = pygame.Rect(x + leap_dx, y + 30 + leap_dy, 50, 70)
        # STOP MOVEMENT IF HITTING ENEMY
        if future_rect.colliderect(enemy_rect):
            leap_dx = 0
            leap_dy = 0
        x += leap_dx
        y += leap_dy
    # -----------------------------
    # SCREEN BOUNDARY LIMITS
    # -----------------------------
    scaled_w = FRAME_W * scale_multiplier
    scaled_h = FRAME_H * scale_multiplier
    if x < 0:
        x = 0
    if x > WIDTH - scaled_w:
        x = WIDTH - scaled_w
    if y < 0:
        y = 0
    if y > HEIGHT - scaled_h:
        y = HEIGHT - scaled_h
    # -----------------------------
    # RECTS
    # -----------------------------
    player_rect = pygame.Rect(x, y + 30, 50, 70)
    enemy_rect = pygame.Rect(enemy_x + 35, enemy_y + 30, 50, 70)
    # -----------------------------
    # BULLETS
    # -----------------------------
    bullets_to_remove = []
    for bullet in bullets:
        bullet[0] += bullet_speed * bullet[2]
        bullet_rect = pygame.Rect(bullet[0], bullet[1], 12, 12)
        if bullet_rect.colliderect(enemy_rect):
            bullets_to_remove.append(bullet)
            if not enemy_dead:
                enemy_hp -= 1
                if enemy_hp < 1:
                    enemy_hp = 1
                if enemy_hp <max_enemy_hp:
                    make_enemy_wounded()
                enemy_action = "hurt"
                enemy_animation = enemyHurt_frames
                enemy_frame_index = 0.0
    bullets = [
        b for b in bullets
        if b not in bullets_to_remove
           and 0 <= b[0] <= WIDTH
    ]
    # -----------------------------
    # PLAYER MELEE ATTACK
    # -----------------------------
    if current_action == "attack":
        # ATTACK HITBOX IN FRONT ONLY
        if facing_right:
            attack_rect = pygame.Rect(x + 80, y + 30, 20, 50)
        else:
            attack_rect = pygame.Rect(x - 10, y + 30, 20, 50)
        # DEBUG HITBOX
        # pygame.draw.rect(screen, (255, 0, 0), attack_rect, 2)
        if attack_rect.colliderect(enemy_rect) and not attack_has_hit:
            attack_has_hit = True
            snd_melee.play()
            if not enemy_dead and enemy_action != "hurt":
                # =====================================
                # ENDING EXECUTION SYSTEM
                # =====================================
                if rage_mode and ending_triggered:
                    # FIRST HIT
                    if not can_kill:
                        can_kill = True
                        enemy_locked = True
                        enemy_action = "idle"
                        enemy_animation = enemyIdle_frames
                        enemy_frame_index = 0.0
                    # SECOND HIT
                    elif can_kill and not kill:
                        kill = True
                        enemy_dead = True
                        enemy_action = "dead"
                        enemy_animation = enemyDead_frames
                        enemy_frame_index = 0.0
                        game_end = True
                        game_result = "ENEMY EXECUTED"
                else:
                    enemy_hp -= 1
                    if enemy_hp < 1:
                        enemy_hp = 1
                    if enemy_hp < max_enemy_hp:
                        make_enemy_wounded()
                    enemy_action = "hurt"
                    enemy_animation = enemyHurt_frames
                    enemy_frame_index = 0.0
    # -----------------------------
    # LEAP ATTACK DAMAGE
    # -----------------------------
    if current_action == "shoot" and rage_mode:
        if facing_right:
            leap_rect = pygame.Rect(x + 40, y + 20, 140, 90)
        else:
            leap_rect = pygame.Rect(x - 90, y + 20, 140, 90)
        if leap_rect.colliderect(enemy_rect) and not attack_has_hit:
            attack_has_hit = True
            if not enemy_dead and enemy_action != "hurt":
                if rage_mode and ending_triggered:
                    # FIRST LEAP HIT
                    if not can_kill:
                        can_kill = True
                        enemy_locked = True
                        enemy_action = "idle"
                        enemy_animation = enemyIdle_frames
                        enemy_frame_index = 0.0
                    # SECOND LEAP HIT
                    elif can_kill and not kill:
                        kill = True
                        enemy_dead = True
                        enemy_action = "dead"
                        enemy_animation = enemyDead_frames
                        enemy_frame_index = 0.0
                        game_end = True
                        game_result = "ENEMY EXECUTED"
                else:
                    enemy_hp -= 1
                    if enemy_hp < 1:
                        enemy_hp = 1
                    if enemy_hp < max_enemy_hp:
                        make_enemy_wounded()
                    enemy_action = "hurt"
                    enemy_animation = enemyHurt_frames
                    enemy_frame_index = 0.0
    # -----------------------------
    # RECHARGE
    # -----------------------------
    if recharging:
        if now - recharge_start >= recharge_time:
            recharging = False
            shots = fullMag
            if current_action == "recharge":
                change_animation("idle", idle_frames)
    # -----------------------------
    # ENEMY AUTO ATTACK
    # -----------------------------
    if not enemy_dead and not enemy_march and not enemy_locked:
        if enemy_action != "attack":
            if now - enemy_attack_timer >= enemy_attack_interval:
                enemy_attack_timer = now
                enemy_action = "attack"
                enemy_animation = enemyAttack_frames
                enemy_frame_index = 0.0
    # -----------------------------
    # ENEMY WALK / TARGET SYSTEM
    # -----------------------------
    if enemy_march and not enemy_dead and not enemy_locked:
        # -----------------------------
        # ENEMY ESCAPE
        # -----------------------------
        if enemy_escape:
            enemy_x -= 5
            enemy_action = "run"
            enemy_animation = enemyRun_frames
            enemy_facing_right = False
            # ENEMY LEFT SCREEN
            if enemy_x < -200:
                game_end = True
                game_result = "ENEMY ESCAPED"
        # =========================================
        # TARGET PARTNER
        # =========================================
        if target_partner and not partner_dead:
            target_x = partner_x + 30
            target_y = partner_y - 20
            dx = target_x - enemy_x
            dy = target_y - enemy_y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 5:
                move_x = (dx / distance) * enemy_speed
                move_y = (dy / distance) * enemy_speed
                enemy_x += move_x
                enemy_y += move_y
                enemy_action = "walk"
                enemy_animation = enemyWalk_frames
                if move_x > 0:
                    enemy_facing_right = True
                else:
                    enemy_facing_right = False
            else:
                if enemy_action != "attack":
                    enemy_action = "attack"
                    enemy_animation = enemyAttack_frames
                    enemy_frame_index = 0.0
                    enemy_has_hit_partner = False
        elif partner_dead:
            if now - enemy_attack_timer >= enemy_attack_interval:
                enemy_attack_timer = now
                enemy_action = "attack"
                enemy_animation = enemyAttack_frames
                enemy_frame_index = 0.0
                enemy_has_hit_partner = False
        # =========================================
        # TARGET CIVIC
        # =========================================
        else:
            target_x = civic_x+20
            target_y = civic_y-50
            dx = target_x - enemy_x
            dy = target_y - enemy_y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 5:
                move_x = (dx / distance) * enemy_speed
                move_y = (dy / distance) * enemy_speed
                enemy_x += move_x
                enemy_y += move_y
                enemy_action = "walk"
                enemy_animation = enemyWalk_frames
                if move_x > 0:
                    enemy_facing_right = True
                else:
                    enemy_facing_right = False
            else:
                if now - enemy_attack_timer >= enemy_attack_interval:
                    enemy_attack_timer = now
                    enemy_action = "attack"
                    enemy_animation = enemyAttack_frames
                    enemy_frame_index = 0.0
                current_enemy_frame = int(enemy_frame_index)
                if current_enemy_frame == 4 and not civic_hit:
                    civic_x += 100
                    civic_y -= 100
                    civic_hit = True
                    target_partner = True
    # -----------------------------
    # UNIVERSAL ENEMY DAMAGE SYSTEM
    # -----------------------------
    if enemy_action == "attack" and current_action != "hurt":
        current_enemy_frame = int(enemy_frame_index)
        # DAMAGE WINDOW
        if 4 <= current_enemy_frame <= 5:
            # ATTACK HITBOX
            if enemy_facing_right:
                attack_rect = pygame.Rect(enemy_x + 60, enemy_y + 45, 20, 50)
            else:
                attack_rect = pygame.Rect(enemy_x - 30, enemy_y + 45, 30, 50)
            # DEBUG
            # pygame.draw.rect(screen, (255,0,0), attack_rect, 2)
            # DAMAGE PLAYER
            if attack_rect.colliderect(player_rect):
                if now - last_player_hit >= player_hit_cooldown:
                    last_player_hit = now
                    snd_melee.play()
                    player_hp -= enemy_attack_damage
                    if player_hp <= 0:
                        player_hp = 0
                        dead = True
                        evading = False
                        evade_dx = 0
                        evade_dy = 0
                        leaping = False
                        leap_dx = 0
                        leap_dy = 0
                        recharging = False
                        change_animation("dead", dead_frames)
                    else:
                        interrupt_to_hurt()
    # -----------------------------
    # ENEMY DAMAGE PARTNER
    # -----------------------------
    if target_partner and not partner_dead:
        partner_rect = pygame.Rect(partner_x + 35, partner_y + 30, 90, 70)
        current_enemy_frame = int(enemy_frame_index)
        # DAMAGE ONLY ON FRAME 4
        if (
                enemy_action == "attack"
                and current_enemy_frame == 4
                and not enemy_has_hit_partner
        ):
            attack_rect = pygame.Rect(enemy_x + 60, enemy_y + 45, 20, 40)
            if attack_rect.colliderect(partner_rect):
                partner_hp -= enemy_partner_damage
                enemy_has_hit_partner = True
                # HURT
                if partner_hp > 0:
                    change_partner_animation("hurt", partner_hurt_frames)
                # DEAD
                else:
                    partner_hp = 0
                    partner_dead = True
                    change_partner_animation("dead", partner_dead_frames)
    # -----------------------------
    # HP REGEN
    # -----------------------------
    # PLAYER REGEN
    if now - player_regen_timer >= player_regen_interval:
        player_regen_timer = now
        if player_hp > 0:
            player_hp += player_regen_amount
            if player_hp > max_player_hp:
                player_hp = max_player_hp
    # ENEMY REGEN
    if now - enemy_regen_timer >= enemy_regen_interval:
        enemy_regen_timer = now
        if not enemy_dead:
            enemy_hp += enemy_regen_amount
            if enemy_hp > max_enemy_hp:
                enemy_hp = max_enemy_hp
            if enemy_hp == max_enemy_hp:
                make_enemy_normal()
    # -----------------------------
    # AUTO PLAYER ANIMATION
    # -----------------------------
    if current_action not in [
        "attack",
        "shoot",
        "hurt",
        "dead",
        "recharge",
        "jump"
    ]:
        if moving:
            change_animation("walk", walk_frames)
        else:
            change_animation("idle", idle_frames)
    # -----------------------------
    # PLAYER ANIMATION UPDATE
    # -----------------------------
    if current_action == "jump":
        frame_index += jump_animation_speed
    else:
        frame_index += normal_animation_speed
    # -----------------------------
    # ENEMY ANIMATION UPDATE
    # -----------------------------
    enemy_frame_index += enemy_animation_speed
    # -----------------------------
    # ENEMY ANIMATION END
    # -----------------------------
    if enemy_frame_index >= len(enemy_animation):
        if enemy_action == "attack":
            enemy_action = "idle"
            enemy_animation = enemyIdle_frames
            enemy_frame_index = 0.0
        elif enemy_action == "hurt":
            if not enemy_dead:
                enemy_action = "idle"
                enemy_animation = enemyIdle_frames
                enemy_frame_index = 0.0
        elif enemy_action == "dead":
            enemy_frame_index = len(enemy_animation) - 1
        else:
            enemy_frame_index = 0.0
    # -----------------------------
    # PLAYER ANIMATION END
    # -----------------------------
    if frame_index >= len(current_animation):
        if current_action in ["idle", "walk"]:
            frame_index = 0
        elif current_action == "jump":
            evading = False
            evade_dx = 0
            evade_dy = 0
            change_animation("idle", idle_frames)
        elif current_action == "shoot":
            leaping = False
            leap_dx = 0
            leap_dy = 0
            change_animation("idle", idle_frames)
        elif current_action == "dead":
            frame_index = len(current_animation) - 1
        elif current_action == "hurt":
            change_animation("idle", idle_frames)
        else:
            change_animation("idle", idle_frames)
    # =========================================================
    # PARTNER AUTO SHOOT
    # =========================================================
    if (
            not partner_dead
            and partner_action != "hurt"
            and now - partner_last_shot >= partner_shot_interval
    ):
        partner_last_shot = now
        snd_shotgun.play()
        change_partner_animation("shoot", partner_shot_frames)
        # SHOOT 3 BULLETSu
        # SHOTGUN SPREAD
        spread_angles = [-15, 0, 15]
        for angle in spread_angles:
            bullet_x = partner_x + 90
            bullet_y = partner_y + 70
            # AIM AT ENEMY
            target_x = enemy_x + 60
            target_y = enemy_y + 60
            dx = target_x - bullet_x
            dy = target_y - bullet_y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance == 0:
                distance = 1
            # NORMALIZED DIRECTION
            dir_x = dx / distance
            dir_y = dy / distance
            # ROTATE DIRECTION FOR SPREAD
            radians = math.radians(angle)
            spread_x = (
                    dir_x * math.cos(radians)
                    - dir_y * math.sin(radians)
            )
            spread_y = (
                    dir_x * math.sin(radians)
                    + dir_y * math.cos(radians)
            )
            partner_bullets.append([
                bullet_x,
                bullet_y,
                spread_x,
                spread_y
            ])
    # =========================================================
    # PARTNER BULLETS UPDATE
    # =========================================================
    partner_remove = []
    for bullet in partner_bullets:
        # MOVE
        bullet[0] += bullet[2] * partner_bullet_speed
        bullet[1] += bullet[3] * partner_bullet_speed
        bullet_rect = pygame.Rect(bullet[0], bullet[1], 10, 10)
        # HIT ENEMY
        if bullet_rect.colliderect(enemy_rect):
            partner_remove.append(bullet)
            if not enemy_dead:
                enemy_hp -= 1
                if enemy_hp < 1:
                    enemy_hp = 1
                if enemy_hp < max_enemy_hp:
                    make_enemy_wounded()
                enemy_action = "hurt"
                enemy_animation = enemyHurt_frames
                enemy_frame_index = 0.0
        # REMOVE OFFSCREEN
        if (
            bullet[0] < -50
            or bullet[0] > WIDTH + 50
            or bullet[1] < -50
            or bullet[1] > HEIGHT + 50
        ):
            partner_remove.append(bullet)
    for bullet in partner_remove:
        if bullet in partner_bullets:
            partner_bullets.remove(bullet)
    # =========================================================
    # PARTNER ANIMATION UPDATE
    # =========================================================
    partner_frame_index += partner_animation_speed
    if partner_frame_index >= len(partner_animation):
        if partner_action == "shoot":
            change_partner_animation("idle", partner_idle_frames)
        elif partner_action == "hurt":
            if not partner_dead:
                change_partner_animation("idle", partner_idle_frames)
        elif partner_action == "dead":
            partner_frame_index = len(partner_animation) - 1
        else:
            partner_frame_index = 0.0
    # -----------------------------
    # DRAW
    # -----------------------------
    screen.blit(bgGrassGround, (0, 0))
    # DRAW ENEMY
    enemy_frame = enemy_animation[
        int(enemy_frame_index)
    ]
    # FLIP ENEMY
    if not enemy_facing_right:
        enemy_frame = pygame.transform.flip(enemy_frame, True, False)
    enemy_frame = pygame.transform.scale(
        enemy_frame,
        (
            int(FRAME_W * scale_multiplier),
            int(FRAME_H * scale_multiplier)
        )
    )
    screen.blit(enemy_frame, (enemy_x, enemy_y))
    # DRAW PLAYER
    current_frame = current_animation[
        int(frame_index)
    ]
    if not facing_right:
        current_frame = pygame.transform.flip(current_frame, True, False)
    current_frame = pygame.transform.scale(
        current_frame,
        (
            int(FRAME_W * scale_multiplier),
            int(FRAME_H * scale_multiplier)
        )
    )
    screen.blit(current_frame, (x, y))
    # DRAW BULLETS
    for bullet in bullets:
        pygame.draw.circle(
            screen,
            (255, 220, 50),
            (
                int(bullet[0]),
                int(bullet[1])
            ),
            6
        )
    screen.blit(civic_img, (civic_x, civic_y))
    # =========================================================
    # DRAW PARTNER
    # =========================================================
    partner_frame = partner_animation[
        int(partner_frame_index)
    ]
    partner_frame = pygame.transform.scale(
        partner_frame,
        (
            int(FRAME_W * 0.9),
            int(FRAME_H * 0.9)
        )
    )
    screen.blit(partner_frame, (partner_x, partner_y))
    # =========================================================
    # DRAW PARTNER BULLETS
    # =========================================================
    for bullet in partner_bullets:
        pygame.draw.circle(
            screen,
            (50, 200, 255),
            (
                int(bullet[0]),
                int(bullet[1])
            ),
            5
        )
    # -----------------------------
    # UI
    # -----------------------------
    draw_text(screen, f"Shots: {shots}/{fullMag}", (255, 255, 255), (20, 20), "vcrosdmono", 35)
    draw_text(screen, f"Action: {current_action}", (255, 255, 0), (20, 60), "vcrosdmono", 35)
    draw_text(screen, f"Enemy: {enemy_action}", (255, 100, 100), (20, 100), "vcrosdmono", 35)
    draw_text(screen, f"Player HP: {int(player_hp)}", (100, 255, 100), (20, 140), "vcrosdmono", 35)
    draw_text(screen, f"Enemy HP: {enemy_hp:.1f}", (255, 100, 100), (20, 180), "vcrosdmono", 35)
    if now - rage_start_time >= ending_time:
        draw_text(screen, f"Can Kill: {bool(can_kill)}", (255, 100, 100), (20, 240), "vcrosdmono", 35)
    draw_text(screen, f"Time: {int(now)}", (255, 100, 100), (20, 280), "vcrosdmono", 35)
    if rage_mode:
        draw_text(screen, "RAGE MODE", (255, 40, 40), (20, 220), "vcrosdmono", 35)
    if game_end:
        draw_text(screen, game_result, (255, 50, 50), (WIDTH // 2, HEIGHT // 2), "vcrosdmono", 35)
    pygame.display.flip()
pygame.quit()
sys.exit()