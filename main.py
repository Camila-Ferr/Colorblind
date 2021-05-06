import pygame
from pygame import mixer
import os
import random
import csv

import boss
import menu

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Colorblind Quest")

# frame rate
clock = pygame.time.Clock()
FPS = 60

# variaveis do jogo
GRAVIDADE = 0.70
SCROOL_TRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
MAX_LEVEL = 2

#muda em relação a quantidade de tipos de objetos de mundo
TILE_TYPES = 20
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

# Ações do heroi
moving_left = False
moving_right = False
atirar = False
bomba = False
bomba_jogou = False

# carregar músicas
pygame.mixer.music.load('audios/fase1.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audios/jump.wav')
morte_fx = pygame.mixer.Sound('audios/morte.wav')
shot_fx = pygame.mixer.Sound('audios/shot.wav')
shotmal_fx = pygame.mixer.Sound('audios/monstro.wav')
grenade_fx = pygame.mixer.Sound('audios/grenade.wav')


# carregar imagens
fundo1_img = pygame.image.load('Sprites/Background/1.png').convert_alpha()
fundo2_img = pygame.image.load('Sprites/Background/0.png').convert_alpha()
montanha_img = pygame.image.load('Sprites/Background/3.png').convert_alpha()
ceu_img = pygame.image.load('Sprites/Background/2.png').convert_alpha()

#guardar os tiles numa lista

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'Sprites/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# ataque
bullet_img = pygame.image.load('Sprites/Elementos/ataque/bola.png').convert_alpha()
bullet_img2 = pygame.image.load('Sprites/Elementos/ataque/projetil.png').convert_alpha()

# bomba
bomba_img = pygame.image.load('Sprites/Elementos/ataque/bola.png').convert_alpha()

#coletavel
coracao_img = pygame.image.load('Sprites/Elementos/coracao.png').convert_alpha()
coracao_sem_vida_img = pygame.image.load('Sprites/Elementos/coracao_vazio.png').convert_alpha()
moeda_img = pygame.image.load('Sprites/Elementos/moeda.png').convert_alpha()

item_coletavel = {
    'coracao': coracao_img,
    'moeda': moeda_img
}

# definir cores
BG = (201, 144, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

#definir fonte
fonte = pygame.font.SysFont('Futura', 30)

def update_musica():
    if (menu.som == 0):
        pygame.mixer.music.set_volume(0)
    elif (menu.som==1):
        pygame.mixer.music.set_volume(0.5)

def desenhar_bg():
    screen.fill(BG)
    for x in range (10):
        screen.blit(ceu_img,((x*ceu_img.get_width()-500)- bg_scroll*0.5 ,0))
        screen.blit(montanha_img,((x*montanha_img.get_width()-500)-bg_scroll * 0.8,SCREEN_HEIGHT-montanha_img.get_height()-300))
        screen.blit(fundo1_img,((x*fundo1_img.get_width()-500)-bg_scroll * 0.7 ,SCREEN_HEIGHT-fundo1_img.get_height()-170))
        screen.blit(fundo2_img, ((x*fundo2_img.get_width()-600)-bg_scroll * 0.8 , SCREEN_HEIGHT - fundo2_img.get_height()-30))

#função para resetar level
def reset_level():
    inimigo_group.empty()
    bullet_group.empty()
    bullet_group2.empty()
    bomba_group.empty()
    explosao_group.empty()
    item_coletavel_group.empty()
    decoracao_group.empty()
    agua_group.empty()
    saida_group.empty()

    #empty.tile_list
    data = []
    for row in range (ROWS):
        r=[-1]*COLS
        data.append(r)
    return data

def desenhar_texto(texto , fonte , text_col,  x, y):
    img = fonte.render(texto, True, text_col)
    screen.blit(img, (x, y))


class Personagens(pygame.sprite.Sprite):
    def __init__(self, char_tipo, x, y, scale, velocidade, municao , bombas):
        pygame.sprite.Sprite.__init__(self)
        self.vivo = True
        self.char_tipo = char_tipo
        self.velocidade = velocidade
        self.municao = municao
        self.municao_inicial = municao
        self.tiro_cooldown = 0
        self.bombas = bombas
        self.vida = 3
        self.pontos = 0
        self.max_vida = self.vida
        self.direction = 1
        self.vel_y = 0
        self.pulo = False
        self.no_ar = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        #Variaveis para IA
        self.move_count = 0
        self.visao = pygame.Rect(0, 0, 150, 20)
        self.parado = False
        self.parado_count = 0

        # carregar todas as imagens do personagem
        tipos_animacao = ['parado', 'move', 'pulo', 'morto', 'ataque']

        for animacao in tipos_animacao:
            # reset lista temporaria
            temporaria_list = []
            # contar quantas imagens tem na pasta
            num_of_frames = len(os.listdir(f'Sprites/{self.char_tipo}/{animacao}'))

            # Passando pelas fotos para forma uma animação
            for i in range(num_of_frames):
                img = pygame.image.load(f'Sprites/{self.char_tipo}/{animacao}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temporaria_list.append(img)
            # Adicionando uma lista em outra lista de animação
            self.animation_list.append(temporaria_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_width()

    def update(self):
        self.update_animation()
        self.checar_seEstaVivo()
        # update cooldown
        if self.tiro_cooldown > 0:
            self.tiro_cooldown -= 1


    def mover(self, moving_left, moving_right):
        # resetar as variaveis de movimento
        screen_scroll = 0

        dx = 0
        dy = 0

        # atribuindo variaveis para o movimento
        if moving_left:
            dx = - self.velocidade
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.velocidade
            self.flip = False
            self.direction = 1

        # Pular
        if self.pulo == True and self.no_ar == False:
            self.vel_y = - 11
            self.pulo = False
            self.no_ar = True

        # Gravidade
        self.vel_y += GRAVIDADE
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # checar colisão com chão
        # 300 é o nível do chão

        comColisao = False

        for tile in mundo.lista_obstaculos:

            #checar colisão na direção x
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0

                #Se ele colidir, virar
                if self.char_tipo == 'Goblin':
                    self.direction *= -1
                    self.move_count = 0

            #checar colisão na posição y
            if tile[1].colliderect(self.rect.x + dx, self.rect.y + dy + 49, self.width, self.height):
                comColisao = True

                #pulando
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy=tile[1].bottom-self.rect.top

                #caindo
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.rect.y += dy
                    self.vel_y = 0
                    self.no_ar = False

        #checar a colisão com a água
        if self.char_tipo == "Heroi":
            if pygame.sprite.spritecollide(self, agua_group , False):
                self.vida = 0

        if self.char_tipo == 'Goblin':
            if pygame.sprite.spritecollide(self, agua_group, False):
                self.direction *= -1


        #checar colisão com a saida
        level_complete = False
        if pygame.sprite.spritecollide(self, saida_group, False):
            level_complete = True

        #if self.rect.bottom>SCREEN_HEIGHT:
            self.vida = 0

        # atualizando a posicao retangulo
        self.rect.x += dx
        if self.no_ar or not comColisao:
            self.rect.y += dy

        if self.char_tipo == 'Heroi':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # atualizando a tela de acordo com a posição do heroi
        if self.char_tipo == 'Heroi':
            if ((self.rect.right > SCREEN_WIDTH - SCROOL_TRESH and bg_scroll < mundo.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                    or (self.rect.left < SCROOL_TRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def atirar_mal(self):
        if not self.no_ar:
            if self.tiro_cooldown == 0 and self.municao > 0:
                self.tiro_cooldown = 100
                tiro = Bullet_mal(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction), self.rect.centery,
                          self.direction)
                bullet_group2.add(tiro)


    def atirar(self):
        if not self.no_ar:
            if self.tiro_cooldown == 0 and self.municao > 0:
                self.tiro_cooldown = 70
                tiro = Bullet(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction), self.rect.centery,
                          self.direction)
                bullet_group.add(tiro)
                if menu.som == 1:
                    shot_fx.play()


    def ia(self):
        if self.vivo and heroi.vivo:
            if self.parado == False and random.randint(1, 200) == 1:
                self.update_action(0) #0: parado
                self.parado = True
                self.parado_count = 50

            #checar se a IA ta perto do heroi
            if self.visao.colliderect(heroi.rect):
                # Para de andar e olha pro heroi
                self.update_action(4)#4: atirar
                self.atirar_mal()
                if (menu.som==1):
                    shotmal_fx.play()

            else:
                if self.parado == False:
                    if self.direction == 1:
                        ia_move_direita = True
                    else:
                        ia_move_direita = False

                    ia_move_esquerda = not ia_move_direita
                    self.mover(ia_move_esquerda, ia_move_direita)
                    self.update_action(1) # 1: mover
                    self.move_count += 1

                    #Atualiza a visao da IA
                    self.visao.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_count > TILE_SIZE:
                        self.direction *= -1
                        self.move_count *= -1

                else:
                    self.parado_count -= 1
                    if self.parado_count <= 0:
                        self.parado = False

        #scrool
        self.rect.x += screen_scroll

    def update_animation(self):
        # update animation
        ANIMATION_TEMPORIZADOR = 100
        # atualizar a imagem dependendo do frame atual
        self.image = self.animation_list[self.action][self.frame_index]
        # Checar o tempo da animação
        if pygame.time.get_ticks() - self.update_time > ANIMATION_TEMPORIZADOR:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # Resetar a animação
        if self.frame_index >= len(self.animation_list[self.action]):

            # Para a animaocao se for a de morte
            if self.action == 5:
                self.frame_index = len(self.animation_list[self.action])

            else:
                self.frame_index = 0


    def update_action(self, nova_action):
        # checar se a nova ação é diferente a anterior
        if nova_action != self.action:
            self.action = nova_action
            # atualizar animação
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    def checar_seEstaVivo(self):
        if self.vida <= 0:
            self.vida = 0
            self.velocidade = 0
            self.vivo = False
            self.update_action(3)


    def desenhar(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Mundo():

    def __init__(self):
        self.lista_obstaculos = []

    def process_data(self, data):
        self.level_length = len(data[0])

        #passar pelos valores e arquivos do data
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)

                    #Criar as plataformas para os persoangens
                    #de 0 a 8
                    if (tile >= 0 and tile <= 8) or (tile == 12):
                        self.lista_obstaculos.append(tile_data)

                    #criar os obstaculos que matam o personagem
                    #9 a 10
                    elif tile >= 9 and tile <= 10:
                        agua = Agua(img, x * TILE_SIZE, y * TILE_SIZE)
                        agua_group.add(agua)

                    #criar a decoração do cenário
                    #11 a 14
                    elif (tile == 11) or (tile>=13 and tile <= 14):
                        decoracao = Decoracao(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoracao_group.add(decoracao)

                    #criar heroi
                    #15
                    elif tile == 15:
                        heroi = Personagens('Heroi', x * TILE_SIZE + 380, y * TILE_SIZE, 0.4, 5, 20, 5)

                    #criar inimigos
                    #16
                    elif tile == 16:
                        inimigo = Personagens('Goblin', x * TILE_SIZE, y * TILE_SIZE, 0.5, 3, 20, 2)
                        inimigo_group.add(inimigo)

                    #criar moedas
                    #17
                    elif tile == 17:
                        item_coletavel = Coletaveis('coracao', x * TILE_SIZE, y * TILE_SIZE)
                        item_coletavel_group.add(item_coletavel)


                    #criar vida
                    #18
                    elif tile == 18:
                        item_coletavel = Coletaveis('moeda', x * TILE_SIZE, y * TILE_SIZE)
                        item_coletavel_group.add(item_coletavel)

                    #criar saida
                    #19
                    elif tile == 19:
                        saida = Saida(img, x * TILE_SIZE, y * TILE_SIZE)
                        saida_group.add(saida)
        return heroi


    def draw(self):
        for tile in self.lista_obstaculos:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoracao(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Agua(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Saida(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Coletaveis(pygame.sprite.Sprite):
    def __init__(self, item_tipo, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_tipo = item_tipo
        self.image = item_coletavel[self.item_tipo]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


    def update(self):
        #scroll
        self.rect.x += screen_scroll
        #checar se o jogador pegou a caixa
        if pygame.sprite.collide_rect(self, heroi):
            #checar qual tipo de colecionável
            if self.item_tipo == 'coracao':
                heroi.vida += 1
                if heroi.vida > heroi.max_vida:
                    heroi.vida = heroi.max_vida

            elif self.item_tipo == 'moeda':
                heroi.pontos += 50
            self.kill()

class Bullet_mal(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.velocidade = 10
        self.image = bullet_img2
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # mover tiro
        self.rect.x += (self.direction * self.velocidade) + screen_scroll

        # checar se a bala saiu da tela
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # checar a colisão com o nível
        for tile in mundo.lista_obstaculos:
            if tile[1].colliderect(self.rect):
                self.kill()

        # checar colisão com personagens
        if pygame.sprite.spritecollide(heroi, bullet_group2, False):
            if heroi.vivo:
                heroi.vida -= 1
                self.kill()



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.velocidade = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction


    def update(self):
        # mover tiro
        self.rect.x += (self.direction * self.velocidade) + screen_scroll

        # checar se a bala saiu da tela
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # checar a colisão com o nível
        for tile in mundo.lista_obstaculos:
            if tile[1].colliderect(self.rect):
                self.kill()

        # checar colisão com personagens
        if pygame.sprite.spritecollide(heroi, bullet_group, False):
            if heroi.vivo:
                heroi.vida -= 1
                self.kill()

        # Mesma função so que para inimigos
        for inimigo in inimigo_group:
            if pygame.sprite.spritecollide(inimigo, bullet_group, False):
                if inimigo.vivo:
                    inimigo.vida -= 2
                    heroi.pontos += 15
                    inimigo_group.remove(inimigo)
                    inimigo.kill()
                self.kill()


class Bomba(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.velocidade = 7
        self.image = bomba_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVIDADE
        dx = self.direction * self.velocidade
        dy = self.vel_y

       #checar colisão da bomba com o chão
        for tile in mundo.lista_obstaculos:
            # checar se a bomba vai sair da tela
            if tile[1].colliderect (self.rect.x + dx, self.rect.y + dy, self.width,self.height):
                self.direction *= -1
                dx = self.direction * self.velocidade

            # checar colisão na posição y
            if tile[1].colliderect(self.rect.x + dx, self.rect.y + dy, self.width, self.height):
                self.velocidade = 0
                # thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top

                # falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        # atualizar posição da granada
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #timer da explosao
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosao = Explosao(self.rect.x, self.rect.y, 0.5)
            explosao_group.add(explosao)
            if menu.som == 1:
                grenade_fx.play()
                grenade_fx.set_volume(0.8)

            #dano a qualquer um perto
            if abs(self.rect.centerx - heroi.rect.centerx) < TILE_SIZE * 4 and \
                abs(self.rect.centery - heroi.rect.centery < TILE_SIZE * 4):
                heroi.vida -= 1

            for inimigo in inimigo_group:
                if abs(self.rect.centerx - inimigo.rect.centerx) < TILE_SIZE * 4 and \
                    abs(self.rect.centery - inimigo.rect.centery < TILE_SIZE * 4):

                    if inimigo.vivo:
                        inimigo.vida -= 3
                        heroi.pontos += 30
                        inimigo_group.remove(inimigo)
                        inimigo.kill()


class Explosao(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.imagens = []
        for num in range(1, 6):
            img = pygame.image.load(f'Sprites/Explosao/exp{num}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.imagens.append(img)

        self.frame_index = 0
        self.image = self.imagens[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0


    def update(self):
        #scroll
        self.rect.x += screen_scroll

        EXPLOSAO_VELOCIDADE = 4
        #atualizar a animação da explosão
        self.counter += 1

        if self.counter >= EXPLOSAO_VELOCIDADE:
            self.counter = 0
            self.frame_index += 1

            #se a animação esta completa ,deleta a explosão
            if self.frame_index >= len(self.imagens):
                self.kill()

            else:
                self.image = self.imagens[self.frame_index]


class telaFade():
    def __init__(self, direcao, cor, velocidade):
        self.direcao = direcao
        self.cor = cor
        self.velocidade = velocidade
        self.count_fade = 0


    def fade(self):
        fade_completo = False
        self.count_fade += self.velocidade

        #toda tela fade
        if self.direcao == 1:
            pygame.draw.rect(screen, self.cor, (0 - self.count_fade, 0, SCREEN_WIDTH//2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.cor, (SCREEN_WIDTH // 2 + self.count_fade, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.cor, (0, 0 - self.count_fade, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.cor, (0, SCREEN_HEIGHT // 2 + self.count_fade, SCREEN_WIDTH, SCREEN_HEIGHT))

        #descer fade verticalmente
        if self.direcao == 2:
            pygame.draw.rect(screen, self.cor, (0, 0, SCREEN_WIDTH, 0 + self.count_fade))
        if self.count_fade >= SCREEN_WIDTH:
            fade_completo = True

        return fade_completo


#criar os fades
intro_fade = telaFade(1, BLACK, 4)
morte_fade = telaFade(2, RED, 4)


# criar grupos de sprite
inimigo_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
bullet_group2 = pygame.sprite.Group()
bomba_group = pygame.sprite.Group()
explosao_group = pygame.sprite.Group()
item_coletavel_group = pygame.sprite.Group()
decoracao_group = pygame.sprite.Group()
agua_group = pygame.sprite.Group()
saida_group = pygame.sprite.Group()


#criar uma lista de tiles vazia
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

#carregar o level do mapa e criar o mundo
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

mundo = Mundo()
heroi = mundo .process_data(world_data)

run = True
while run:

    clock.tick(FPS)
    if start_game == False:
        menu.draw_menu()
        if menu.estado == 0:
            start_game = True
            start_intro = True

    else:
        desenhar_bg()

        #desenhar mundo
        mundo.draw()

        #mostrar vida
        desenhar_texto(f'VIDA:', fonte, BLACK, 10, 35)
        for y in range(heroi.max_vida):
            screen.blit(coracao_sem_vida_img, (70 + (y * 40), 30))

        for x in range(heroi.vida):
            screen.blit(coracao_img, (70 + (x * 40), 30))

        #mostrar pontos
        desenhar_texto(f'{heroi.pontos}', fonte, BLACK, 750, 35)
        #screen.blit(moeda_img, 720, 35)

        heroi.update()
        heroi.desenhar()
        update_musica()
        for inimigo in inimigo_group:
            inimigo.ia()
            inimigo.update()
            inimigo.desenhar()

        # update e desenhar grupos
        bullet_group.update()
        bullet_group2.update()
        bomba_group.update()
        explosao_group.update()
        item_coletavel_group.update()
        decoracao_group.update()
        agua_group.update()
        saida_group.update()

        bullet_group.draw(screen)
        bullet_group2.draw(screen)
        bomba_group.draw(screen)
        explosao_group.draw(screen)
        item_coletavel_group.draw(screen)
        decoracao_group.draw(screen)
        agua_group.draw(screen)
        saida_group.draw(screen)

        #mostrar intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.count_fade = 0


        # atualizar ação
        if heroi.vivo:
            # atirar balas
            if atirar:
                heroi.atirar()

            # jogar bombas
            elif bomba and (bomba_jogou == False) and (heroi.bombas > 0):
                bomba = Bomba(heroi.rect.centerx + (0.5 * heroi.rect.size[0] * heroi.direction),
                              heroi.rect.top, heroi.direction)
                bomba_group.add(bomba)
                heroi.bombas -= 1
                bomba_jogou = True

            if heroi.no_ar:
                heroi.update_action(2)  # 2 : Pular

            elif moving_left or moving_right:
                heroi.update_action(1)  # 1: andar

            elif atirar:
                heroi.update_action(4)  # 4 : Atirar

            else:
                heroi.update_action(0)  # 0 : parado

            screen_scroll, level_complete = heroi.mover(moving_left, moving_right)
            bg_scroll -= screen_scroll

            #checar se o player completou o nível
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVEL:
                    # carregar o level do mapa e criar o mundo
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    mundo = Mundo()
                    heroi = mundo.process_data(world_data)
                    vida = 3
                if level==3:
                    boss.boss()

        else:
            morte_fx.play()
            screen_scroll = 0
            if morte_fade.fade():
                morte_fade.count_fade = 0
                start_intro = True
                bg_scroll = 0
                world_data = reset_level()

                # carregar o level do mapa e criar o mundo
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)

                mundo = Mundo()
                heroi = mundo.process_data(world_data)
                vida = 3
                start_game = False

        for event in pygame.event.get():

            # quit game
            if event.type == pygame.QUIT:
                run = False

            # keyboard presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_SPACE:
                    atirar = True
                if event.key == pygame.K_g:
                    bomba = True
                if event.key == pygame.K_w and heroi.vivo:
                    heroi.pulo = True
                    if menu.som == 1:
                        jump_fx.play()

                if event.key == pygame.K_ESCAPE:
                    start_game=False

            # Keyboard released
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                if event.key == pygame.K_SPACE:
                    atirar = False
                if event.key == pygame.K_g:
                    bomba = False
                    bomba_jogou = False

        pygame.display.update()
pygame.quit()