import pygame
from pygame import mixer
import random
import os
from constants import *
import menu
from models.Text import DamageText

pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()
fps = 60
bottom_panel = 150
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Colorblind Quest")

#definir variáveis do game
current_fighter = 1
total_fighters = 2
action_cooldown = 0
action_wait_time = 90
attack = False
potion = False
potion_effect = 50
clicked = False
effect = False
game_over = 0
cont = 0

pygame.mixer.music.load(PATH_MUSICA_FX)
pygame.mixer.music.play(-1, 0.0, 2000)
pygame.mixer.music.set_volume(0.5)
ataque_fx = pygame.mixer.Sound(PATH_ATAQUE1_DRAGAO_FX)
ataque2_fx = pygame.mixer.Sound(PATH_ATAQUE2_DRAGAO_FX)
ataque_heroi_fx = pygame.mixer.Sound(PATH_ATAQUE_HBOSS_FX)
pocao_fx = pygame.mixer.Sound(PATH_JUMP_FX)

#definir fontes
font = pygame.font.SysFont('Arial', 24, bold=False, italic=False)

#definir cores
red = (255, 0, 0)
green = (0, 255, 0)

# Carregar imagens
background_image=pygame.image.load(PATH_BACKGROUND_FINAL).convert_alpha()

#painel
painel_image=pygame.image.load(PATH_CENARIO_PAINEL).convert_alpha()

#imagens de poções
potion_img = pygame.image.load(PATH_MOEDA).convert_alpha()

#Imagens de vitória e derrota
victory_img=pygame.image.load(PATH_MENU_WIN).convert_alpha()
defeat_img=pygame.image.load(PATH_MENU_LOSE).convert_alpha()

#desenhar texto
def draw_text(text, font,text_color,x,y):
    image=font.render(text,True,text_color)
    screen.blit(image,(x,y))

#Função para desenhar background
def draw():
    screen.blit(background_image,(0,0))

#Função para desenhar o painel
def painel():
    screen.blit(painel_image,(-70,SCREEN_HEIGHT-bottom_panel))
    #mostrar status do dragão
    draw_text(f'{"O grande dragão"} HP:{Dragao.hp}',font,red,440,SCREEN_HEIGHT-bottom_panel+10)
    #mostrar status do heroi
    draw_text(f'{"Herói"} HP:{Heroi.hp}', font, red, 100, SCREEN_HEIGHT - bottom_panel + 10)

#Função para atualizar música
def update_musica():
    if (menu.som == 0):
        pygame.mixer.music.set_volume(0)
    elif (menu.som==1):
        pygame.mixer.music.set_volume(0.5)

#Função para batalhar
class Boss():

    def __init__(self,x,y,name,max_hp,strength,potions,scale):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.potions = potions
        self.alive = True
        self.animations_list=[]
        self.frame_index = 0
        self.action=0 #0: parado, 1: ataque, 2: ferido, 3:morto; 4:ataque2
        self.update_time=pygame.time.get_ticks()

        #Carregar imagens parado
        temp_list=[]
        for i in range (6):
            image = pygame.image.load(f'sprites/{self.name}/luta/{i}.png')
            image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
            temp_list.append(image)
        self.animations_list.append(temp_list)

        #Carregar imagens para ataque
        temp_list = []
        for i in range(3):
            image = pygame.image.load(f'sprites/{self.name}/ataque/{i}.png')
            image = pygame.transform.scale(image, (image.get_width()*scale, image.get_height()*scale))
            temp_list.append(image)
        self.animations_list.append(temp_list)

        # Carregar imagens para ferida
        temp_list = []
        for i in range(5):
            image = pygame.image.load(f'sprites/{self.name}/ferido/{i}.png')
            image = pygame.transform.scale(image, (image.get_width()*scale, image.get_height()*scale))
            temp_list.append(image)
        self.animations_list.append(temp_list)

        # Carregar imagens para morto
        temp_list = []
        for i in range(5):
            image = pygame.image.load(f'sprites/{self.name}/morto/{i}.png')
            image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
            temp_list.append(image)
        self.animations_list.append(temp_list)

        # Carregar imagens para o segundo ataque do dragão
        temp_list = []
        for i in range(9):
            image = pygame.image.load(f'sprites/dragao/master/{i}.png')
            image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
            temp_list.append(image)
        self.animations_list.append(temp_list)

        self.image=self.animations_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def update(self):
        animation_cooldown = 100

        #handle animation
        #update imagem
        self.image = self.animations_list[self.action][self.frame_index]

        #Conferir o tempo para realizar o próximo update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        #Resetar animação, caso a lista tenha acabado
        if self.frame_index >= len(self.animations_list[self.action]):
            self.frame_index = 0
            if self.action == 3:
                self.frame_index = len(self.animations_list[self.action])-1
            else:
                self.iddle()

    def iddle(self):
        # voltar ao estado parado
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack (self, target):
        #dano ao inimigo
        if self.name=="heroi":
            rand=20*(4-self.potions)

        if self.name== "dragao":
            rand= 30

        damage = self.strength + rand
        target.hp -= damage

        # ativer o metodo ferido
        target.hurt()
        #checar se ta vivo
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()

        damage_text = DamageText(target.rect.centerx,target.rect.centery,str(damage),red, font)
        damage_textgroup.add(damage_text)

        #mudar variáveis de ataque
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        if self.name == "dragao":
            if menu.som == 1:
                ataque_fx.play()

        if self.name == "heroi":
            if menu.som == 1:
                ataque_heroi_fx.play()

    def attackM (self, target):

        if self.name == "dragao":
            rand = 60
            cont = 0
            damage = self.strength + rand
            target.hp -= damage

            # ativer o metodo ferido
            target.hurt()
            # checar se ta vivo
            if target.hp < 1:
                target.hp = 0
                target.alive = False
                target.death()

            damage_text = DamageText(target.rect.centerx, target.rect.centery, str(damage), red, font)
            damage_textgroup.add(damage_text)

            # mudar variáveis de ataque
            self.action = 4
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            if (menu.som==1):
                ataque2_fx.play()

    def hurt(self):
        # ferido
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        # morto
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image,self.rect)

class HealthBar():
    def __init__(self,x,y,hp,max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        #update com a vida nova
        self.hp = hp
        #calcula vida restante
        ratio = self.hp/self.max_hp
        pygame.draw.rect(screen,red,(self.x,self.y,150,20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150*ratio, 20))

damage_textgroup = pygame.sprite.Group()

Dragao = Boss(780,300,"dragao",300,10,1,5)
Heroi=Boss(200,370, "heroi",300,6,3,1)

Heroi_health_bar=HealthBar(100, SCREEN_HEIGHT-bottom_panel+40, Heroi.hp,Heroi.max_hp)
Dragao_health_bar=HealthBar(550, SCREEN_HEIGHT-bottom_panel+40, Dragao.hp,Dragao.max_hp)


def boss():
    run = True
    global clicked, game_over, current_fighter, action_cooldown, cont
    global effect
    while run:
        if (game_over!=0):
            menu.draw_menu()
        else:
            clock.tick(fps)
            draw()
            painel()
            Heroi_health_bar.draw(Heroi.hp)
            Dragao_health_bar.draw(Dragao.hp)
            Dragao.update()
            Dragao.draw()
            Heroi.update()
            Heroi.draw()
            update_musica()

            #desenha o texto de dano
            damage_textgroup.update()
            damage_textgroup.draw(screen)

            #controlar ações do player
            #resetar variáveis de ação
            attack = False
            potion = False
            target = None

            if clicked == True and Dragao.alive == True:
                attack = True
                target = Dragao
                clicked = False

            if effect == True:
                potion = True
                if (menu.som == 1):
                    pocao_fx.play()
            #mostrar o número de poções resultantes
            draw_text("Poções restantes: " +str(Heroi.potions),font,red,100,SCREEN_HEIGHT-bottom_panel+70)

            if game_over == 0:
                #ações do player:
                if Heroi.alive == True:
                    if current_fighter == 1:
                        action_cooldown += 1
                        if action_cooldown >= action_wait_time:
                            #olhar para ação do player
                            #ataque
                            if attack == True and target != None:
                                Heroi.attack(Dragao)
                                current_fighter += 1
                                action_cooldown = 0

                            #Poção
                            if potion == True:
                                if Heroi.potions > 0:
                                    #checar se a poção vai dar ao player mais que a vida máxima
                                    if Heroi.max_hp - Heroi.hp > potion_effect:
                                        heal_amount = potion_effect
                                    else:
                                        heal_amount = Heroi.max_hp - Heroi.hp
                                    Heroi.hp += heal_amount
                                    Heroi.potions -= 1
                                    damage_text = DamageText(Heroi.rect.centerx, Heroi.rect.centery, str(heal_amount), green, font)
                                    damage_textgroup.add(damage_text)
                                    current_fighter += 1
                                    action_cooldown = 0
                                    effect = False

                else:
                    game_over = -1
                #ações do Boss:
                if current_fighter == 2:
                    if Dragao.alive == True:
                        action_cooldown += 1
                        if action_cooldown >= action_wait_time:
                            #checar se o Dragão precisa se curar primeiro
                            if (Dragao.hp/Dragao.max_hp) < 0.5 and Dragao.potions>0:
                                if Dragao.max_hp - Dragao.hp > potion_effect:
                                    heal_amount = potion_effect
                                else:
                                    heal_amount = Dragao.max_hp - Dragao.hp
                                Dragao.hp += heal_amount
                                Dragao.potions -= 1
                                damage_text = DamageText(Dragao.rect.centerx, Dragao.rect.centery, str(heal_amount), green, font)
                                damage_textgroup.add(damage_text)
                                current_fighter += 1
                                action_cooldown = 0
                            #ataque
                            else:
                                if (cont == 3):
                                    Dragao.attackM(Heroi)
                                    cont = 1
                                else:
                                    Dragao.attack(Heroi)
                                    cont= cont+1
                                current_fighter += 1
                                action_cooldown = 0

                #Se todos já tiverem seus turnos, reset
                if current_fighter > total_fighters:
                    current_fighter = 1

                #checar se o dragão ta vivo
                if Dragao.alive == False:
                    game_over = 1

            #checar se o jogo acabou
            if game_over != 0:
                if game_over == 1:
                    screen.blit(victory_img,(250,50))

                elif game_over == -1:
                    screen.blit(defeat_img,(250,50))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            #comandos do teclado:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        clicked = True
                    else:
                        clicked = False
                    if event.key == pygame.K_a:
                        effect = True


        pygame.display.update()
    pygame.quit()