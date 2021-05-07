import pygame


class DamageText(pygame.sprite.Sprite):
    def __init__(self,x,y,damage,colour, font):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage,True,colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0

    def update(self):
        #move o texto do dano
        self.rect.y -= 1
        #apaga o texto depois de alguns segundos
        self.counter += 1
        if self.counter > 30:
            self.kill()
