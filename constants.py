import pygame

pygame.init()

# Scene sizes are number of tiles in the scene.
SCENE_WIDTH_TILES = 24
SCENE_HEIGHT_TILES = 24

# Tile resolution
RES = 32

SCENE_WIDTH = SCENE_WIDTH_TILES * RES
SCENE_HEIGHT = SCENE_HEIGHT_TILES * RES

# Game sizes
SIDE_BAR_WIDTH = 256
LOWER_BANNER_HEIGHT = 224
GAME_WIDTH = SCENE_WIDTH + SIDE_BAR_WIDTH
GAME_HEIGHT = SCENE_HEIGHT + LOWER_BANNER_HEIGHT
INPUT_BOX_HEIGHT = 32

# Color definitions
COLOR_BLACK = (0,0,0)
COLOR_GREY = (100,100,100)
COLOR_WHITE = (255,255,255)

# Game colors
DEFAULT_BG = COLOR_GREY
CHEAT_TXT = COLOR_WHITE
CHEAT_TXT_BOX_BG = COLOR_BLACK
DEBUG_TXT = COLOR_WHITE
MENU_HEADER_TXT = COLOR_BLACK

# Sprites
S_PLAYER = pygame.image.load("art/character.png")
S_ENEMY = pygame.image.load("art/enemy.png")
S_CHEST = pygame.image.load("art/chest.png")
S_CHEST_OPEN = pygame.image.load("art/chest_open.png")
S_SELECTOR = pygame.image.load("art/selector.png")
S_DOOR = pygame.image.load("art/door.png")
S_DOOR_OPEN = pygame.image.load("art/door.png") # replace this art

S_SWORD = pygame.image.load("art/sword.png")
S_SHIELD = pygame.image.load("art/shield.png")
S_GLOVES = pygame.image.load("art/gloves.png")
S_BOOTS = pygame.image.load("art/boots.png")
S_BELT = pygame.image.load("art/belt.png")
S_HELMET = pygame.image.load("art/helmet.png")
S_BRACERS = pygame.image.load("art/bracers.png")
S_SHOULDERS = pygame.image.load("art/shoulders.png")

S_GOLD_COIN = pygame.image.load("art/gold_coin.png")
S_SILVER_COIN = pygame.image.load("art/silver_coin.png")
S_BRONZE_COIN = pygame.image.load("art/bronze_coin.png")

# Loot tables
TABLE_CURRENCY = "data//currency_table.txt"
TABLE_GEAR = "data//gear_table.txt"
TABLE_TIER = "data//tier_table.txt"

LOOT_PROPERTIES = "data//loot.txt"

#Menus
MENU_FIRST_PAGE = pygame.image.load("art/Side bar menu first page.png")
MENU_MIDDLE_PAGE = pygame.image.load("art/Side bar menu middle page.png")
MENU_LAST_PAGE = pygame.image.load("art/Side bar menu last page.png")
MENU_BACKGROUND = pygame.image.load("art/Side bar menu background.png")
SIDE_HEADER_HEIGHT = 64
PAGE_TURN_HITBOX = 20 # Height and width of the page turn hitbox in pixels
HEADER_1_STRING = "SELECTED"
CHEST_INVENTORY = pygame.image.load("art/chest_inventory.png")
