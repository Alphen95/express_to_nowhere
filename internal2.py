import pygame as pg
import threading

#internal system v2
win_size = (800,600)

pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(win_size, pg.SRCALPHA | pg.HWSURFACE) #| pg.FULLSCREEN)
font = pg.font.Font("res/font.ttf",20)

class Internal():

    def __init__(self):
        self.network_voltage = 1500

        self.



working = True

while working:
    clicked = False
    released = False
    pressed = []

    for evt in pg.event.get():
        if evt.type == pg.QUIT:
            working = False
        elif evt.type == pg.KEYDOWN:
            pressed.append(evt.key)
        elif evt.type == pg.MOUSEBUTTONDOWN:
            clicked = True
        elif evt.type == pg.MOUSEBUTTONUP:
            released = True
    m_pos = pg.mouse.get_pos()
    m_btn = pg.mouse.get_pressed()

    pg.display.update()
    clock.tick(60)

pg.quit()
