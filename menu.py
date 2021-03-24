from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *


janela = Window(900,506)
janela.set_title("Colorblind Quest")
teclado = Window.get_keyboard()
mouse = Window.get_mouse()


#Definição de Fundo
fundo = GameImage("fundom.jpg.png")
fundonuvem=Sprite("fundonuvem.png",1)
fundonuvem2=Sprite("fundonuvem.png",1)

Jogar = Sprite("play.png",1)
Opcoes = Sprite("options.png",1)
Volume = Sprite("semsom.png",1)
Volume2=Sprite("comsom.png",1)
Guia=Sprite("guia.png")
Sair=Sprite("exit.png",1)


#Atributos
Jogar.x = janela.width/2 -120
Jogar.y = (janela.height/2)*(1/6)
Opcoes.x = janela.width/2 -120
Opcoes.y = (janela.height/2)*(5/6)
Sair.x = janela.width/2 -120
Sair.y = (janela.height/2) *(3/2)
Volume.y = janela.height/2 -190
Volume.x = janela.width/2 -120
Volume2.y = janela.height/2 -190
Volume2.x = janela.width/2 -120
Guia.x = janela.width/2-120
Guia.y = janela.height/2
fundonuvem.speed=100

#variaveis globais
estado=1
som=1
def opcoes ():
    global estado
    global som
    Guia.draw()
    if (som==1):
        Volume2.draw()
    if (som==0):
        Volume.draw()


    if (teclado.key_pressed("1")):
        if (som==0):
            som=1
        elif (som==1):
            som=0
    if (teclado.key_pressed("3")):
        janela.close()


def menu():
    global estado

    Jogar.draw()
    Opcoes.draw()
    Sair.draw()

    if (teclado.key_pressed("1")):
        estado=0

    if (teclado.key_pressed("2")):
        estado=2

    if (teclado.key_pressed("3")):
        janela.close()

while (True):
    #desenho
    fundonuvem.draw()
    fundo.draw()


    if (estado==0):
        janela.set_background_color((0, 0, 0))
        if (teclado.key_pressed("escape")):
            estado = 1

    if (estado==2):
        fundonuvem.draw()
        fundo.draw()
        opcoes()
        if (teclado.key_pressed("escape")):
            estado = 1

    if (estado == 1):
        menu()
    janela.update()