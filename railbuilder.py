# fun railbuilding thingy

import pygame as pg
import math
import rails_iso as rails_m
import json

win_size = (0,0)

tile_size = 64
colors = []
for color in ("#333333","#ee3330", "#1f419b", "#f6d217", "#0e9447"):
    colors.append(pg.color.Color(color))

first = [None, None]
second = [None, None]

cur_stat = 0
select = 0

with open("world.json") as f:
    q = json.loads(f.read())
    rail_nodes, blockmap, aux_blockmap, underlay_map, stations = q

tracks = {

}

def draw_opaque_polygon(target, points, color, opacity):
    px, py = [], []
    for point in points:
        px.append(point[0])
        py.append(point[1])

    w, h = max(px)-min(px), max(py)-min(py)
    s = pg.Surface((w,h))
    s.set_alpha(opacity)
    pg.draw.polygon(s, color, [(i[0]-min(px), i[1]-min(py)) for i in points])
    s.set_colorkey((0,0,0))
    target.blit(s, (min(px), min(py)))


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
    tracks[rail_id].ud = tile_size//2+1
    tracks[rail_id].build()


maxtrack=(max(tracks)+1 if tracks != {} else 0)

pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(win_size, pg.SRCALPHA | pg.HWSURFACE)# | pg.FULLSCREEN)
font = pg.font.Font("res/font.ttf",20)
font_alt = pg.font.Font("res/font.ttf",14 )

win_size = [i+100 for i in screen.get_size()]
tiles_disp = [math.ceil(i/tile_size/2) for i in win_size]

directional_prism = pg.Surface((tile_size,tile_size))

pg.draw.polygon(directional_prism,(colors[1]),[
    [0,0],
    [tile_size,0],
    [tile_size*0.5,tile_size*0.5],
]),
pg.draw.polygon(directional_prism,(colors[2]),[
    [0,tile_size],
    [tile_size,tile_size],
    [tile_size*0.5,+tile_size*0.5],
])
pg.draw.polygon(directional_prism,(colors[3]),[
    [0,0],
    [0,tile_size],
    [tile_size*0.5,tile_size*0.5],
])
pg.draw.polygon(directional_prism,(colors[4]),[
    [tile_size,0],
    [tile_size,tile_size],
    [tile_size*0.5,tile_size*0.5],
])

directional_prism.set_alpha(128)

working = True
pos = [0,0,0]
m_block = [14,88,1488]
old_m_pos = (0,0)

underlay_blocks = ["base", "corner_a", "corner_b", "corner_c", "corner_d", "wall_a", "wall_b", "wall_c", "wall_d"]
underlay_blocks_alt = ["base", "corner_a", "corner_b", "corner_c", "corner_d", "fence_a", "fence_b", "fence_c", "fence_d"]
special_objects = ["temp_a", "temp_b", "temp_c", "temp_d", "temp_e", "temp_f"]
objects = [
    'plt',
    'plt_exl',
    'plt_exr',
    'plt_eyl',
    'plt_eyr',
    ['plt_exl', 'plt_exr'],
    ['plt_eyl', 'plt_eyr'],
    'plt',
    'plt',
]

mode = "underlay"
modes = ["rail", "object", "spobject", "underlay", "station"]
mode_str = {'rail':'Rails', 'object': 'Tiles', 'spobject': 'Temporary tiles' , 'underlay':'Underlay', "station":"Stations "}

while working:
    if cur_stat+1 > len(stations):
        stations.append([(0,0,0), (1,1,0), "unnamed", "lines"])

    clicked = False
    released = False
    pressed = []
    screen.fill((240,240,240))

    cam_pos = (pos[0]//tile_size, pos[1]//tile_size, pos[2]//tile_size)
    sw, sh = screen.get_size()
    rails = []
    stat = pg.Surface([tile_size]*2)
    stat.fill((240,0,0))
    stat.set_alpha(64)
    ax, ay, az = stations[cur_stat][0]
    bx, by, bz = stations[cur_stat][1]

    for ty in range(-tiles_disp[1],tiles_disp[1]+1):
        for tx in range(-tiles_disp[0],tiles_disp[0]+1):
            block_corner = (sw/2-(tx*tile_size-pos[1]%tile_size), sh/2+ty*tile_size-pos[0]%tile_size, tile_size, tile_size)
            bcrd = f"{cam_pos[0]+ty}:{cam_pos[1]+tx}:{cam_pos[2]}"
            if (cam_pos[0]+tx)%2 == (cam_pos[1]+ty)%2:
                pg.draw.rect(screen, (200,200,200), block_corner)

            if bcrd in rail_nodes:

                for axis in rail_nodes[bcrd]:
                    for side in rail_nodes[bcrd][axis]:
                        for track in side: rails.append(track)

    for track in rails:
        inf = tracks[track]
        l_stack = ["",""]
        r_stack = ["", ""]
        for i in range(len(inf.raw_up_l)):
            l_stack = [l_stack[1], ""]
            r_stack = [r_stack[1], ""]

            l_p = inf.raw_up_l[i]
            l_stack[1] = ((
                sw/2-(l_p[1]-pos[1])+tile_size,
                sh/2+(l_p[0]-pos[0]),
                l_p[2]
            ))
            
            r_p = inf.raw_up_r[i]
            r_stack[1] = ((
                sw/2-(r_p[1]-pos[1])+tile_size,
                sh/2+(r_p[0]-pos[0]),
                r_p[2]
            ))

            if l_stack[0] != "":
                dh = abs((l_stack[0][2]+l_stack[1][2])/2-pos[2])
                if dh != 0 and dh <= tile_size/2:
                    draw_opaque_polygon(screen, l_stack+r_stack[::-1], (80,80,80), 255*(1-dh*2/tile_size))
                elif dh == 0:
                    pg.draw.polygon(screen, (80,80,80), [i[:2] for i in l_stack+r_stack[::-1]])

    for ty in range(-tiles_disp[1],tiles_disp[1]+1):
        for tx in range(-tiles_disp[0],tiles_disp[0]+1):
            block_corner = (sw/2-(tx*tile_size-pos[1]%tile_size), sh/2+ty*tile_size-pos[0]%tile_size, tile_size, tile_size)
            bcrd = f"{cam_pos[0]+ty}:{cam_pos[1]+tx}:{cam_pos[2]}"
            if bcrd in underlay_map:
                if False: pass
                elif underlay_map[bcrd] == "base":
                    pg.draw.rect(screen, (96,96,96), block_corner)
                elif underlay_map[bcrd] == "corner_a":
                    pg.draw.polygon(screen, (96,96,96),(
                        (block_corner[0], block_corner[1]),
                        (block_corner[0]+tile_size, block_corner[1]),
                        (block_corner[0]+tile_size, block_corner[1]+tile_size)
                    ))
                elif underlay_map[bcrd] == "corner_b":
                    pg.draw.polygon(screen, (96,96,96),(
                        (block_corner[0]+tile_size, block_corner[1]+tile_size),
                        (block_corner[0], block_corner[1]+tile_size),
                        (block_corner[0]+tile_size, block_corner[1])
                    ))
                elif underlay_map[bcrd] == "corner_c":
                    pg.draw.polygon(screen, (96,96,96),(
                        (block_corner[0], block_corner[1]+tile_size),
                        (block_corner[0], block_corner[1]),
                        (block_corner[0]+tile_size, block_corner[1]+tile_size)
                    ))
                elif underlay_map[bcrd] == "corner_d":
                    pg.draw.polygon(screen, (96,96,96),(
                        (block_corner[0], block_corner[1]),
                        (block_corner[0], block_corner[1]+tile_size),
                        (block_corner[0]+tile_size, block_corner[1])
                    ))


    for track in rails:
        inf = tracks[track]
        p = []
        for point in inf.points:
            p.append((
                sw/2-(point[1]-pos[1])+tile_size,
                sh/2+(point[0]-pos[0])
            ))
        
        pg.draw.lines(screen, colors[0], False, p, 2)

        if tile_size >= 32:
            tid = font.render(f"{track}", True, (240,240,240),(10,10,10))
            m=0
            if len(inf.points) > 2: m=1
            a = (
                    sw/2-(inf.points[len(inf.points)//2-m][1]-pos[1])+tile_size,
                    sh/2+(inf.points[len(inf.points)//2-m][0]-pos[0])
                )
            b = (
                    sw/2-(inf.points[len(inf.points)//2-1-m][1]-pos[1])+tile_size,
                    sh/2+(inf.points[len(inf.points)//2-1-m][0]-pos[0])
                )
            screen.blit(tid, ((a[0]+b[0])/2-tid.get_width()/2, (a[1]+b[1])/2-tid.get_height()/2))

    for ty in range(-tiles_disp[1],tiles_disp[1]+1):
        for tx in range(-tiles_disp[0],tiles_disp[0]+1):
            block_corner = (sw/2-(tx*tile_size-pos[1]%tile_size), sh/2+ty*tile_size-pos[0]%tile_size, tile_size, tile_size)
            bcrd = f"{cam_pos[0]+ty}:{cam_pos[1]+tx}:{cam_pos[2]}"
            
            #if tile_size >= 32:
            #    a = font_alt.render(bcrd, True, (0,0,0))
            #    screen.blit(a, block_corner)

            if bcrd in underlay_map:
                if False: pass
                elif underlay_map[bcrd] == "wall_a":
                    pg.draw.rect(screen, (120,120,120), [block_corner[0]+tile_size*7/8, block_corner[1],block_corner[2]/8, block_corner[3]])
                elif underlay_map[bcrd] == "wall_b":
                    pg.draw.rect(screen, (120,120,120), [block_corner[0], block_corner[1],block_corner[2], block_corner[3]/8])
                elif underlay_map[bcrd] == "wall_c":
                    pg.draw.rect(screen, (120,120,120), [block_corner[0], block_corner[1],block_corner[2]/8, block_corner[3]])
                elif underlay_map[bcrd] == "wall_d":
                    pg.draw.rect(screen, (120,120,120), [block_corner[0], block_corner[1]+tile_size*7/8,block_corner[2], block_corner[3]/8])
                elif underlay_map[bcrd] == "fence_a":
                    pg.draw.rect(screen, (240,240,240), [block_corner[0]+tile_size*7/8, block_corner[1],block_corner[2]/8, block_corner[3]])
                elif underlay_map[bcrd] == "fence_b":
                    pg.draw.rect(screen, (240,240,240), [block_corner[0], block_corner[1],block_corner[2], block_corner[3]/8])
                elif underlay_map[bcrd] == "fence_c":
                    pg.draw.rect(screen, [240]*3, [block_corner[0], block_corner[1],block_corner[2]/8, block_corner[3]])
                elif underlay_map[bcrd] == "fence_d":
                    pg.draw.rect(screen, [240]*3, [block_corner[0], block_corner[1]+tile_size*7/8,block_corner[2], block_corner[3]/8])

            if bcrd in blockmap:
                tpc = [[block_corner[0]+tile_size*0.3,block_corner[1]+tile_size*0.4], [block_corner[0]+tile_size*0.4,block_corner[1]+tile_size*0.3],[block_corner[0]+tile_size*0.5,block_corner[1]+tile_size*0.4],[block_corner[0]+tile_size*0.4,block_corner[1]+tile_size*0.5]]
                for tile in blockmap[bcrd]:
                    if False: pass
                    elif tile == "plt":
                        pg.draw.rect(screen, (160,160,160), block_corner)
                    elif tile == "plt_exr":
                        pg.draw.rect(screen, (160,160,160), [block_corner[0]+tile_size*3/4, block_corner[1],block_corner[2]/4, block_corner[3]])
                    elif tile == "plt_exl":
                        pg.draw.rect(screen, (160,160,160), [block_corner[0], block_corner[1],block_corner[2]/4, block_corner[3]])
                    elif tile == "plt_eyl":
                        pg.draw.rect(screen, (160,160,160), [block_corner[0], block_corner[1]+tile_size*3/4,block_corner[2], block_corner[3]/4])
                    elif tile == "plt_eyr":
                        pg.draw.rect(screen, (160,160,160), [block_corner[0], block_corner[1],block_corner[2], block_corner[3]/4])
                    elif tile == "temp_a":
                        pg.draw.polygon(screen,(255,0,0),tpc)
                    elif tile == "temp_b":
                        pg.draw.polygon(screen,(0,255,0),tpc)
                    elif tile == "temp_c":
                        pg.draw.polygon(screen,(0,0,255),tpc)
                    elif tile == "temp_d":
                        pg.draw.polygon(screen,(255,255,0),tpc)
                    else:
                        pg.draw.rect(screen, (0,0,0), [block_corner[0]+tile_size*1/2, block_corner[1]+tile_size*1/2,block_corner[2]/2, block_corner[3]/2])
                        pg.draw.rect(screen, (255,128,0), [block_corner[0]+tile_size*1/2, block_corner[1]+tile_size*1/2,block_corner[2]/4, block_corner[3]/4])
                        pg.draw.rect(screen, (255,128,0), [block_corner[0]+tile_size*3/4, block_corner[1]+tile_size*3/4,block_corner[2]/4, block_corner[3]/4])
            
            if bcrd in aux_blockmap:
                tpc = [[block_corner[0]+tile_size*0.3,block_corner[1]+tile_size*0.4], [block_corner[0]+tile_size*0.4,block_corner[1]+tile_size*0.3],[block_corner[0]+tile_size*0.5,block_corner[1]+tile_size*0.4],[block_corner[0]+tile_size*0.4,block_corner[1]+tile_size*0.5]]
                for tile in aux_blockmap[bcrd]:
                    if False: pass
                    elif tile == "temp_a":
                        pg.draw.polygon(screen,(255,0,0),tpc)
                    elif tile == "temp_b":
                        pg.draw.polygon(screen,(0,255,0),tpc)
                    elif tile == "temp_c":
                        pg.draw.polygon(screen,(0,0,255),tpc)
                    elif tile == "temp_d":
                        pg.draw.polygon(screen,(255,255,0),tpc)
                    else:
                        pg.draw.rect(screen, (0,0,0), [block_corner[0], block_corner[1],block_corner[2]/2, block_corner[3]/2])
                        pg.draw.rect(screen, (255,0,255), [block_corner[0], block_corner[1],block_corner[2]/4, block_corner[3]/4])
                        pg.draw.rect(screen, (255,0,255), [block_corner[0]+tile_size*1/4, block_corner[1]+tile_size*1/4,block_corner[2]/4, block_corner[3]/4])

                #if "platform_s_a" in blockmap[bcrd]:
                #    pg.draw.polygon(screen, (200,200,200),(
                #        (block_corner[0]+tile_size, block_corner[1]),
                #        (block_corner[0]+tile_size/2, block_corner[1]),
                #        (block_corner[0]+tile_size, block_corner[1]+tile_size/2)
                #    ))
                #if "platform_s_b" in blockmap[bcrd]:
                #    pg.draw.polygon(screen, (200,200,200),(
                #        (block_corner[0], block_corner[1]+tile_size),
                #        (block_corner[0], block_corner[1]+tile_size/2),
                #        (block_corner[0]+tile_size/2, block_corner[1]+tile_size)
                #    ))
                #if "platform_s_c" in blockmap[bcrd]:
                #    pg.draw.polygon(screen, (200,200,200),(
                #        (block_corner[0], block_corner[1]),
                #        (block_corner[0]+tile_size/2, block_corner[1]),
                #        (block_corner[0], block_corner[1]+tile_size/2)
                #    ))
                #if "platform_s_d" in blockmap[bcrd]:
                #    pg.draw.polygon(screen, (200,200,200),(
                #        (block_corner[0]+tile_size, block_corner[1]+tile_size),
                #        (block_corner[0]+tile_size/2, block_corner[1]+tile_size),
                #        (block_corner[0]+tile_size, block_corner[1]+tile_size/2)
                #    ))

            if bcrd in rail_nodes:
                pg.draw.polygon(screen,(colors[0]),[
                    [block_corner[0]+tile_size*0.4,block_corner[1]+tile_size*0.5],
                    [block_corner[0]+tile_size*0.5,block_corner[1]+tile_size*0.4],
                    [block_corner[0]+tile_size*0.6,block_corner[1]+tile_size*0.5],
                    [block_corner[0]+tile_size*0.5,block_corner[1]+tile_size*0.6],
                ])

                for axis in rail_nodes[bcrd]:
                    for side in rail_nodes[bcrd][axis]:
                        for track in side: rails.append(track)

                if [cam_pos[0]+ty, cam_pos[1]+tx, cam_pos[2]] == m_block and mode == "rail":
                    screen.blit(directional_prism, block_corner)
            
            if min(ay,by) <= cam_pos[1]+tx < max(ay, by) and min(ax,bx) <= cam_pos[0]+ty < max(ax, bx) and min(az, bz) <= cam_pos[2] <= max(az, bz) and mode == "station":
                screen.blit(stat, block_corner[:2])


    for evt in pg.event.get():
        if evt.type == pg.QUIT:
            working = False
        elif evt.type == pg.KEYDOWN:
            pressed.append(evt.key)

            if evt.key == pg.K_MINUS and cur_stat > 0: cur_stat -= 1
            elif evt.key == pg.K_EQUALS: cur_stat += 1

            if evt.key == pg.K_1: select = 0
            if evt.key == pg.K_2: select = 1
            if evt.key == pg.K_3: select = 2
            if evt.key == pg.K_4: select = 3
            if evt.key == pg.K_5: select = 4
            if evt.key == pg.K_6: select = 5
            if evt.key == pg.K_7: select = 6
            if evt.key == pg.K_8: select = 7
            if evt.key == pg.K_9: select = 8

            if evt.key == pg.K_q: pos[2] -= tile_size
            if evt.key == pg.K_e: pos[2] += tile_size

            #if evt.key == pg.K_TAB:
            #    mode = modes[(modes.index(mode)+1)%len(modes)]

            if evt.key == pg.K_F1: mode = modes[0]
            if evt.key == pg.K_F2: mode = modes[1]
            if evt.key == pg.K_F3: mode = modes[2]
            if evt.key == pg.K_F4: mode = modes[3]
            if evt.key == pg.K_F5: mode = modes[4]

                #print(mode)
        elif evt.type == pg.MOUSEBUTTONDOWN:
            clicked = True


    fps = round(clock.get_fps())
    kbd = pg.key.get_pressed()
    speed = 4 if not kbd[pg.K_LSHIFT] else 32

    if kbd[pg.K_w]: pos[0] -= speed
    if kbd[pg.K_s]: pos[0] += speed
    if kbd[pg.K_a]: pos[1] += speed
    if kbd[pg.K_d]: pos[1] -= speed
    

    m_pos = [pg.mouse.get_pos()[i]-screen.get_size()[i]/2 for i in range(2)]
    m_pos[0] = pos[1]-m_pos[0]
    m_pos[1] = pos[0]+m_pos[1]
    m_btn = pg.mouse.get_pressed()
    m_block = [int(m_pos[1]//tile_size), int(m_pos[0]//tile_size)+1, int(pos[2]//tile_size)]
    m_pos = [m_pos[1], m_pos[0], pos[2]]
    crd = f"{m_block[0]}:{m_block[1]}:{m_block[2]}"

    if kbd[pg.K_LALT]:
        a = font.render(f"x: {m_block[0]} | y: {m_block[1]} | z: {m_block[2]}", True, (255,255,255), (10,10,10))
        screen.blit(a, [i+20 for i in pg.mouse.get_pos()])

    if first != [None, None]:
        a = font.render(f"dx: {abs(first[0][0]-m_block[0])} | dy: {abs(first[0][1]-m_block[1])}", True, (255,255,255), (10,10,10))
        screen.blit(a, [i+20 for i in pg.mouse.get_pos()])


    if clicked and not kbd[pg.K_SPACE]:

        if m_btn[0] and mode == "station":
            stations[cur_stat][0] = m_block
        elif m_btn[2] and mode == "station":
            stations[cur_stat][1] = m_block
        elif m_btn[0] and crd not in rail_nodes and mode == "rail":
            rail_nodes[crd] = {
                "x":[[],[]],
                "y":[[],[]]
            }
        elif m_btn[0] and crd in rail_nodes and mode == "rail":
            a = m_pos[0]-m_block[0]*tile_size  > m_block[1]*tile_size-m_pos[1]
            b = tile_size-(m_pos[0]-m_block[0]*tile_size ) > m_block[1]*tile_size-m_pos[1]

            if not a and not b:
                # green: y-
                if first == [None, None]:
                    first = [m_block, "y-"]
                else:
                    second = [m_block, "y-"]
            if a and not b:
                # blue: x+
                if first == [None, None]:
                    first = [m_block, "x+"]
                else:
                    second = [m_block, "x+"]
            if not a and b:
                # red: x-
                if first == [None, None]:
                    first = [m_block, "x-"]
                else:
                    second = [m_block, "x-"]
            if a and b:
                # yellow: y+
                if first == [None, None]:
                    first = [m_block, "y+"]
                else:
                    second = [m_block, "y+"]

            if first != [None, None] and second != [None, None]:
                if first[1] != second[1] and first[0] != second[0]:
                    passed = True
                    s_crd = f"{first[0][0]}:{first[0][1]}:{first[0][2]}"
                    e_crd = f"{second[0][0]}:{second[0][1]}:{second[0][2]}"
                    for link in rail_nodes[s_crd][first[1][0]][0 if first[1][1] == "-" else 1]:
                        if link in rail_nodes[e_crd][second[1][0]][0 if second[1][1] == "-" else 1]:
                            passed = False
                            rail_nodes[s_crd][first[1][0]][0 if first[1][1] == "-" else 1].remove(link)
                            rail_nodes[e_crd][second[1][0]][0 if second[1][1] == "-" else 1].remove(link)

                            break

                    if first[1][0] != second[1][0] and (first[0][0] == second[0][0] or first[0][1] == second[0][1]): passed = False
                    
                    if passed:
                        maxtrack += 1
                        rail_nodes[s_crd][first[1][0]][0 if first[1][1] == "-" else 1].append(maxtrack)
                        rail_nodes[e_crd][second[1][0]][0 if second[1][1] == "-" else 1].append(maxtrack)

                        tracks[maxtrack] = rails_m.Rail(maxtrack)
                        tracks[maxtrack].s_pos = ((first[0][0]+0.5)*tile_size, (first[0][1]+0.5)*tile_size, first[0][2]*tile_size)
                        tracks[maxtrack].e_pos = ((second[0][0]+0.5)*tile_size, (second[0][1]+0.5)*tile_size, second[0][2]*tile_size)
                        tracks[maxtrack].s_axis = first[1][0]
                        tracks[maxtrack].e_axis = second[1][0]
                        tracks[maxtrack].ud = tile_size//2+1
                        tracks[maxtrack].build()
                first = [None, None]
                second = [None, None]


        elif m_btn[2] and crd in rail_nodes and mode == "rail":
            if rail_nodes[crd]["x"] == [[],[]] and rail_nodes[crd]["y"] == [[],[]]:
                rail_nodes.pop(crd)
                if first[0] != None and first[0] == m_block: first = [None, None]

    if not kbd[pg.K_SPACE] and mode == "underlay":
        if m_btn[0]:
            underlay_map[crd] =  underlay_blocks[select] if not kbd[pg.K_LALT] else underlay_blocks_alt[select]
        elif m_btn[2] and crd in underlay_map:
            underlay_map.pop(crd)

    if not kbd[pg.K_SPACE] and mode == "object":
        if m_btn[0]:
            sel = objects[select]
            blockmap[crd] = [sel] if type(sel) == str else sel
        elif m_btn[2] and crd in blockmap:
            blockmap.pop(crd)

    if not kbd[pg.K_SPACE] and mode == "spobject":
        if m_btn[0] and not kbd[pg.K_LALT]:
            sel = special_objects[select]
            aux_blockmap[crd] = [sel] if type(sel) == str else sel
        elif m_btn[0] and kbd[pg.K_LALT]:
            sel = special_objects[select]
            if crd not in blockmap: blockmap[crd] = []

            if sel not in blockmap[crd]:
                blockmap[crd] += [sel] if type(sel) == str else sel
        elif m_btn[2] and crd in aux_blockmap and not kbd[pg.K_LALT]:
            aux_blockmap.pop(crd)
        elif m_btn[2] and crd in blockmap and kbd[pg.K_LALT]:
            blockmap.pop(crd)

    if kbd[pg.K_SPACE] and m_btn[0]:
        pos[1] -= int(old_m_pos[0]-pg.mouse.get_pos()[0])
        pos[0] += int(old_m_pos[1]-pg.mouse.get_pos()[1])

    old_m_pos = pg.mouse.get_pos()
    z = [
        f"pos: {pos}",
        f"fps: {fps}",
        f"edit mode: {mode_str[mode]}",
        "",
        f"current station: {cur_stat}",
        f"current station: {stations[min(cur_stat, len(stations)-1)][2]}",
    ]

    if mode == "underlay": z[3] = f"selection: {underlay_blocks[select] if not kbd[pg.K_LALT] else underlay_blocks_alt[select]}"
    if mode == "object": z[3] = f"selection: {objects[select]}"
    if mode == "spobject": z[3] = f"selection: {special_objects[select]}"

    for enum, line in enumerate(z):
        ptext = font.render(line,True,(240,240,240),(0,0,0))
        screen.blit(ptext,(20,20+30*enum))

    pg.display.update()
    clock.tick(60)

pg.quit()

with open("world.json", mode="w", encoding="utf-8") as f:
    f.write(json.dumps([rail_nodes, blockmap, aux_blockmap, underlay_map, stations], indent=4))