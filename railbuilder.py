# fun railbuilding thingy

import pygame as pg
import math
import rails2d
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
    rail_nodes, blockmap, stations = q

tracks = {

}

for node in rail_nodes:
    sx, sy = [(i+0.5)*tile_size for i in map(int,node.split(":"))]
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
pos = [0,0]
m_block = [14,88]
old_m_pos = (0,0)

while working:
    if cur_stat+1 > len(stations):
        stations.append([(0,0), (1,1), "unnamed", "lines"])

    clicked = False
    released = False
    pressed = []
    screen.fill((240,240,240))

    cam_pos = (pos[0]//tile_size, pos[1]//tile_size)
    sw, sh = screen.get_size()
    rails = []
    az = pg.Surface([tile_size]*2)
    az.fill((240,0,0))
    az.set_alpha(64)
    ax, ay = stations[cur_stat][0]
    bx, by = stations[cur_stat][1]

    for ty in range(-tiles_disp[1],tiles_disp[1]+1):
        for tx in range(-tiles_disp[0],tiles_disp[0]+1):
            block_corner = (sw/2-(tx*tile_size-pos[1]%tile_size), sh/2+ty*tile_size-pos[0]%tile_size, tile_size, tile_size)
            if (cam_pos[0]+tx)%2 == (cam_pos[1]+ty)%2:
                pg.draw.rect(screen, (200,200,200), block_corner)

            a = font_alt.render(f"{cam_pos[0]+ty}:{cam_pos[1]+tx}", True, (0,0,0))
            screen.blit(a, block_corner)

            if f"{cam_pos[0]+ty}:{cam_pos[1]+tx}" in blockmap:
                if blockmap[f"{cam_pos[0]+ty}:{cam_pos[1]+tx}"][0] == "platform":
                    pg.draw.rect(screen, (100,100,100), block_corner)
                elif blockmap[f"{cam_pos[0]+ty}:{cam_pos[1]+tx}"][0] == "platform_e_x_r":
                    pg.draw.rect(screen, (100,100,100), [block_corner[0]+tile_size*3/4, block_corner[1],block_corner[2]/4, block_corner[3]])
                elif blockmap[f"{cam_pos[0]+ty}:{cam_pos[1]+tx}"][0] == "platform_e_x_l":
                    pg.draw.rect(screen, (100,100,100), [block_corner[0], block_corner[1],block_corner[2]/4, block_corner[3]])
                elif blockmap[f"{cam_pos[0]+ty}:{cam_pos[1]+tx}"][0] == "platform_e_y_r":
                    pg.draw.rect(screen, (100,100,100), [block_corner[0], block_corner[1]+tile_size*3/4,block_corner[2], block_corner[3]/4])
                elif blockmap[f"{cam_pos[0]+ty}:{cam_pos[1]+tx}"][0] == "platform_e_y_l":
                    pg.draw.rect(screen, (100,100,100), [block_corner[0], block_corner[1],block_corner[2], block_corner[3]/4])
                
                if "platform_s_a" in blockmap[f"{cam_pos[0]+ty}:{cam_pos[1]+tx}"]:
                    pg.draw.polygon(screen, (200,200,200),(
                        (block_corner[0]+tile_size, block_corner[1]),
                        (block_corner[0]+tile_size/2, block_corner[1]),
                        (block_corner[0]+tile_size, block_corner[1]+tile_size/2)
                    ))
                if "platform_s_b" in blockmap[f"{cam_pos[0]+ty}:{cam_pos[1]+tx}"]:
                    pg.draw.polygon(screen, (200,200,200),(
                        (block_corner[0], block_corner[1]+tile_size),
                        (block_corner[0], block_corner[1]+tile_size/2),
                        (block_corner[0]+tile_size/2, block_corner[1]+tile_size)
                    ))
                if "platform_s_c" in blockmap[f"{cam_pos[0]+ty}:{cam_pos[1]+tx}"]:
                    pg.draw.polygon(screen, (200,200,200),(
                        (block_corner[0], block_corner[1]),
                        (block_corner[0]+tile_size/2, block_corner[1]),
                        (block_corner[0], block_corner[1]+tile_size/2)
                    ))
                if "platform_s_d" in blockmap[f"{cam_pos[0]+ty}:{cam_pos[1]+tx}"]:
                    pg.draw.polygon(screen, (200,200,200),(
                        (block_corner[0]+tile_size, block_corner[1]+tile_size),
                        (block_corner[0]+tile_size/2, block_corner[1]+tile_size),
                        (block_corner[0]+tile_size, block_corner[1]+tile_size/2)
                    ))

            if f"{cam_pos[0]+ty}:{cam_pos[1]+tx}" in rail_nodes:
                pg.draw.polygon(screen,(colors[0]),[
                    [block_corner[0]+tile_size*0.4,block_corner[1]+tile_size*0.5],
                    [block_corner[0]+tile_size*0.5,block_corner[1]+tile_size*0.4],
                    [block_corner[0]+tile_size*0.6,block_corner[1]+tile_size*0.5],
                    [block_corner[0]+tile_size*0.5,block_corner[1]+tile_size*0.6],
                ])

                for axis in rail_nodes[f"{cam_pos[0]+ty}:{cam_pos[1]+tx}"]:
                    for side in rail_nodes[f"{cam_pos[0]+ty}:{cam_pos[1]+tx}"][axis]:
                        for track in side: rails.append(track)

                if [cam_pos[0]+ty, cam_pos[1]+tx] == m_block:
                    screen.blit(directional_prism, block_corner)
            
            if min(ay,by) <= cam_pos[1]+tx < max(ay, by) and min(ax,bx) <= cam_pos[0]+ty < max(ax, bx):
                screen.blit(az, block_corner[:2])

    for track in rails:
        inf = tracks[track]
        p = []
        for point in inf.points:
            p.append((
                sw/2-(point[1]-pos[1])+tile_size,
                sh/2+(point[0]-pos[0])
            ))
        
        pg.draw.lines(screen, colors[0], False, p, 2)

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
        elif evt.type == pg.MOUSEBUTTONDOWN:
            clicked = True


    fps = round(clock.get_fps())
    kbd = pg.key.get_pressed()
    speed = 4 if not kbd[pg.K_LSHIFT] else 32

    if kbd[pg.K_UP]: pos[0] -= speed
    if kbd[pg.K_DOWN]: pos[0] += speed
    if kbd[pg.K_LEFT]: pos[1] += speed
    if kbd[pg.K_RIGHT]: pos[1] -= speed

    m_pos = [pg.mouse.get_pos()[i]-screen.get_size()[i]/2 for i in range(2)]
    m_pos[0] = pos[1]-m_pos[0]
    m_pos[1] = pos[0]+m_pos[1]
    m_btn = pg.mouse.get_pressed()
    m_block = [int(m_pos[1]//tile_size), int(m_pos[0]//tile_size)+1]
    m_pos = [m_pos[1], m_pos[0]]

    if clicked and not kbd[pg.K_SPACE]:
        crd = f"{m_block[0]}:{m_block[1]}"

        if m_btn[0] and kbd[pg.K_LALT]:
            if kbd[pg.K_LSHIFT]:
                sel = ['platform', 'platform_s_a', 'platform_s_b', 'platform_s_c' , 'platform_s_d'][select]
            else:
                sel = ['platform', 'platform_e_x_l', 'platform_e_x_r', 'platform_e_y_l' , 'platform_e_y_r'][select]

            if sel in ['platform', 'platform_e_x_l', 'platform_e_x_r', 'platform_e_y_l' , 'platform_e_y_r'] and crd not in blockmap:
                blockmap[crd] = [sel]
            elif sel not in ['platform', 'platform_e_x_l', 'platform_e_x_r', 'platform_e_y_l' , 'platform_e_y_r'] and crd in blockmap and sel not in blockmap[crd]:
                blockmap[crd].append(sel)

        elif m_btn[0] and kbd[pg.K_LCTRL]:
            stations[cur_stat][0] = m_block
        elif m_btn[2] and kbd[pg.K_LCTRL]:
            stations[cur_stat][1] = m_block
        elif m_btn[0] and crd not in rail_nodes and not kbd[pg.K_LALT]:
            rail_nodes[crd] = {
                "x":[[],[]],
                "y":[[],[]]
            }
        elif m_btn[0] and crd in rail_nodes:
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
                    s_crd = f"{first[0][0]}:{first[0][1]}"
                    e_crd = f"{second[0][0]}:{second[0][1]}"
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

                        tracks[maxtrack] = rails2d.Rail(maxtrack)
                        tracks[maxtrack].s_pos = [(first[0][i]+0.5)*tile_size for i in range(2)]
                        tracks[maxtrack].e_pos = [(second[0][i]+0.5)*tile_size for i in range(2)]
                        tracks[maxtrack].s_axis = first[1][0]
                        tracks[maxtrack].e_axis = second[1][0]
                        tracks[maxtrack].build()
                first = [None, None]
                second = [None, None]


        elif m_btn[2] and crd in rail_nodes and not kbd[pg.K_LALT]:
            if rail_nodes[crd]["x"] == [[],[]] and rail_nodes[crd]["y"] == [[],[]]:
                rail_nodes.pop(crd)
                if first[0] != None and first[0] == m_block: first = [None, None]

        elif m_btn[2] and crd in blockmap and kbd[pg.K_LALT]:
            blockmap.pop(crd)

    if kbd[pg.K_SPACE] and m_btn[0]:
        pos[1] -= int(old_m_pos[0]-pg.mouse.get_pos()[0])
        pos[0] += int(old_m_pos[1]-pg.mouse.get_pos()[1])

    old_m_pos = pg.mouse.get_pos()

    z = [
        f"pos: {pos}",
        f"fps: {fps}",
        f"selected: {['platform', 'edge vertical l', 'edge vertical r', 'edge horizontal up' , 'edge horizontal down'][select]}",
        f"current station: {cur_stat}",
        f"current station: {stations[min(cur_stat, len(stations)-1)][2]}",
    ]
    for enum, line in enumerate(z):
        ptext = font.render(line,True,(240,240,240),(0,0,0))
        screen.blit(ptext,(20,20+30*enum))

    pg.display.update()
    clock.tick(60)

pg.quit()

with open("world.json", mode="w", encoding="utf-8") as f:
    f.write(json.dumps([rail_nodes, blockmap, stations], indent=4))