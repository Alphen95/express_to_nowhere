#EXP TO:[Nowhere] VIA:[Shugurovka]

import pygame as pg
import os
import time
import random
import isometry
import rails
import train

win_size = (0,0)
version = "0.1 testificate"


pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(win_size, pg.SRCALPHA)
font = pg.font.Font("res/font.ttf",20)

win_size = screen.get_size()
win_size = (win_size[0]+100,win_size[1]+100)

working = True

tile_sheet = pg.image.load("res/tiles.png")
el_s_sheet = pg.image.load("res/el_s.png")
el_sp_sheet = pg.image.load("res/el_sp.png")

player = isometry.Camera(win_size)
player.sprites["millimetrovka"] = player.render_tile(tile_sheet.subsurface(0,0,64,64),(1,0,2))
player.sprites["house_absc_a"] = player.render_tile(tile_sheet.subsurface(0,64,5120,64),(80,0,2))
player.sprites["house_absc_b"] = player.render_tile(tile_sheet.subsurface(0,128,5120,64),(80,0,2))
player.sprites["house_absc_c"] = player.render_tile(tile_sheet.subsurface(0,192,5120,64),(80,0,2))

player.train_sprites["Sv_p"] = player.render_train(el_s_sheet,((32,98),28 ,2))
player.train_sprites["Sv_m"] = player.render_train(el_sp_sheet,((32,98),32 ,2))

player.blockmap["-15:-1"] = ["house_absc_a"]
player.blockmap["-14:-1"] = ["house_absc_b"]
player.blockmap["-13:-1"] = ["house_absc_c"]
player.blockmap["-12:-3"] = ["house_absc_a"]
player.blockmap["-11:-3"] = ["house_absc_b"]
player.blockmap["-10:-3"] = ["house_absc_c"]
rail_nodes = {
    "-25:-2":[[],[111]],
    "-20:-2":[[111],[100]],
    "-10:-2":[[100],[101,102]],
    "-10:-1":[[],[103]],
    "-5:-2":[[101],[104]],
    "-5:-1":[[102,103],[105,106]],
    "0:-1":[[105],[107]],
    "0:0":[[106],[108]],
    "5:-1":[[107],[]],
    "5:0":[[108],[109]],
    "15:-15":[[104],[110]],
    "8:0":[[109],[]],
    "20:-15":[[110],[]]
}

switches = {
    "-10:-2":[[],[101]],
    "-5:-1":[[103],[105]],
}
'''
rail_nodes = {
    "-20:2":[[],[99]],
    "-17:2":[[99],[100]],
    "0:-2":[[100],[101]],
    "30:-2":[[101],[]]
}
'''
tracks = {}

for node in rail_nodes:
    sx, sy = [(i+0.5)*256 for i in map(int,node.split(":"))]
    for rail_id in rail_nodes[node][0]:
        if rail_id not in tracks: tracks[rail_id] = rails.Rail(rail_id)
        tracks[rail_id].pos_a = (sx,sy)
    for rail_id in rail_nodes[node][1]:
        if rail_id not in tracks: tracks[rail_id] = rails.Rail(rail_id)
        tracks[rail_id].pos_b = (sx,sy)

for rail_id in tracks:
    tracks[rail_id].build()

train.tracks = tracks
train.nodes = rail_nodes
train.switches = switches

consists = []
consists.append(train.Consist(
    [(-16)*256,-1.5*256],["Sv_p","Sv_m","Sv_p"], 100, 392, font
))
consists[-1].velocity_vector = -1

player.scale = 1

track_edges = {111:["up",(-25,-2),False]}
max_track_id = 111
generation_params = {
    "dx":[7,14],
    "max_dy":[0,3],
    "repeat_bezier":False
}

class Dummy:
    def __init__(self,pos,angle,type):
        self.pos = (pos[0],pos[1])
        self.angle = angle
        self.type = type

while working:
    train.switches = switches
    clicked = False
    pressed = []

    for evt in pg.event.get():
        if evt.type == pg.QUIT:
            working = False
        elif evt.type == pg.KEYDOWN:
            pressed.append(evt.key)

            if evt.key == pg.K_d: player.debug = not player.debug
            elif evt.key == pg.K_EQUALS: player.scale += 0.5
            elif evt.key == pg.K_MINUS: player.scale /= 2

            if evt.key == pg.K_s: consists[-1].velocity = 0
        elif evt.type == pg.MOUSEBUTTONDOWN:
            clicked = True

    screen.fill((0,0,0))

    temp_trains = []
    occupied_tracks = []
    for c in consists:
        for tr in c.trains:
            temp_trains.append(Dummy(tr.pos,tr.angle+tr.flipped*180,tr.type))
            occupied_tracks.append(tr.occupied_tracks[0])
            occupied_tracks.append(tr.occupied_tracks[1])

    player.pos = temp_trains[0].pos
    disp = player.draw_map(temp_trains,font)
    screen.blit(disp,(screen.get_width()/2-disp.get_width()/2,screen.get_height()/2-disp.get_height()/2))

    to_generate = []
    for oc_t in occupied_tracks:
        if oc_t not in to_generate and oc_t in track_edges:
            to_generate.append(oc_t)

    for oc_t in to_generate:
        params = track_edges[oc_t]
        dx = random.randint(generation_params["dx"][0],generation_params["dx"][1])*(-1 if params[0] == "up" else 1)
        if not params[2] or generation_params["repeat_bezier"]:
            if len(generation_params["max_dy"]) == 1:
                z = int(abs(dx/generation_params["max_dy"][0]))
                if z > 0: dy = int(random.randint(0,z))*(1-random.randint(0,1)*2)
                else: dy = 0
            else:
                dy = int(random.randint(generation_params["max_dy"][0],generation_params["max_dy"][1]))*(1-random.randint(0,1)*2)
        else:
            dy = 0
        new_pos = (params[1][0]+dx, params[1][1]+dy)

        max_track_id+=1
        tracks[max_track_id] = rails.Rail(max_track_id)
        tracks[max_track_id].pos_a = [i*256+128 for i in new_pos]
        tracks[max_track_id].pos_b = [i*256+128 for i in params[1]]
        tracks[max_track_id].build()

        if params[0] == "up":
            rail_nodes[f"{params[1][0]}:{params[1][1]}"][0].append(max_track_id)
            rail_nodes[f"{new_pos[0]}:{new_pos[1]}"] = [[],[max_track_id]]
        else:
            rail_nodes[f"{params[1][0]}:{params[1][1]}"][1].append(max_track_id)
            rail_nodes[f"{new_pos[0]}:{new_pos[1]}"] = [[max_track_id],[]]

        track_edges[max_track_id] = (params[0],new_pos, dy != 0)
        track_edges.pop(max_track_id-1)


    player.rail_nodes = rail_nodes
    player.tracks = tracks
    train.tracks = tracks
    train.nodes = rail_nodes
    train.switches = switches

    if pg.mouse.get_pressed()[0]: print(player.translate_from(pg.mouse.get_pos()))

    kbd = pg.key.get_pressed()

    screen.blit(consists[-1].electrical_system.render_graphics([i-100 for i in win_size], "look here! a stroka!", pressed, kbd, [pg.mouse.get_pos(), pg.mouse.get_pressed(), clicked]),(0,0))

    fps = round(clock.get_fps())
    speed = 16
    '''
    if kbd[pg.K_DOWN]: 
        consists[-1].velocity_vector = 1

        player.pos[0] += speed
        player.pos[1] += speed
    elif kbd[pg.K_UP]: 
        consists[-1].velocity_vector = -1

        player.pos[0] -= speed
        player.pos[1] -= speed
    else:
        #trains[-1].velocity = 0
        consists[-1].velocity_vector = 0
        
    if kbd[pg.K_RIGHT]: 
        player.pos[0] += speed
        player.pos[1] -= speed
    if kbd[pg.K_LEFT]: 
        player.pos[0] -= speed
        player.pos[1] += speed'''


    if kbd[pg.K_LALT]:
        switches = {
            "-10:-2":[[],[102]],
            "-5:-1":[[102],[106]],
        }
    else:
        switches = {
            "-10:-2":[[],[101]],
            "-5:-1":[[103],[105]],
        }

    #player.pos = [round(i) for i in player.pos]
    z = [version,f"pos: {player.pos}",f"fps: {fps}",f"active rail {occupied_tracks[0]}",f"speed: {round(consists[-1].pixel_velocity,2)} px/s",f"speed: {round(consists[-1].velocity*3.6,2)} km/h",f"acceleration: {round(consists[-1].acceleration,2)} m/s^2"]
    for enum, line in enumerate(z):
        ptext = font.render(line,True,(240,240,240),(0,0,0))
        screen.blit(ptext,(20,20+30*enum))

    ptext = font.render(f"alt {'pressed' if kbd[pg.K_LALT] else 'released'}",True,(240,240,240),(84,109,255) if kbd[pg.K_LALT] else(0,0,0))
    screen.blit(ptext,(20,20+30*len(z)))

    #ptext = font.render(f"а приборки-то нема",True,(240,240,240),(255,50,50))
    #screen.blit(ptext,(screen.get_width()-20-ptext.get_width(),screen.get_height()-20-ptext.get_height()))

    pg.display.update()
    clock.tick(60)

pg.quit()
for tr in consists:
    tr.is_alive = False