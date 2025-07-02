#EXP TO:[Nowhere] VIA:[Shugurovka]

import pygame as pg
import os
import time
import random
import leitmotifplus as leitmotif
import isometry as isometry
import rails_iso as rails_m
import train
import json

win_size = (0,0)#(800,600)
version = "0.2.8.1 polishing"


pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(win_size, pg.SRCALPHA | pg.HWSURFACE) #| pg.FULLSCREEN)
font = pg.font.Font("res/font.ttf",20)
dfont = pg.font.Font("res/dots.otf",28)
sfont = pg.font.Font("res/font.ttf",24)

win_size = screen.get_size()
win_size = (win_size[0],win_size[1])

working = True
tile_size = 256
ct, fg, bg = (tile_size/2, tile_size/2), (tile_size, tile_size), (0,0)

route_map = {
    None:[(10,10,10),(255,255,255),"X"],

    #"c_old":[(75,199,123),(1,1,1),"CC"],

    #"a":[(9,59,93),(255,255,255),"A"],
    #"c":[(9,59,93),(255,255,255),"C"],
    #"h":[(9,59,93),(255,255,255),"H"],

    "b":[(242,99,35),(255,255,255),"B"],
    "d":[(242,99,35),(255,255,255),"D"],

    "e":[(31,65,155),(255,255,255),"E"],
    "k":[(31,65,155),(255,255,255),"K"],

    #"j":[(154,103,51),(255,255,255),"E"],
    #"m":[(154,103,51),(255,255,255),"K"],

    #"n":[(246,210,23),(0,0,0),"N"],
    #"q":[(246,210,23),(0,0,0),"Q"],
    
    #"l":[(167,170,172),(255,255,255),"L"],
    #"l_exp":[(167,170,172),(255,255,255),"Lx"],

    #"1":[(238,51,48),(255,255,255),"1"],
    #"2":[(238,51,48),(255,255,255),"2"],
    #"3":[(238,51,48),(255,255,255),"3"],
    #"9":[(238,51,48),(255,255,255),"9"],
    
    "4":[(14,148,71),(255,255,255),"4"],
    "5":[(14,148,71),(255,255,255),"5"],
    "6":[(14,148,71),(255,255,255),"6"],

    #"8":[(73,218,247),(255,255,255),"8"],

    "7":[(172,66,152),(255,255,255),"7"],
    "7_exp":[(172,66,152),(255,255,255),"7x"],
    "11":[(172,66,152),(255,255,255),"11"],
}

tile_sheet = pg.image.load("res/tiles.png")
el_s_sheet = pg.image.load("res/el_s.png")
el_sp_sheet = pg.image.load("res/el_sp.png")
plt0_sheet = pg.image.load("res/plt0.png")
plt1_sheet = pg.image.load("res/plt1.png")
plt3_sheet = pg.image.load("res/plt3.png")

player = isometry.Camera(win_size)
player.sprites["under_base"] = player.render_tile(tile_sheet.subsurface(1248,128,32,32),(1,0,4),0)
player.sprites["under_crna"] = player.render_tile(tile_sheet.subsurface(1248,160,32,32),(1,0,4),0,0)
player.sprites["under_crnb"] = player.render_tile(tile_sheet.subsurface(1248,160,32,32),(1,0,4),0,90)
player.sprites["under_crnc"] = player.render_tile(tile_sheet.subsurface(1248,160,32,32),(1,0,4),0,180)
player.sprites["under_crnd"] = player.render_tile(tile_sheet.subsurface(1248,160,32,32),(1,0,4),0,270)

player.sprites["rock"] = player.render_tile(tile_sheet.subsurface(0,128,1280,32),(32,0,4),1)
player.sprites["platform"] = player.render_tile(tile_sheet.subsurface(0,160,96,32),(3,0,4),ct)
player.sprites["platform_e_x_l"] = player.render_tile(tile_sheet.subsurface(0,192,96,32),(3,0,4),fg,0)
player.sprites["platform_e_x_r"] = player.render_tile(tile_sheet.subsurface(0,192,96,32),(3,0,4),bg,180)
player.sprites["platform_e_y_r"] = player.render_tile(tile_sheet.subsurface(0,192,96,32),(3,0,4),fg,270)
player.sprites["platform_e_y_l"] = player.render_tile(tile_sheet.subsurface(0,192,96,32),(3,0,4),bg,90)
player.sprites["platform_s_a"] = player.render_tile(tile_sheet.subsurface(96,192,448,32),(14,0,4),ct,0)
player.sprites["platform_s_b"] = player.render_tile(tile_sheet.subsurface(96,224,448,32),(14,0,4),ct,180)
player.sprites["platform_s_c"] = player.render_tile(tile_sheet.subsurface(96,256,448,32),(14,0,4),ct,90)
player.sprites["platform_s_d"] = player.render_tile(tile_sheet.subsurface(96,288,448,32),(14,0,4),ct,270)

#player.train_sprites["Sv_p"] = player.render_train(el_s_sheet,((32,98),28 ,2))
#player.train_sprites["Sv_m"] = player.render_train(el_sp_sheet,((32,98),32 ,2))
player.train_sprites["plt0"] = player.render_train(plt0_sheet,((32,101),21 ,2))
player.train_sprites["plt1"] = player.render_train(plt1_sheet,((32,122),21 ,2))
player.train_sprites["plt3"] = player.render_train(plt3_sheet,((32,97),21 ,2))


with open("world.json") as f:
    q = json.loads(f.read())
    rail_nodes, blockmap, underay_map, stations = q

with open("route_switches.json") as f: route_switches = json.loads(f.read())

player.blockmap = blockmap
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
    [[("plt0",False,True,True),("plt0",True,True,True),("plt0",False,True,True),("plt0",True,True,True)],400],
    [[("plt1",False,True,True),("plt1",True,True,True),("plt1",False,True,True),("plt1",True,True,True)],488],
    [[("plt3",False,True,True),("plt3",True,True,True),("plt3",False,True,True),("plt3",True,True,True)],388]
]

consists = {}
curc = -1
q = 0

spawn_params = {
    "spawnpoints":[
        ["78-Waterside", 1227], ["Union Tpke", 1267], ["Pathalassic-Expo", 1350], ["Intervale Sq", 1374], ["Halson Term", 516], #5av-Wside-Garcia
        ["Kennedy-Main", 840], ["Herald Sq", 1379], ["Eastferry", 1395], ["South Bway", 1969], ["Suffolk Av", 2017] #Kennedy-Union
    ],
    "trains":["PLT-0", "PLT-1", "PLT-3"],
    "pointers":[0,0]
}


follow = True
spawn = False

spawnpoints = [
    ["78 St - Waterside", 1227], ["Union Turnpike", 1267], ["Pathalassic Av - Expo", 1350], ["Intervale Square", 1374], ["Halson Terminal", 516], #5av-Wside-Garcia
    ["Kennedy - Main St", 840], ["Herald Square", 1379], ["Eastferry", 1395], ["Suffolk Av", 2017], #Kennedy-Union
    ["South Broadway", 1947], ["39 Street - Exchange", 2200], ["Worth Street", 2522], ["Tenporter Yard", [2547,2546,2545,2544]], #Newport
]
trains = ["PLT-0", "PLT-1", "PLT-3"]

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
        "active":True,"type":"button","text":"Spawn!","align":"center",
        "rect":["w/4+1","indent+line_height*8","w/2-2","line_height"]
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
        screen.blit(consists[curc].internal.render_graphics(screen.get_size(), "look here! a stroka!", pressed, kbd, [pg.mouse.get_pos(), pg.mouse.get_pressed(), clicked, released]),(0,0))
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
        if spawn_window.get_state("button_spawn") and spawn_window.get_state("list_station") != "" and spawn_window.get_state("list_train") != "":
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


    if curc != -1:
        bh = 20
        maxchar = 30
        dlt = int(char.get_width()*1)
        w = char.get_width()*3+dlt*(maxchar)+char.get_height()
        h = char.get_height()*1.5
        bx = screen.get_width()-w-20
        pg.draw.rect(screen, (128,128,128), (bx-4, bh-4, w+8, h+8))
        pg.draw.rect(screen, (96,96,96), (bx, bh, w, h))
        name = ""
        if player_block in st_tilemap:
            name = st_tilemap[player_block][0]

        route = consists[curc].route
        pg.draw.rect(screen, route_map[route][0], (bx+char.get_width(), bh+char.get_height()*0.25, char.get_height(), char.get_height()))
        line = sfont.render(route_map[route][2], True, route_map[route][1])
        screen.blit(line, (bx+char.get_width()+char.get_height()/2-line.get_width()/2, bh+char.get_height()*0.75-line.get_height()/2))
        
        for i in range(maxchar):
            pg.draw.rect(screen, (91,127,0), (bx+char.get_width()+char.get_height()+dlt*(i+1), bh+char.get_height()*0.25, char.get_width(), char.get_height()))
            if i < len(name):
                let = dfont.render(name[i].upper(), True, (182,255,0))
                screen.blit(let, (bx+char.get_width()+char.get_height()+dlt*(i+1.5)-let.get_width()/2, bh+char.get_height()*0.25))



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