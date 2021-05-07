import pygame
from constants import TILE_SIZE, PATH_CORACAO, PATH_MOEDA


class GenericObject(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self, screen_scroll):
        self.rect.x += screen_scroll



class ColetaveisGroup(pygame.sprite.Group):
    def __int__(self):
        pass

    def update(self, screen_scroll, heroi, menu, coracao_fx, moeda_fx):
        temp_vida2 = 0
        temp_point2 = 0
        for i in self.sprites():
            temp_vida, temp_point = i.update(screen_scroll, heroi, menu, coracao_fx, moeda_fx)
            temp_vida2 += temp_vida
            temp_point2 += temp_point

        return temp_vida2, temp_point2


class Coletaveis(pygame.sprite.Sprite):
    def __init__(self, item_tipo, x, y):
        coracao_img = pygame.image.load(PATH_CORACAO).convert_alpha()
        moeda_img = pygame.image.load(PATH_MOEDA).convert_alpha()

        pygame.sprite.Sprite.__init__(self)
        item_coletavel = {
            'coracao': coracao_img,
            'moeda': moeda_img
        }
        self.item_tipo = item_tipo
        self.image = item_coletavel[self.item_tipo]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self, screen_scroll, heroi, menu, coracao_fx, moeda_fx):
        temp_vida = 0
        temp_point = 0
        #scroll
        self.rect.x += screen_scroll
        #checar se o jogador pegou a caixa
        if pygame.sprite.collide_rect(self, heroi):
            #checar qual tipo de colecionável
            if self.item_tipo == 'coracao':
                temp_vida += 1
                if menu.som == 1:
                    coracao_fx.play()

                if heroi.vida > heroi.max_vida:
                    heroi.vida = heroi.max_vida


            elif self.item_tipo == 'moeda':
                temp_point += 50
            self.kill()

            if menu.som == 1:
                moeda_fx.play()
        return temp_vida, temp_point
