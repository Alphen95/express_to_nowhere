#тестирование сетки

win_size = (800,600)
import pygame as pg
import threading
import random
import json
import internal_system

pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(win_size, pg.SRCALPHA)
font = pg.font.Font("res/font.ttf",16)

pg.mixer.init(44100, -16, 2, 1024)
pg.mixer.set_num_channels(128)

with open("elements.json", encoding="utf-8") as f:
    info = json.loads(f.read())

working = True


syst = internal_system.InternalSystem(
    wire_amt = 30, 
    obj_list = info["elements"],
    ns = (10,6), 
    ds = (10,7), 
    tls = 64,
    tt = info["text_lines"], font=font
)

params = {
    "km":["res/controls.png", [96,0,20,10]],
    "tk":["res/controls.png", [96,10,20,10]],
    "box":["res/controls.png", [0,0,96,45]],
}

syst.add_sprites("res/electrical_tiles.png", params)

syst.add("dpt-7",[0,0])
syst.add("dpt-7",[3,0])
syst.add("dpt-7",[0,2])
syst.add("dpt-7",[3,2])
syst.add("grk-14",[7,0])
syst.add("yas-7",[7,3])
syst.add("lk-2")
syst.add("gr-3")
syst.add("gr-3")
syst.add("gr-3")
syst.add("gr-3")
syst.add("gr-3")
syst.add("gr-3")
syst.add("rt-5")
syst.add("ep-1")
syst.add("akb-3")

m_dx, m_dy = 0,0
m_pos = pg.mouse.get_pos()

syst.load([['el_motor', [0, 0, 3, 2], [], [], 'dpt-7', [0.4, 14]], ['el_motor', [3, 0, 3, 2], [], [], 'dpt-7', [0.4, 14]], ['el_motor', [0, 2, 3, 2], [], [], 'dpt-7', [0.4, 14]], ['el_motor', [3, 2, 3, 2], [], [], 'dpt-7', [0.4, 14]], ['group_cn', [6, 0, 2, 3], [20, 1], [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 0, 0, 0, 0, 0, 0, 0, 0], 'grk-14', [14, [0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]]], ['resistor', [6, 3, 2, 2], [12, 13, 14, 15, 16, 17, 18], [], 'yas-7', [4, [100, 84, 66, 50, 33, 16, 0]]], ['hv_relay', [0, 4, 2, 1], [7], [], 'lk-2', []], ['gr_relay', [2, 4, 2, 1], [2, 3, 4], [7], 'gr-3', [1]], ['gr_relay', [4, 4, 2, 1], [5, 0, 0], [7], 'gr-3', [1]], ['gr_relay', [0, 5, 2, 1], [2, 6, 8], [20], 'gr-3', [0]], ['gr_relay', [2, 5, 2, 1], [3, 6, 9], [20], 'gr-3', [0]], ['gr_relay', [4, 5, 2, 1], [4, 6, 10], [20], 'gr-3', [0]], ['gr_relay', [6, 5, 2, 1], [5, 6, 11], [20], 'gr-3', [0]], ['cu_relay', [8, 0, 1, 1], [], [6], 'rt-5', [0, 200]], ['elswitch', [9, 0, 1, 1], [], [1], 'ep-1', []], ['akumbatt', [8, 1, 2, 2], [], [], 'akb-3', []], ['combiner', [8, 3, 2, 2], [19, 0], [], 'kd-30', []]])
syst.add("akb-3")
syst.add("kd-30")
syst.dumb = True

while working:
    dt = 2/max(1,clock.get_fps())
    clicked=False
    released=False
    pressed = pg.key.get_pressed()
    keydowns = []
    for evt in pg.event.get():
        if evt.type == pg.QUIT: working = False
        elif evt.type == pg.KEYDOWN:
            if evt.key == pg.K_d:
                print(syst.dump())
            keydowns.append(evt.key)
        elif evt.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]: clicked = True
        elif evt.type == pg.MOUSEBUTTONUP: released = True

    m_pos = pg.mouse.get_pos()

    screen.fill((30,30,30))

    pdc = (10,10)
    syst.render_graphics(screen,win_size,"oleg",keydowns, pressed,[pg.mouse.get_pos(), pg.mouse.get_pressed(), clicked, released]),(0,0)

    syst.axial_speed = max(0, syst.axial_speed/3.5+syst.torque*3.5*dt/134000)*3.5
    z = [
        f"Rб: {syst.total_resistance} Ом",
        f"цепь: {'собрана' if syst.high_voltage else 'разобрана'}",
        f"угловая: {round(syst.axial_speed,2)} рад/с",
        f"линейка: {round(syst.axial_speed*70/29*0.51*3.6,2)} км/ч",
        f"ток: {round(syst.current,2)} А",
        f"км: {syst.km['pos']} позиция",
        f"подключение: {syst.connection_mode}",
    ]
    for enum, line in enumerate(z):
        ptext = font.render(line,True,(240,240,240),(30,30,30))
        screen.blit(ptext,(20,20+16*enum))

    pg.display.update()

    clock.tick(120)

print(syst.dump())
syst.working = False
pg.quit()
