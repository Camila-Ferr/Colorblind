import pygame
import os
import random
import csv

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
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
#muda em relação a quantidade de tipos de objetos de mundo
TILE_TYPES = 21
level = 1


# Ações do heroi
moving_left = False
moving_right = False
atirar = False
bomba = False
bomba_jogou = False

# carregar imagens
#guardar os tiles numa lista

'''img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'Sprites/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
'''
# ataque
bullet_img = pygame.image.load('Sprites/Elementos/ataque/bola.png').convert_alpha()

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

def desenhar_bg():
    screen.fill(BG)
    pygame.draw.line(screen, BLACK, (0, 300), (SCREEN_WIDTH , 300))


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


    def update(self):
        self.update_animation()
        self.checar_seEstaVivo()
        # update cooldown
        if self.tiro_cooldown > 0:
            self.tiro_cooldown -= 1


    def mover(self, moving_left, moving_right):
        # resetar as variaveis de movimento
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
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.no_ar = False

        # atualizando a posicao retangulo
        self.rect.x += dx
        self.rect.y += dy


    def atirar(self):
        if not self.no_ar:
            if self.tiro_cooldown == 0 and self.municao > 0:
                self.tiro_cooldown = 70
                tiro = Bullet(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction), self.rect.centery,
                          self.direction)

                bullet_group.add(tiro)

    def ia(self):
        if self.vivo and heroi.vivo:
            if self.parado == False and random.randint(1, 200) == 1:
                self.update_action(0) #0: parado
                self.parado = True
                self.parado_count = 50
            #checar se a IA ta perto do heroi
            if self.visao.colliderect(heroi.rect):
                # Para de andar e olha pro heroi
                self.update_action(0)#0: parado
                self.atirar()
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

'''
class Mundo():
    def __init__(self):
        self.lista_obstaculos = []


    def process_data(self, data):
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
                    if tile >= 0 and tile <= 8:
                        self.lista_obstaculos.append(tile_data)

                    #criar os obstaculos que matam o personagem
                    #9 a 10
                    elif tile >= 9 and tile <= 10:
                        agua = Agua(img, x * TILE_SIZE, y * TILE_SIZE)
                        agua_group.add(agua)

                    #criar a decoração do cenário
                    #11 a 14
                    elif tile >= 11 and tile <= 14:
                        decoracao = Decoracao(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoracao_group.add(decoracao)

                    #criar heroi
                    #15
                    elif tile == 15:
                        heroi = Personagens('Heroi', x * TILE_SIZE, y * TILE_SIZE, 0.7, 5, 20, 5)

                    #criar inimigos
                    #16
                    elif tile == 16:
                        inimigo = Personagens('Goblin', x * TILE_SIZE, y * TILE_SIZE, 0.9, 3, 20, 2)
                        inimigo_group.add(inimigo)

                    #criar moedas
                    #17
                    elif tile == 17:
                        item_coletavel = Coletaveis('moeda',x * TILE_SIZE, y * TILE_SIZE)
                        item_coletavel_group.add(item_coletavel)

                    #criar vida
                    #18
                    elif tile == 18:
                        item_coletavel = Coletaveis('coracao', x * TILE_SIZE, y * TILE_SIZE)
                        item_coletavel_group.add(item_coletavel)

                    #criar saida
                    #20
                    elif tile == 20:
                        saida = Saida(img, x * TILE_SIZE, y * TILE_SIZE)
                        saida_group.add(saida)

        return heroi


    def draw(self):
        for tile in self.lista_obstaculos:
            screen.blit(tile[0], tile[1])


class Decoracao(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y * (TILE_SIZE - self.image.get_height()))


class Agua(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y * (TILE_SIZE - self.image.get_height()))



class Saida(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y * (TILE_SIZE - self.image.get_height()))

'''
class Coletaveis(pygame.sprite.Sprite):
    def __init__(self, item_tipo, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_tipo = item_tipo
        self.image = item_coletavel[self.item_tipo]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


    def update(self):
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
        self.rect.x += (self.direction * self.velocidade)

        # checar se a bala saiu da tela
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
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
                    inimigo.vida -= 3
                    heroi.pontos += 15
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
        self.direction = direction

    def update(self):
        self.vel_y += GRAVIDADE
        dx = self.direction * self.velocidade
        dy = self.vel_y

        #checar colisão
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.velocidade = 0

        #checar se a bomba vai sair da tela
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.velocidade

        # atualizar posição da granada
        self.rect.x += dx
        self.rect.y += dy

        #timer da explosao
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosao = Explosao(self.rect.x, self.rect.y, 0.5)
            explosao_group.add(explosao)

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


# criar grupos de sprite
inimigo_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
bomba_group = pygame.sprite.Group()
explosao_group = pygame.sprite.Group()
item_coletavel_group = pygame.sprite.Group()
decoracao_group = pygame.sprite.Group()
agua_group = pygame.sprite.Group()
saida_group = pygame.sprite.Group()


#Temporario - criar itens coletaveis
item_coletavel2 = Coletaveis('moeda', 300, 260)
item_coletavel_group.add(item_coletavel2)

item_coletavel = Coletaveis('coracao', 100, 260)
item_coletavel_group.add(item_coletavel)

heroi = Personagens('Heroi', 200, 200, 0.7, 5, 20, 5)
inimigo = Personagens('Goblin', 200, 200, 0.9, 3, 20, 2)
inimigo2 = Personagens('Goblin', 300, 200, 0.9, 3, 20, 2)

inimigo_group.add(inimigo)
inimigo_group.add(inimigo2)

'''
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


'''

run = True
while run:

    clock.tick(FPS)

    desenhar_bg()

    #desenhar mundo
   # mundo.draw()

    #mostrar vida
    desenhar_texto(f'VIDA:', fonte, WHITE, 10, 35)
    for y in range(heroi.max_vida):
        screen.blit(coracao_sem_vida_img, (70 + (y * 40), 30))

    for x in range(heroi.vida):
        screen.blit(coracao_img, (70 + (x * 40), 30))

    #mostrar pontos
    desenhar_texto(f'{heroi.pontos}', fonte, WHITE, 750, 35)
    #screen.blit(moeda_img, 720, 35)

    heroi.update()
    heroi.desenhar()

    for inimigo in inimigo_group:
        inimigo.ia()
        inimigo.update()
        inimigo.desenhar()

    # update e desenhar grupos
    bullet_group.update()
    bomba_group.update()
    explosao_group.update()
    item_coletavel_group.update()
    #decoracao_group.update()
    #agua_group.update()
    #saida_group.update()

    bullet_group.draw(screen)
    bomba_group.draw(screen)
    explosao_group.draw(screen)
    item_coletavel_group.draw(screen)
    #decoracao_group.draw(screen)
    #agua_group.draw(screen)
    #saida_group.draw(screen)

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
        heroi.mover(moving_left, moving_right)

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
            if event.key == pygame.K_ESCAPE:
                run = False

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
