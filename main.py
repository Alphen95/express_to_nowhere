#EXP TO:[Nowhere] VIA:[Shugurovka]

import pygame as pg
import os
import time
import random
import train
import isometry as isometry
import rails_iso as rails_m
import leitmotifplus as leitmotif
import json

win_size = (0,0)#(800,600)
version = "0.3.0.9 Oct-Dim prerelease"


pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(win_size, pg.SRCALPHA | pg.HWSURFACE) #| pg.FULLSCREEN)
font = pg.font.Font("res/font.ttf",20)
dfont = pg.font.Font("res/dots.otf",28)
sfont = pg.font.Font("res/font.ttf",24)

win_size = screen.get_size()
win_size = (win_size[0],win_size[1])

working = True
screenshot_mode = False
tile_size = 256
ct, fg, bg = (tile_size/2, tile_size/2), (tile_size, tile_size), (0,0)

route_map = {
    None:[" X "],
    "k":["(K)"],
    "m":["(M)"],
    "j":["<J>"],
}

tile_sheet = pg.image.load("res/tiles.png")
el_s_sheet = pg.image.load("res/el_s.png")
el_sp_sheet = pg.image.load("res/el_sp.png")
uvm8m_sheet = pg.image.load("res/uvm8.png")
uvm8p_sheet = pg.image.load("res/uvm8p.png")

player = isometry.Camera(win_size)

sprite_load_params = [ # name - (x|y) - (stacks|offset|repeats) - rotation/flip - alignment
    ["cyrok_cx", (0,0), (5,6,1), 0, ct],
    ["cyrok_cy", (0,0), (5,6,1), 90, ct],
    ["cyrok_xr", (0,5), (5,6,1), 0, ct],
    ["cyrok_xl", (0,5), (5,6,1), 180, ct],
    ["cyrok_yl", (0,5), (5,6,1), 90, ct],
    ["cyrok_yr", (0,5), (5,6,1), 270, ct],
    ["halfcyrok_xr", (0,10), (5,6,1), 0, ct],
    ["halfcyrok_xl", (0,10), (5,6,1), 180, ct],
    ["halfcyrok_yl", (0,10), (5,6,1), 90, ct],
    ["halfcyrok_yr", (0,10), (5,6,1), 270, ct],
    ["sign_x", (0,15), (6,24,1), 0, ct],
    ["sign_y", (0,15), (6,24,1), 90, ct],
    
    ["u_base", (1,12), (1,0,1), 0, ct],
    ["u_corner_a", (1,13), (1,0,1), 270, ct],
    ["u_corner_b", (1,13), (1,0,1), 180, ct],
    ["u_corner_c", (1,13), (1,0,1), 90, ct],
    ["u_corner_d", (1,13), (1,0,1), 0, ct],
    ["u_wall_a", (1,14), (1,0,6), 0, bg],
    ["u_wall_b", (1,14), (1,0,6), 270, bg],
    ["u_wall_c", (1,14), (1,0,6), 180, fg],
    ["u_wall_d", (1,14), (1,0,6), 90, fg],

    ["u_fence_a", (1,15), (4,0,1), 0, bg],
    ["u_fence_b", (1,15), (4,0,1), 90, bg],
    ["u_fence_c", (1,15), (4,0,1), 180, fg],
    ["u_fence_d", (1,15), (4,0,1), 270, fg],
    
    ["plt",     (1,0), (6,0,1),  0, ct],
    ["plt_exl", (1,6), (6,0,1),  0, fg],
    ["plt_exr", (1,6), (6,0,1), 180, bg],
    ["plt_eyl", (1,6), (6,0,1), 270, fg],
    ["plt_eyr", (1,6), (6,0,1),  90, bg],
    
    ["soundwall_xl", (2,0), (29,0,1),  0, fg],
    ["soundwall_xr", (2,0), ( 6,0,1),180, bg],
    ["soundwall_yl", (2,0), (29,0,1),270, bg],
    ["soundwall_yr", (2,0), ( 6,0,1), 90, fg],
    
    ["soundwall_sign_xr", (3,0), (29,0,1), 180, bg],
    ["soundwall_sign_yl", (3,0), (29,0,1), 270, bg],
    
    ["pillar_orange_xl", (0,21), (1,6,24),   0, fg],
    ["pillar_orange_xr", (0,21), (1,6,24), 180, bg],
    ["pillar_orange_yl", (0,21), (1,6,24), 270, bg],
    ["pillar_orange_yr", (0,21), (1,6,24),  90, fg],

    ["pillar_beige_xl", (0,22), (1,6,24),   0, fg],
    ["pillar_beige_xr", (0,22), (1,6,24), 180, bg],
    ["pillar_beige_yl", (0,22), (1,6,24), 270, bg],
    ["pillar_beige_yr", (0,22), (1,6,24),  90, fg],
    
    ["hloc-oct_xr", (4,0), (30,0,1),  0, bg],
    ["hloc-oct_xl", (4,0), (6,0,1),180, fg],

    ["cmkt_xr", (5,0), (24,6,1),  0, bg],
    ["cmkt_xl", (5,0), (24,6,1),180, fg],

    ["kirv_xr", (6,0), (24,6,1),  0, bg],
    ["kirv_xl", (6,0), (24,6,1),180, fg],
    ["kirv_pillar_xr", (0,23), (1,6,24),  0, bg],
    ["kirv_pillar_xl", (0,23), (1,6,24),180, fg],
    
    ["krnh-oct_xr", (7,0), (24,6,1),  0, bg],
    ["krnh-oct_xl", (7,0), (24,6,1),180, fg],
    ["krnh-oct_pillar_xr", (8,0), (24,6,1),  0, bg],
    ["krnh-oct_pillar_xl", (8,0), (24,6,1),180, fg],
    
    ["wemb_xr", (9,0), (24,6,1), 0, bg],
    ["wemb_xl", (9,0), (24,6,1), (1,0), fg],
    ["wemb_alt_xr", (10,0), (24,6,1), 0, bg],
    ["wemb_alt_xl", (10,0), (24,6,1), (1,0), fg],
    
    ["tast_xr", (11,0), (24,6,1), 0, bg],
    ["tast_xl", (11,0), (24,6,1), (1,0), fg],
    
    ["bnpk_xr", (12,0), (30,0,1), 0, bg],
    ["bnpk_xl", (12,0), (30,0,1), (1,0), fg],
    ["bnpk_pillar_xr", (13,0), (24,6,1), 0, bg],
    ["bnpk_pillar_xl", (13,0), (24,6,1), (1,0), fg],
    
    ["dage", (14,0), (24,6,1), 90, ct],
    ["dage_alt", (15,0), (24,6,1), 90, ct],
    
    ["mlwk", (16,0), (24,6,1), 90, ct],
    ["mlwk_alt", (17,0), (24,6,1), 90, ct],
    ["mlwk_exit_a", (18,0), (24,6,1), 90, ct],
    ["mlwk_exit_b", (18,0), (24,6,1), 270, ct],
    
    ["unmg_xr", (19,0), (24,6,1), 0, bg],
    ["unmg_xl", (19,0), (24,6,1), (1,0), fg],
    ["unmg_pillar_xr", (20,0), (24,6,1), 0, fg],
    ["unmg_pillar_xl", (20,0), (24,6,1), (1,0), bg],
    
    ["usmr_xr", (21,0), (24,6,1), 0, bg],
    ["usmr_xl", (21,0), (24,6,1), (1,0), fg],
    ["usmr_pillar_xr", (22,0), (24,6,1), 0, fg],
    ["usmr_pillar_xl", (22,0), (24,6,1), (1,0), bg],
    
    ["zrge-oct_xr", (23,0), (30,0,1), 0, bg],
    ["zrge-oct_xl", (23,0), (6 ,0,1), (1,0), fg],
    ["zrge-oct_pillar_xr", (24,0), (24,6,1), 0, fg],
    ["zrge-oct_pillar_xl", (24,0), (24,6,1), (1,0), bg],
    
    ["lesq_xr", (25,0), (24,0,1), 0, bg],
    ["lesq_xl", (25,0), (24,0,1), (1,0), fg],
    ["lesq_pillar_xr", (26,0), (24,6,1), 0, fg],
    ["lesq_pillar_xl", (26,0), (24,6,1), (1,0), bg],
    
    ["cuhl_xr", (27,0), (30,0,1), 0, bg],
    ["cuhl_xl", (27,0), (6 ,0,1), (1,0), fg],
    ["cuhl_pillar_xr", (0,24), (1,6,24), 0, fg],
    ["cuhl_pillar_xl", (0,24), (1,6,24), (1,0), bg],
    
    ["encg_yl", (28,0), (24,6,1), 0, fg],
    ["encg_yr", (28,0), (24,6,1), (0,1), bg],
]

for param_pack in sprite_load_params:
    player.sprites[param_pack[0]] = player.render_tile(
        pg.transform.rotate(tile_sheet.subsurface(param_pack[1][0]*64,(param_pack[1][1]+1)*64,64,param_pack[2][0]*64),90) # base surface
        ,(param_pack[2][0],param_pack[2][1],2,param_pack[2][2]), # stacks-offset-FIXED SCALE-repeats
        param_pack[4], # rotation/flip
        param_pack[3]  # align
    )


#player.train_sprites["Sv_p"] = player.render_train(el_s_sheet,((32,98),28 ,2))
#player.train_sprites["Sv_m"] = player.render_train(el_sp_sheet,((32,98),32 ,2))
player.train_sprites["uvm8-m"] = player.render_train(uvm8m_sheet,((22,104),21 ,2))
player.train_sprites["uvm8-p"] = player.render_train(uvm8p_sheet,((22,104),21 ,2))


with open("world.json") as f:
    q = json.loads(f.read())
    rail_nodes, blockmap, aux_blockmap, underay_map, stations = q

with open("route_switches.json") as f: route_switches = json.loads(f.read())

player.blockmap = blockmap
player.auxmap = aux_blockmap
player.undermap = underay_map

st_tilemap = {}

for stat in stations:
    for x in range(min(stat[0][0], stat[1][0]), max(stat[0][0], stat[1][0])):
        for y in range(min(stat[0][1], stat[1][1]), max(stat[0][1], stat[1][1])):
            for z in range(min(stat[0][2], stat[1][2]), max(stat[0][2], stat[1][2])+1):
                st_tilemap[(x,y,z)] = (stat[2], stat[3])

tracks = {}


for node in rail_nodes:
    bx, by, bz = map(int, node.split(":"))
    sx, sy, sz = (bx+0.5)*tile_size, (by+0.5)*tile_size, bz*tile_size
    for axis in ["x","y"]:
        for rail_id in rail_nodes[node][axis][1]:
            if rail_id not in tracks: tracks[rail_id] = rails_m.Rail(rail_id)
            if tracks[rail_id].s_pos == None:
                tracks[rail_id].s_pos = (sx,sy,sz)
                tracks[rail_id].s_axis = axis
                tracks[rail_id].s_links = rail_nodes[node][axis][0]
            else:
                tracks[rail_id].e_pos = (sx,sy,sz)
                tracks[rail_id].e_axis = axis
                tracks[rail_id].e_links = rail_nodes[node][axis][0]

        for rail_id in rail_nodes[node][axis][0]:
            if rail_id not in tracks: tracks[rail_id] = rails_m.Rail(rail_id)
            if tracks[rail_id].s_pos == None:
                tracks[rail_id].s_pos = (sx,sy,sz)
                tracks[rail_id].s_axis = axis
                tracks[rail_id].s_links = rail_nodes[node][axis][1]
            else:
                tracks[rail_id].e_pos = (sx,sy,sz)
                tracks[rail_id].e_axis = axis
                tracks[rail_id].e_links = rail_nodes[node][axis][1]

for rail_id in tracks:
    tracks[rail_id].build()

player.rail_nodes = rail_nodes
player.tracks = tracks
train.tracks = tracks
train.nodes = rail_nodes
player.pos = [0*256,0,0]

player.scale = 1

class Dummy:
    def __init__(self, pos, size, angle,type, bogeys):
        self.pos = [pos[0],pos[1],pos[2]]
        self.size = size
        self.bogeys = bogeys
        self.angle = (angle-90)%360
        self.type = type

a = pg.Surface(win_size, pg.SRCALPHA)
a.fill((64,64,64,32))

train_spawn_info = [
    [[("uvm8-m",False,True,True),("uvm8-p",True,True,True),("uvm8-m",True,True,True)],105*4],
    [[("uvm8-m",False,True,True),("uvm8-m",True,True,True),],105*4]
]

consists = {}
curc = -1
q = 0

follow = True
spawn = False

spawnpoints = [
    ["Energy College", 288],["City Culture Hall", 275],["Zorge St-October Av [OCT]", 220],["Halle St-October Av-1", 1], ["Balanovo-Park", 124], ["Milowsk Hwy", 160], # October Av & Dim
]
trains = ["UVM-8 (3 cars)", "UVM-8 (2 cars)"]

spawn_window = leitmotif.Window((screen.get_width()-300-4, screen.get_height()/2-75, 300, 242), font, 26, {
    "label_title":{
        "active":True,"type":"label","align":"center","text":"Train spawner",
        "rect":[0,"indent","w","line_height"]
    },
    "list_station": {
        "active":True,"type":"item_list","items":[i[0] for i in spawnpoints],
        "rect":[0,"indent+line_height*1.33","w","line_height*4"]
    },
    "list_train": {
        "active":True,"type":"item_list","items":trains,
        "rect":[0,"indent+line_height*5.66","w","line_height*2"]
    },
    "button_spawn":{
        "active":True,"type":"button","text":"Spawn","align":"center",
        "rect":["2","indent+line_height*8","w/2-4","line_height"]
    },
    "button_spawn_arcade":{
        "active":True,"type":"button","text":"Spawn Arcade","align":"center",
        "rect":["w/2+2","indent+line_height*8","w/2-4","line_height"]
    },
})
spawn_window.recalculate()

while working:
    clicked = False
    released = False
    pressed = []
    if curc == -1: follow = False

    for evt in pg.event.get():
        if evt.type == pg.QUIT:
            working = False
        elif evt.type == pg.KEYDOWN:
            pressed.append(evt.key)

            if evt.key == pg.K_d: player.debug = not player.debug
            elif evt.key == pg.K_q and not follow: player.pos[2] -= tile_size
            elif evt.key == pg.K_e and not follow: player.pos[2] += tile_size
            
            if evt.key == pg.K_p: follow = not follow

            if evt.key == pg.K_s: spawn = not spawn
            if evt.key == pg.K_o: screenshot_mode = not screenshot_mode

            if evt.key == pg.K_DELETE and curc != -1:
                consists[curc].is_alive = False
                consists.pop(curc)
                curc = -1

            if evt.key == pg.K_z and curc != -1: consists[curc].velocity_vector = [0,-1,1][consists[curc].velocity_vector]

            if evt.key == pg.K_LEFT and follow:
                consists[curc].route = list(route_map.keys())[(list(route_map.keys()).index(consists[curc].route)+1)%len(route_map)]
                if consists[curc].route in route_switches:consists[curc].routing_switches = route_switches[consists[curc].route]
                else: consists[curc].routing_switches = {}
                
            if evt.key == pg.K_RIGHT and follow:
                consists[curc].route = list(route_map.keys())[(list(route_map.keys()).index(consists[curc].route)-1)%len(route_map)]
                if consists[curc].route in route_switches:consists[curc].routing_switches = route_switches[consists[curc].route]
                else: consists[curc].routing_switches = {}

        elif evt.type == pg.MOUSEBUTTONDOWN:
            clicked = True
        elif evt.type == pg.MOUSEBUTTONUP:
            released = True
    m_pos = pg.mouse.get_pos()
    m_btn = pg.mouse.get_pressed()

    mouse_state = (m_pos[0], m_pos[1], clicked, (m_btn[0] or m_btn[1] or m_btn[2]), (m_btn[0], m_btn[1], m_btn[2]))

    screen.fill((0,0,0))

    temp_trains = []
    occupied_tracks = []
    for c in consists:
        for enum, tr in enumerate(consists[c].trains):
            temp_trains.append(Dummy([round(i,2) for i in tr.pos], consists[c].size,tr.angle+tr.flipped*180,tr.type, tr.bogeys))
            if c == curc and follow:
                if consists[curc].velocity_vector == -1 and enum == 0: player.pos = temp_trains[-1].pos
                if consists[curc].velocity_vector == 1 and enum+1 == len(consists[c].trains): player.pos = temp_trains[-1].pos

            occupied_tracks.append(tr.occupied_tracks[0])
            occupied_tracks.append(tr.occupied_tracks[1])
    
    player.draw_map(temp_trains,screen, q)
    player_block = [int(i//tile_size) for i in player.pos]
    player_block = (player_block[0], player_block[1], player_block[2])

    #player.rail_nodes = rail_nodes
    #player.tracks = tracks
    #train.tracks = tracks
    #train.nodes = rail_nodes

    kbd = pg.key.get_pressed()

    if follow and curc != -1:
        screen.blit(consists[curc].internal.render_graphics(screen, screen.get_size(), "look here! a stroka!", pressed, kbd, [pg.mouse.get_pos(), pg.mouse.get_pressed(), clicked, released]),(0,0))
        consists[curc].switch = kbd[pg.K_LALT]# if consists[curc].route != None else 0

    fps = round(clock.get_fps())
    speed = 16 if not kbd[pg.K_LALT] else 1

    if not follow:
        if kbd[pg.K_DOWN]: 
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


    z = [
        version,
        f"pos: {player.pos}",
        f"fps: {fps}",
    ]
    
    if curc != -1:
        z += [
        f"pressure {consists[curc].internal.pressure} атм",
        f"скорость {round(consists[curc].velocity*3.6,2)} км/ч",
        f"ускорение {round(consists[curc].acceleration,2)} м/с^2",]

    char = dfont.render("A",True, (0,0,0))

    if spawn:
        spawn_window.update(screen, mouse_state, pressed)
        if spawn_window.get_state("button_spawn") and spawn_window.get_state("list_station") != "" and spawn_window.get_state("list_train") != "" and curc == -1:
            trackid = spawnpoints[spawn_window.objects["list_station"]["items"].index(spawn_window.get_state("list_station"))][1]
            trainpar = train_spawn_info[spawn_window.objects["list_train"]["items"].index(spawn_window.get_state("list_train"))]
            tmp = train.spawn_train(
                trainpar[0],
                trackid if type(trackid) == int else random.choice(trackid), 
                (trainpar[1],64), font)
            if tmp != None:
                curc = random.randint(0, 9999)
                consists[curc] = tmp
                consists[curc].velocity_vector = 1
                follow = True
        if spawn_window.get_state("button_spawn_arcade") and spawn_window.get_state("list_station") != "" and spawn_window.get_state("list_train") != "" and curc == -1:
            trackid = spawnpoints[spawn_window.objects["list_station"]["items"].index(spawn_window.get_state("list_station"))][1]
            trainpar = train_spawn_info[spawn_window.objects["list_train"]["items"].index(spawn_window.get_state("list_train"))]
            tmp = train.spawn_train(
                trainpar[0],
                trackid if type(trackid) == int else random.choice(trackid), 
                (trainpar[1],64), font)
            if tmp != None:
                curc = random.randint(0, 9999)
                consists[curc] = tmp
                consists[curc].velocity_vector = 1
                consists[curc].internal.dumb = True
                follow = True


    if curc != -1:
        bh = 20
        maxchar = 34
        dlt = int(char.get_width()*1)
        w = dlt*(maxchar)+char.get_height()
        h = char.get_height()*1.5
        bx = screen.get_width()-w-20
        pg.draw.rect(screen, (128,128,128), (bx-4, bh-4, w+8, h+8))
        pg.draw.rect(screen, (96,96,96), (bx, bh, w, h))
        name = route_map[consists[curc].route][0]+" "
        if player_block in st_tilemap:
            name += st_tilemap[player_block][0]
        
        for i in range(maxchar):
            pg.draw.rect(screen, (91,127,0), (bx+char.get_height()/2+dlt*(i), bh+char.get_height()*0.25, char.get_width(), char.get_height()))
            if i < len(name):
                let = dfont.render(name[i].upper(), True, (182,255,0))
                screen.blit(let, (bx+char.get_height()/2+dlt*(i+0.5)-let.get_width()/2, bh+char.get_height()*0.25))


    if not screenshot_mode:
        for enum, line in enumerate(z):
            ptext = font.render(line,True,(240,240,240),(0,0,0))
            screen.blit(ptext,(20,20+30*enum))

        #if curc != -1 and consists[curc].route == None: altstate = "DISABLED"
        altstate = 'pressed' if kbd[pg.K_LALT] else 'released'
        ptext = font.render(f"alt {altstate}",True,(240,240,240),(84,109,255) if altstate == 'pressed' else(0,0,0))
        screen.blit(ptext,(20,20+30*len(z)))


    #ptext = font.render(f"а приборки-то нема",True,(240,240,240),(255,50,50))
    #screen.blit(ptext,(screen.get_width()-20-ptext.get_width(),screen.get_height()-20-ptext.get_height()))

    pg.display.update()
    clock.tick(60)

pg.quit()
for tr in consists:
    consists[tr].is_alive = False