#EXP TO:[Nowhere] VIA:[Shugurovka]

import pygame as pg
import os
import time
import random
import isometry
import rails
import rails2d
import train

win_size = (0,0)
version = "0.2 2d space"


pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(win_size, pg.SRCALPHA | pg.HWSURFACE)# | pg.FULLSCREEN)
font = pg.font.Font("res/font.ttf",20)

win_size = screen.get_size()
win_size = (win_size[0]+100,win_size[1]+100)

working = True

tile_sheet = pg.image.load("res/tiles.png")
el_s_sheet = pg.image.load("res/el_s.png")
el_sp_sheet = pg.image.load("res/el_sp.png")

player = isometry.Camera(win_size)
player.sprites["millimetrovka"] = player.render_tile(tile_sheet.subsurface(0,0,32,32),(1,0,4))
player.sprites["house_absc_a"] = player.render_tile(tile_sheet.subsurface(0,32,1280,32),(40,0,4))
player.sprites["house_absc_b"] = player.render_tile(tile_sheet.subsurface(0,64,1280,32),(40,0,4))
player.sprites["house_absc_c"] = player.render_tile(tile_sheet.subsurface(0,96,1280,32),(40,0,4))
player.sprites["rock"] = player.render_tile(tile_sheet.subsurface(0,128,1280,32),(32,0,4))

player.train_sprites["Sv_p"] = player.render_train(el_s_sheet,((32,98),28 ,2))
player.train_sprites["Sv_m"] = player.render_train(el_sp_sheet,((32,98),32 ,2))

player.blockmap["-20:-1"] = ["rock"]


'''

rail_nodes = {
    "-5:20":{
        "x":[[101],[102]],
        "y":[[],[]]
    },
    "-10:15":{
        "x":[[],[]],
        "y":[[102],[103]]
    },
    "-10:5":{
        "x":[[],[]],
        "y":[[103],[104]]
    },
    "-5:0":{
        "x":[[104],[105]],
        "y":[[],[]]
    },
    "5:0":{
        "x":[[105],[106]],
        "y":[[],[]]
    },
    "10:5":{
        "x":[[],[]],
        "y":[[106],[107]]
    },
    "10:15":{
        "x":[[],[]],
        "y":[[107],[108]]
    },
    "5:20":{
        "x":[[108],[101]],
        "y":[[],[]]
    },
}
rail_nodes = {
    "0:-4":{
        "x":[[],[]],
        "y":[[],[100]]
    },
    "0:3":{
        "x":[[],[]],
        "y":[[100],[101]]
    },
    "-6:3":{
        "x":[[],[]],
        "y":[[103],[104]]
    },
    "-3:6":{
        "x":[[101],[103]],
        "y":[[],[]]
    },
    "-6:-4":{
        "x":[[],[]],
        "y":[[104],[]]
    },
}
'''
rail_nodes = {'0:-4': {'x': [[], []], 'y': [[108], [100]]}, '0:4': {'x': [[110], [111]], 'y': [[100], [101, 102]]}, '-4:8': {'x': [[101], [103]], 'y': [[], []]}, '-8:12': {'x': [[], []], 'y': [[103], [104]]}, '-4:16': {'x': [[104], [105]], 'y': [[], []]}, '0:12': {'x': [[], []], 'y': [[105], [102]]}, '-3:-7': {'x': [[109], [108]], 'y': [[], []]}, '-6:-4': {'x': [[], []], 'y': [[109], [110]]}, '5:4': {'x': [[111], []], 'y': [[], []]}}


switches = {

}

tracks = {}

for node in rail_nodes:
    sx, sy = [(i+0.5)*256 for i in map(int,node.split(":"))]
    for axis in ["x","y"]:
        for rail_id in rail_nodes[node][axis][1]:
            if rail_id not in tracks: tracks[rail_id] = rails2d.Rail(rail_id)
            if tracks[rail_id].s_pos == None:
                tracks[rail_id].s_pos = (sx,sy)
                tracks[rail_id].s_axis = axis
                tracks[rail_id].s_links = rail_nodes[node][axis][0]
            else:
                tracks[rail_id].e_pos = (sx,sy)
                tracks[rail_id].e_axis = axis
                tracks[rail_id].e_links = rail_nodes[node][axis][0]

        for rail_id in rail_nodes[node][axis][0]:
            if rail_id not in tracks: tracks[rail_id] = rails2d.Rail(rail_id)
            if tracks[rail_id].s_pos == None:
                tracks[rail_id].s_pos = (sx,sy)
                tracks[rail_id].s_axis = axis
                tracks[rail_id].s_links = rail_nodes[node][axis][1]
            else:
                tracks[rail_id].e_pos = (sx,sy)
                tracks[rail_id].e_axis = axis
                tracks[rail_id].e_links = rail_nodes[node][axis][1]

for rail_id in tracks:
    tracks[rail_id].build()


train.tracks = tracks
train.nodes = rail_nodes
train.switches = switches

consists = []
consists.append(train.Consist(
    [(0.5)*256,-2*256],["Sv_p","Sv_m","Sv_p"], 100, 392, font
))
consists[-1].velocity_vector = 1

player.scale = 1

track_edges = {211:["up",(-25,-2),False]}
max_track_id = 211
generation_params = {
    "dx":[7,14],
    "max_dy":[0,3],
    "repeat_bezier":False
}

class Dummy:
    def __init__(self,pos,angle,type, bogeys):
        self.pos = (pos[0],pos[1])
        self.bogeys = bogeys
        self.angle = (angle-90)%360
        self.type = type

a = pg.Surface(win_size, pg.SRCALPHA)
a.fill((64,64,64,32))

while working:
    train.switches = switches
    clicked = False
    released = False
    pressed = []

    for evt in pg.event.get():
        if evt.type == pg.QUIT:
            working = False
        elif evt.type == pg.KEYDOWN:
            pressed.append(evt.key)

            if evt.key == pg.K_d: player.debug = not player.debug
            elif evt.key == pg.K_EQUALS: player.scale += 0.5
            elif evt.key == pg.K_MINUS: player.scale /= 2
            elif evt.key == pg.K_q: player.flag = not player.flag

            if evt.key == pg.K_s: consists[-1].velocity = 0
            if evt.key == pg.K_z: consists[-1].velocity_vector = [0,-1,1][consists[-1].velocity_vector]
        elif evt.type == pg.MOUSEBUTTONDOWN:
            clicked = True
        elif evt.type == pg.MOUSEBUTTONUP:
            released = True

    screen.fill((0,0,0))

    temp_trains = []
    occupied_tracks = []
    for c in consists:
        for tr in c.trains:
            temp_trains.append(Dummy([round(i,2) for i in tr.pos],tr.angle+tr.flipped*180,tr.type, tr.bogeys))
            occupied_tracks.append(tr.occupied_tracks[0])
            occupied_tracks.append(tr.occupied_tracks[1])

    player.pos = temp_trains[0 if consists[-1].velocity_vector == -1 else 2].pos
    disp = player.draw_map(temp_trains,font)
    screen.blit(disp,(screen.get_width()/2-disp.get_width()/2,screen.get_height()/2-disp.get_height()/2))
    screen.blit(a,(0,0))

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

        #rockgen

        chance = random.random()
        if chance > 0.5: 
            rock_yd = random.randint(1,2)*random.choice([1,-1])
            rock_xd = random.randint(0, max(new_pos[0],params[1][0])-min(new_pos[0],params[1][0]))
            rock_x = min(new_pos[0],params[1][0])+rock_xd
            if rock_yd > 0: rock_y = rock_yd+max(new_pos[1],params[1][1])
            else: rock_y = rock_yd+min(new_pos[1],params[1][1])

            player.blockmap[f"{rock_x}:{rock_y}"] = ["rock"]

        track_edges[max_track_id] = (params[0],new_pos, dy != 0)
        track_edges.pop(max_track_id-1)


    player.rail_nodes = rail_nodes
    player.tracks = tracks
    train.tracks = tracks
    train.nodes = rail_nodes
    train.switches = switches

    if pg.mouse.get_pressed()[0]: print(player.translate_from(pg.mouse.get_pos()))

    kbd = pg.key.get_pressed()

    screen.blit(consists[-1].electrical_system.render_graphics([i-100 for i in win_size], "look here! a stroka!", pressed, kbd, [pg.mouse.get_pos(), pg.mouse.get_pressed(), clicked, released]),(0,0))

    fps = round(clock.get_fps())
    speed = 16

    '''if kbd[pg.K_DOWN]: 
        player.pos[0] += speed
        player.pos[1] += speed
    elif kbd[pg.K_UP]: 
        player.pos[0] -= speed
        player.pos[1] -= speed
        
    if kbd[pg.K_RIGHT]: 
        player.pos[0] += speed
        player.pos[1] -= speed
    if kbd[pg.K_LEFT]: 
        player.pos[0] -= speed
        player.pos[1] += speed

    if kbd[pg.K_LALT]:
        switches = {
            "-10:-2":[[],[102]],
            "-5:-1":[[102],[106]],
        }
    else:
        switches = {
            "-10:-2":[[],[101]],
            "-5:-1":[[103],[105]],
        }'''

    #player.pos = [round(i) for i in player.pos]
    z = [
        version,
        f"pos: {player.pos}",
        f"fps: {fps}",
        #f"active rail {occupied_tracks[0]}",
        #f"speed: {round(consists[-1].pixel_velocity,2)} px/s",
        #f"speed: {round(consists[-1].velocity*3.6,2)} km/h",
        #f"acceleration: {round(consists[-1].acceleration,2)} m/s^2", 
        #f"torque: {round(consists[-1].torque,2)}"
    ]
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