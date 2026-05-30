# Screen
WIDTH = 1200
HEIGHT = 700
FPS = 60

# Frame dimensions
FRAME_W = 128
FRAME_H = 128

# Debug
DEBUG = True

# Debug colors
DEFAULTBLUE = (0, 0, 255)
DEFAULTGREEN = (0, 255, 0)
DEFAULTRED = (255, 0, 0)
DEFAULTWHITE = (255, 255, 255)

# Debug grid
GRID_COLOR = (255, 255, 255)
GRID_SPACING = 100
GRID_ALPHA = 40

# Player character offset (whitespace padding in sprite frames)
PLAYER_CHAR_OFFSET_X = 40
PLAYER_CHAR_OFFSET_Y = 60
PLAYER_CHAR_HITBOX_W = FRAME_W - 80   # 48
PLAYER_CHAR_HITBOX_H = FRAME_H - 60   # 68

# Enemy character offset (whitespace padding in sprite frames)
ENEMY_CHAR_OFFSET_X = 40
ENEMY_CHAR_OFFSET_Y = 65
ENEMY_CHAR_HITBOX_W = 70
ENEMY_CHAR_HITBOX_H = 60

# Gravity
GRAVITY = 2
JUMP_FORCE = -20

# Player
PLAYER_SPEED = 5
PLAYER_HP = 100.0
PLAYER_MAX_HP = 100.0
PLAYER_HIT_COOLDOWN = 1000
PLAYER_REGEN_INTERVAL = 3000
PLAYER_REGEN_AMOUNT = 10
PLAYER_RAGE_REGEN_AMOUNT = 30

# Player shoot
MAX_SHOTS = 12
BULLET_SPEED = 12
RECHARGE_TIME = 1300

# Player leap
LEAP_SPEED = 6

# Player animation speeds
NORMAL_ANIM_SPEED = 0.15
JUMP_ANIM_SPEED = 0.25

# Enemy
ENEMY_HP = 100
ENEMY_MAX_HP = 100
ENEMY_SPEED = 2
ENEMY_ANIM_SPEED = 0.15
ENEMY_ATTACK_INTERVAL = 3000
ENEMY_ATTACK_DAMAGE = 30
ENEMY_PARTNER_DAMAGE = 1
ENEMY_REGEN_INTERVAL = 5000
ENEMY_REGEN_AMOUNT = 1

# Enemy march / escape
ENEMY_TARGET_TIME = 74000
ESCAPE_SPEED = 5

# Rage mode
RAGE_TRIGGER_TIME = 89000
RAGE_SCALE = 1.2

# Ending
ENDING_TIME = 118000
ESCAPE_TIME = 148000
ENDGAME_TIME = 160300

# Partner
PARTNER_HP = 3
PARTNER_ANIM_SPEED = 0.15
PARTNER_SHOT_INTERVAL = 3000
PARTNER_BULLET_SPEED = 10
PARTNER_SPREAD_ANGLES = [-15, 0, 15]

# Scale
DEFAULT_SCALE = 1.0

# Backgrounds (layered)
BG_FULL_PATH = "resources/image/background/night-grass-full.png"
BG_SKY_PATH = "resources/image/background/night-grass-sky.png"
BG_MOON_PATH = "resources/image/elements/moon.png"
BG_CLOUDS_PATH = "resources/image/background/night-grass-clouds.png"
BG_ROCKS_PATH = "resources/image/background/night-grass-rocks.png"
BG_GROUND_PATH = "resources/image/background/night-grass-ground.png"

# Moon position
MOON_X = 700
MOON_Y = 100
MOON_SCALE_W = 200

# Font
FONT_NAME = "vcrosdmono"
FONT_SIZE = 35

# Asset paths
PLAYER_PATH = "resources/image/sprites/maincharacter/"
RAGE_PATH = "resources/image/sprites/rageCharacter/"
ENEMY_PATH = "resources/image/sprites/enemy/"
WOUNDED_ENEMY_PATH = "resources/image/sprites/woundedEnemy/"
PARTNER_PATH = "resources/image/sprites/partner/"
MUSIC_PATH = "resources/audio/musics/waking demon.mp3"
MUSIC_VOLUME = 0.0
