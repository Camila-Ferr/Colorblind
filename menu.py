from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *
import os

janela = Window(800, 640)
janela.set_title("Colorblind Quest")
teclado = Window.get_keyboard()
mouse = Window.get_mouse()

#Definição de Fundo
root = os.path.dirname(__file__)
sprite_path = os.path.join(os.path.sep, root, 'sprites')
menu_path = os.path.join(os.path.sep, sprite_path, 'menu')
logo = Sprite(os.path.join(menu_path, 'logo.png'))

fundo = GameImage(os.path.join(menu_path, 'corte.png'))
fundonuvem=Sprite(os.path.join(menu_path, 'backgroundr.png'),1)
Jogar = Sprite(os.path.join(menu_path, 'play.png'),1)
Opcoes = Sprite(os.path.join(menu_path, 'options.png'),1)
Volume = Sprite(os.path.join(menu_path, 'semsom.png'),1)
Volume2=Sprite(os.path.join(menu_path, 'comsom.png'),1)
Guia=Sprite(os.path.join(menu_path, 'guide.png'),1)
Sair=Sprite(os.path.join(menu_path, 'exit.png'),1)
Pergaminho = Sprite(os.path.join(menu_path, 'pergaminho.png'), 1)

#Atributos
Jogar.x = janela.width/2 - 120
Jogar.y = (janela.height/2) * (3/6)
Opcoes.x = janela.width/2 - 120
Opcoes.y = (janela.height/2) * (6/6)
Sair.x = janela.width/2 - 120
Sair.y = (janela.height/2) * (9/6)
Volume.y = janela.height/2 - 150
Volume.x = janela.width/2 - 120
Volume2.y = janela.height/2 - 150
Volume2.x = janela.width/2 - 120
Guia.x = janela.width/2 - 120
Guia.y = janela.height/2 + 100
Pergaminho.x = janela.width/2 - Pergaminho.width/2
Pergaminho.y = janela.height/2 - Pergaminho.height/2
fundonuvem.speed = 100
logo.x = janela.width / 2 - 300
logo.y = (janela.height / 2) - 420
fundo.y = janela.height - 500

#variaveis globais
estado = 1
som = 1
apertarBotao = 0


def opcoes ():
    global estado, apertarBotao
    global som
    Guia.draw()
    logo.draw()
    if (som == 1):
        Volume2.draw()
        pygame.mixer.music.set_volume(0.5)

    if (som == 0):
        Volume.draw()
        pygame.mixer.music.set_volume(0)


    if (mouse.is_over_object(Volume)):
        if mouse.is_button_pressed(1):
            if (som == 0):
                som = 1
            elif (som == 1):
                som = 0

    if mouse.is_over_object(Guia):
        if mouse.is_button_pressed(1):
            apertarBotao = 1

    if apertarBotao == 1:
        Pergaminho.draw()


    if apertarBotao == 1 and teclado.key_pressed("escape"):
        apertarBotao = 0

def menu():
    global estado

    Jogar.draw()
    Opcoes.draw()
    Sair.draw()

    if mouse.is_over_object(Jogar):
        if mouse.is_button_pressed(1):
            estado=0


    elif mouse.is_over_object(Opcoes):
        if mouse.is_button_pressed(1):
            estado=2

    elif mouse.is_over_object(Sair):
        if mouse.is_button_pressed(1):
            janela.close()


def draw_menu():
    global estado
    global som
    #desenho
    fundonuvem.draw()
    fundo.draw()
    logo.draw()

    if (estado == 0):
        estado = 1
        if (teclado.key_pressed("escape")):
            estado = 1

    elif (estado == 2):
        fundonuvem.draw()
        fundo.draw()
        opcoes()
        if (apertarBotao == 0 and teclado.key_pressed("escape")):
            estado = 1

    elif (estado == 1):
        menu()
    janela.update()