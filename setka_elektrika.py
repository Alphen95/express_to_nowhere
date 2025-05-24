#тестирование сетки

win_size = (800,600)
import pygame as pg
import threading
import random
import json
import electrical_system

pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(win_size, pg.SRCALPHA)
font = pg.font.Font("res/font.ttf",16)

pg.mixer.init(44100, -16, 2, 1024)
pg.mixer.set_num_channels(128)

with open("elements.json") as f:
    info = json.loads(f.read())

working = True

text_lines = {
    "names":{
        "gr-3":"ГР-3 (групповое реле)",
        "gr-2":"ГР-2 (групповое реле)",
        "dr-2":"ДР-1 (двойное реле)",
        "lk-2":"ЛК-2 (линейный контактор)",
        "rt-5":"РТ-5 (реле тока)",

        "akb-3":"АКБ-3 (батарея)",

        "ls-4":"ЛС-4Ж (лампа сигнальная)",
        "ep-1":"ЭП-1 (переключатель)",

        "grk-8":"ГрК-8 (груп. контроллер)",
        "grk-14":"ГрК-14 (груп. контроллер)",

        "yas-7":"ЯС-7 (ящик сопротивлений)",
        "yas-12":"ЯС-12 (ящик сопротивлений)",
        
        "dpt-7":"ДПт-7 (тяговый двигатель)",
    },
    "inputs": "Подключения (+):",
    "outputs": "Подключения (-):",
    "group_controller": "Вал в {} позиции",
    "engine": "{} А на контактах",
    "active": "Контакты: замкнуты",
    "inactive": "Контакты: разомкнуты",
    "type": "Тип:",
    "relay_0": "AND",
    "relay_1": "OR",
    "max": "максимальное",
    "min": "минимальное",
    "res_percent": "Процент сопротивления:",
    "res_max": "Макс. сопротивление",
    "ohm": "Ом",
    "type": "Тип:",
    "contact": "Контактор #",
    "pos": "Позиция вала",
    "peril_current": "Пороговый ток:",
}

syst = electrical_system.ElectricalSystem(
    wire_amt = 30, 
    obj_list = info["elements"],
    ns = (9,6), 
    ds = (12,9), 
    tls = 64,
    tt = text_lines, font=font
)

params = {
    "km":["res/kofemolka_ruchka.png", [0,0,31,9,8]],
    "km_box":["res/kofemolka.png", [0,0,32,64]],
}

syst.add_sprites("res/electrical_tiles.png", params)

syst.add("dpt-7",[0,0])
syst.add("dpt-7",[3,0])
syst.add("dpt-7",[0,2])
syst.add("dpt-7",[3,2])
syst.add("grk-8",[7,0])
syst.add("yas-7",[7,2])
syst.add("lk-2")
syst.add("gr-3")
syst.add("gr-3")
syst.add("rt-5")
syst.add("ep-1")
syst.add("ep-1")
syst.add("ep-1")
syst.add("akb-3")

m_dx, m_dy = 0,0
m_pos = pg.mouse.get_pos()

syst.load([['el_motor', [0, 0, 3, 2], [], [], 'dpt-7', [0.4, 7]], ['el_motor', [3, 0, 3, 2], [], [], 'dpt-7', [0.4, 7]], ['el_motor', [0, 2, 3, 2], [], [], 'dpt-7', [0.4, 7]], ['el_motor', [3, 2, 3, 2], [], [], 'dpt-7', [0.4, 7]], ['group_cn', [7, 0, 2, 2], [20, 3], [10, 11, 12, 13, 14, 15, 16, 0, 18, 19], 'grk-8', [8, [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 1, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 1, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 1, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 1, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 1, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]], ['resistor', [7, 2, 2, 2], [10, 11, 12, 13, 14, 15, 16], [], 'yas-7', [4, [86, 71, 57, 43, 29, 14, 0]]], ['hv_relay', [2, 5, 2, 1], [17], [], 'lk-2', []], ['gr_relay', [0, 5, 2, 1], [1, 18, 4], [20], 'gr-3', [0]], ['gr_relay', [0, 4, 2, 1], [2, 19, 4], [20], 'gr-3', [0]], ['cu_relay', [4, 4, 1, 1], [], [4], 'rt-5', [0, 230]], ['elswitch', [5, 4, 1, 1], [], [3], 'ep-1', []], ['elswitch', [5, 5, 1, 1], [], [2], 'ep-1', []], ['elswitch', [4, 5, 1, 1], [], [1], 'ep-1', []], ['akumbatt', [7, 4, 2, 2], [], [], 'akb-3', []], ['gr_relay', [2, 4, 2, 1], [1, 2, 0], [17], 'gr-3', [1]]])

while working:
    dt = 2/max(1,clock.get_fps())
    clicked=False
    pressed = pg.key.get_pressed()
    keydowns = []
    for evt in pg.event.get():
        if evt.type == pg.QUIT: working = False
        elif evt.type == pg.KEYDOWN:
            if evt.key == pg.K_d:
                print(syst.dump())
            keydowns.append(evt.key)
        elif evt.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]: clicked = True

    m_pos = pg.mouse.get_pos()

    screen.fill((30,30,30))

    pdc = (10,10)
    screen.blit(syst.render_graphics(win_size,pdc,keydowns, pressed,[m_pos, pg.mouse.get_pressed(), clicked]),(0,0))

    syst.axial_speed = max(0, syst.axial_speed/3.5+syst.torque*3.5*dt/134000)*3.5
    z = [
        f"Rб: {syst.total_resistance} Ом",
        f"цепь: {'собрана' if syst.high_voltage else 'разобрана'}",
        f"угловая: {round(syst.axial_speed,2)} рад/с",
        f"ток: {round(syst.current,2)} А",
        f"км: {syst.km['pos']} позиция",
    ]
    for enum, line in enumerate(z):
        ptext = font.render(line,True,(240,240,240),(30,30,30))
        screen.blit(ptext,(20,20+16*enum))

    pg.display.update()

    clock.tick(120)

syst.working = False
pg.quit()
