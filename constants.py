import pygame
pygame.init()

#Variaveis globais
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

SCREEN = (SCREEN_WIDTH, SCREEN_HEIGHT)

ANIMATION_TEMPORIZADOR = 100
FPS = 60
GRAVIDADE = 0.70
SCROOL_TRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
MAX_LEVEL = 2

TILE_TYPES = 20

#Cores
BG = (201, 144, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

#Fonte
fonte = pygame.font.SysFont('Arial', 24,  bold=False, italic=False)

#Paths audios
PATH_MUSICA_FX = 'audios/boss.ogg'

PATH_JUMP_FX = 'audios/jump.wav'
PATH_ATAQUE_HEROI_FX = 'audios/heroThrowing.wav'
PATH_ATAQUE_HBOSS_FX = 'audios/espada.wav'
PATH_DANO_HEROI_FX = 'audios/heroTakingHit.wav'
PATH_MORTE_FX = 'audios/morte.wav'

PATH_ATAQUE_GOBLIN_FX = 'audios/goblinThrowing.wav'
PATH_DANO_GOBLIN_FX = 'audios/goblinTakingHit.wav'
PATH_GRANADA_FX = 'audios/tacarGrenade.wav'
PATH_EXPLOSAO_FX = 'audios/grenade.wav'
PATH_MOEDA_FX = 'audios/moedaColetada.wav'
PATH_CORACAO_FX = 'audios/coracao.wav'
PATH_ATAQUE1_DRAGAO_FX = 'audios/ataque.wav'
PATH_ATAQUE2_DRAGAO_FX = 'audios/ataque2.wav'

#Paths sprites
PATH_BACKGROUND0 = 'sprites/background/0.png'
PATH_BACKGROUND1 = 'sprites/background/1.png'
PATH_BACKGROUND2 = 'sprites/background/2.png'
PATH_BACKGROUND3 = 'sprites/background/3.png'

PATH_BACKGROUND_FINAL = 'sprites/background/bg_final.png'
PATH_CENARIO_PAINEL = 'sprites/cenаrio/painel.png'
PATH_MENU_WIN = 'sprites/menu/win.png'
PATH_MENU_LOSE = "sprites/menu/lose.png"
PATH_ATAQUE_BOLA = 'sprites/elementos/ataque/bola.png'
PATH_ATAQUE_PROJETIL = 'sprites/elementos/ataque/projetil.png'
PATH_CORACAO = 'sprites/elementos/coracao.png'
PATH_MOEDA = 'sprites/elementos/moeda.png'
PATH_CORACAO_VAZIO = 'sprites/elementos/coracao_vazio.png'

