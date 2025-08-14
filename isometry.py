import pygame as pg
import math

#ISOMETRIC shnyaga (45 gradusiv)
#sqrt(2) = 1.4
#stack_koef = 4

def clamp(base, mn, mx):
    return min(max(mn, base), mx)

def copy_surf(surf):
    return pg.transform.rotate(surf,0)

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

class Camera():
    def __init__(self, camera_size):
        self.pos = [0,0,0]
        self.camera_size = camera_size
        self.debug = False
        self.scale = 1
        self.mode_2x = True

        self.sprites = {}
        self.train_sprites = {}

        self.blockmap = {}
        self.auxmap = {}
        self.undermap = {}

        self.rail_nodes = {}
        self.tracks = {}

        self.sounds = {}
        for i in range(30): self.sounds[f"engine_{i}"] = pg.mixer.Sound(f"res/sound/engine_{i}.wav")
        for sound in self.sounds: self.sounds[sound].set_volume(0.05)
        
        self.chunks = {
            "active": False,
            "size": 0,
            "data":{

            }
        }
        self.sound_play = {}

        self.z = pg.Surface(camera_size)
        self.z.fill((128,128,128))
        self.z.set_alpha(64)
        self.flag = False

    def chunk(self, chunk_size):
        self.chunks["active"] = True
        self.chunks["size"] = chunk_size

        for block in self.blockmap:
            x, y = map(int, block.split(":"))
            chx, chy = int(x//chunk_size), int(y//chunk_size)

            if (chx, chy) not in self.chunks["data"]: self.chunks["data"][(chx, chy)] = []


    def translate_to(self, coordinates):
        x, y = coordinates[:2]
        x -= self.pos[0]
        y -= self.pos[1]

        scale = 90/128
        x *= scale
        y *= scale
        dx = ((x - y))
        dy = ((x + y)*0.5)
        dx += self.camera_size[0]/2
        dy += self.camera_size[1]/2

        return (int(dx), int(dy))

    def translate_from(self, coordinates):
        dx, dy = coordinates
        dx -= self.camera_size[0]/2
        dy -= self.camera_size[1]/2

        x = 0.7*(dx+dy*2)
        y = dy*2.8-x

        x, y = round(x),round(y)

        return (x, y)

    def render_tile(self, img, params, overdraw, add_angle = 0):
        stacks, offset, scale, duplication = params
        temp_layers = []

        for i in range(stacks):
            temp_layers.append(
                img.subsurface((128/scale*i,0,128/scale,128/scale)).convert_alpha()
            )
             
            if self.mode_2x: temp_layers[-1] = pg.transform.scale(temp_layers[-1],(256,256))
            else: temp_layers[-1] = pg.transform.scale(temp_layers[-1],(128,128))
            
            if type(add_angle) != int: temp_layers[-1] = pg.transform.flip(temp_layers[-1], add_angle[0], add_angle[1])

            if type(add_angle) == int: temp_layers[-1] = pg.transform.rotate(temp_layers[-1],45-add_angle)
            elif type(add_angle) != int and len(add_angle) == 3: temp_layers[-1] = pg.transform.rotate(temp_layers[-1],45-add_angle[2])
            else: temp_layers[-1] = pg.transform.rotate(temp_layers[-1],45)

            w, h = temp_layers[-1].get_size()

            temp_layers[-1] = pg.transform.scale(temp_layers[-1],(w,h/2))
        
        #temp_layers *= duplication
        if self.mode_2x: duplication*=2

        tile_surface = pg.Surface((temp_layers[0].get_width(),temp_layers[0].get_height()+(len(temp_layers)*scale*duplication)), pg.SRCALPHA)
        i = 0
        base_ht = len(temp_layers)*scale*duplication
        for layer in temp_layers:
            for l in range(scale*duplication):
                tile_surface.blit(layer, (0,base_ht-i))
                i+=1

        w, h = tile_surface.get_size()
        if not self.mode_2x: 
            base_ht *= 2
            tile_surface = pg.transform.scale(tile_surface,(w*2,h*2))
        tile_surface = tile_surface.convert_alpha()
        w, h = tile_surface.get_size()

        return [tile_surface, h-180+offset*scale*2-6, overdraw]

    def render_train(self, directory, full_params):
        train_id = full_params["id"]
        self.train_sprites[train_id] = []
        base_sheet = pg.image.load(directory+full_params["spritesheet"]).convert()
        for state in full_params["sprite_maps"]:
            if full_params["prerendered"]:
                self.train_sprites[train_id].append(self.load_prerendered_train(directory+f"prerender_train{'2x' if self.mode_2x else ''}/{train_id}_{state}_", full_params["sprite_maps"][state][3]*full_params["sprite_maps"][state][4]*2))
            else:
                st = full_params["sprite_maps"][state]
                self.train_sprites[train_id].append(self.render_train_state(base_sheet.subsurface(st[0],st[1],st[2][0]*st[3],st[2][1]),st[2:]))

    def load_prerendered_train(self, general_path, ii):
        sprites = []
        for i in range(0,360):
            tmp = pg.image.load(general_path+str(i)+".png")
            tmp = tmp.convert()
            tmp.set_colorkey((0,0,0))
            sprites.append((tmp, (tmp.get_height()+ii)//2))
        return [sprites]



    def render_train_state(self, img, params):
        size, stacks, scale = params
        temp_layers = []
        
        img = img.convert_alpha()

        for i in range(stacks):
            tmp = img.subsurface((size[0]*i,0,size[0],size[1]))
            if self.mode_2x:
                for i in range(scale*2): temp_layers.append(pg.transform.scale(tmp,(size[0]*scale*2,size[1]*scale*2)))
            else:
                for i in range(scale): temp_layers.append(pg.transform.scale(tmp,(size[0]*scale,size[1]*scale)))
        
        surfaces = []

        for ang in range(0,360,1):
            angle = (ang+45)%360
            layer = pg.transform.rotate(temp_layers[0],angle)


            tile_surface = pg.Surface((layer.get_width(),layer.get_height()/2+len(temp_layers)),pg.SRCALPHA)
            base_h = layer.get_height()/4
            i = 0

            for l in range(len(temp_layers)):
                layer = temp_layers[l]
                
                layer = pg.transform.rotate(layer,angle)

                w_s, h_s = layer.get_size()

                layer = pg.transform.scale(layer,(w_s,h_s/2))

                tile_surface.blit(layer, (0,len(temp_layers)-i))
                i+=1

            w, h = tile_surface.get_size()
            if not self.mode_2x: 
                tile_surface = pg.transform.scale(tile_surface, (w*2, h*2))
                base_h*=2
                h*=2
            tile_surface = tile_surface.convert()
            tile_surface.set_colorkey((0,0,0))
            surfaces.append((tile_surface,h-base_h))

        return [surfaces, size]

    def draw_map(self, trains, disp, debug_flag = False):
        ground_color = pg.Color("#404040")
        grid_color = pg.Color("#505050")
        #ground_color = pg.Color("#f7f1d2")
        #grid_color = pg.Color("#efe9cb")

        tile_size = 256
        bm_pos = (int(self.pos[0])//tile_size,int(self.pos[1])//tile_size)

        screen = disp
        screen.set_colorkey((0,0,0))
        screen.fill(ground_color)

        cnt = 0

        m_tile_w = 360
        m_tile_h = 180
        a = max(int(screen.get_width()//m_tile_w+1), int(screen.get_height()//m_tile_h+1))+3
        tracks = []

        draw_queue = []
        aux_draw_queue = []
        player_coord = self.translate_to((0,0))
        dz = round(self.pos[2]/tile_size)
        height_diff = abs(self.pos[2]-dz*tile_size)
        opacity = int(clamp(255*(1-height_diff*2/tile_size), 0, 255)) if height_diff != 0 else 255

        for dy in range(bm_pos[1]-a,bm_pos[1]+a):

            for dx in range(bm_pos[0]-a,bm_pos[0]+a):
                bcrd = f"{dx}:{dy}:{dz}"


                crdb = self.translate_to((dx*tile_size, dy*tile_size))
                drc = (crdb[0]-180, crdb[1]-4)
                tile_center = [crdb[0], crdb[1]+90]

                if bcrd in self.blockmap:
                    for tile in self.blockmap[bcrd]:
                        if tile in self.sprites:
                            tile_sprite = self.sprites[tile][0]

                            draw_queue.append([
                                (dx*tile_size+self.sprites[tile][2][0],dy*tile_size+self.sprites[tile][2][1]),
                                tile_sprite,
                                (
                                    drc[0],
                                    drc[1]-self.sprites[tile][1]
                                )

                            ])
                
                if bcrd in self.auxmap:
                    for tile in self.auxmap[bcrd]:
                        if tile in self.sprites:
                            tile_sprite = self.sprites[tile][0]

                            aux_draw_queue.append([
                                (dx*tile_size+self.sprites[tile][2][0],dy*tile_size+self.sprites[tile][2][1]),
                                tile_sprite,
                                (
                                    drc[0],
                                    drc[1]-self.sprites[tile][1]
                                )

                            ])

                
                if bcrd in self.undermap:
                    instablit = [
                        "base", "base_spec", "corner_a", "corner_b", "corner_c","corner_d",
                        "bridge_base", "bridge_corner_a", "bridge_corner_b", "bridge_corner_c", "bridge_corner_d"
                    ]
                    if self.undermap[bcrd] in instablit:
                        sp = self.sprites[f"u_{self.undermap[bcrd]}"][0]
                        sp.set_alpha(opacity)
                        screen.blit(sp, (
                            drc[0],
                            drc[1]-self.sprites[f"u_{self.undermap[bcrd]}"][1]
                        ))
                    elif "wall" in self.undermap[bcrd] or "fence" in self.undermap[bcrd]:
                        sprite = f"u_{self.undermap[bcrd]}"
                        sp = self.sprites[sprite][0]
                        sp.set_alpha(opacity)
                        draw_queue.append([
                                (dx*tile_size+self.sprites[sprite][2][0],dy*tile_size+self.sprites[sprite][2][1]),
                                sp,
                                (
                                    drc[0],
                                    drc[1]-self.sprites[f"u_{self.undermap[bcrd]}"][1]
                                )


                            ])

                if bcrd in self.rail_nodes:
                    for track in self.rail_nodes[bcrd]["x"][0]+self.rail_nodes[bcrd]["x"][1]+self.rail_nodes[bcrd]["y"][0]+self.rail_nodes[bcrd]["y"][1]:
                        tracks.append(track)

                cnt+=1

                if self.debug:

                    p1 = self.translate_to(((dx)*tile_size,dy*tile_size))
                    p2 = self.translate_to(((dx+1)*tile_size,dy*tile_size))
                    p3 = self.translate_to(((dx+1)*tile_size,(dy+1)*tile_size))
                    p4 = self.translate_to((dx*tile_size,(dy+1)*tile_size))

                    pg.draw.lines(screen, (0,0,0),True,(p1,p2,p3,p4),2)
                
        for track in tracks:
            inf = self.tracks[track]
            l_stack = ["",""]
            r_stack = ["", ""]
            if inf.enable_underlay:
                for i in range(len(inf.raw_up_l)):

                    l_p = inf.underlay_points_l[i]
                    l_stack = [l_stack[1], (l_p[0]+player_coord[0], l_p[1]+player_coord[1], l_p[2])]
                    
                    r_p = inf.underlay_points_r[i]
                    r_stack = [r_stack[1], (r_p[0]+player_coord[0], r_p[1]+player_coord[1], r_p[2])]

                    if l_stack[0] != "":
                        dh = abs((l_stack[0][2]+l_stack[1][2])/2-self.pos[2])
                        if dh <= tile_size/2:
                            pg.draw.polygon(screen, [int(clamp(80-16*(dh*2/tile_size), 64, 80))]*3, [i[:2] for i in l_stack+r_stack[::-1]])

        for i, track in enumerate(tracks): #стековая рисовальня путей
            stack = ["",""]

            for point in self.tracks[track].l_track+["",""]+self.tracks[track].r_track: # левая рельса - пропуск - правая рельса

                if point != "": point = [point[0]+player_coord[0], point[1]+player_coord[1], point[2]]
                stack = [stack[1],point]
                if stack[0] != "" and stack[1] != "": # если стак вообще есть смысл ворошить (без пропусков), то рисуем
                    dh = abs((stack[0][2]+stack[1][2])/2-self.pos[2])
                    color = [int(clamp(16+48*(dh*2/tile_size), 16, 64))]

                    if 0 <= stack[0][0] <= screen.get_width() and 0 <= stack[0][1] <= screen.get_height(): drawstack = stack
                    else: drawstack = stack[::-1]
                    
                    pg.draw.line(screen,color*3,
                        drawstack[0][:2],
                        drawstack[1][:2],
                        int(4)
                        )

        z = []

        #for dy in range(bm_pos[1]-a,bm_pos[1]+a):
        #    p1 = self.translate_to(((bm_pos[0]-a)*tile_size,dy*tile_size))
        #    p2 = self.translate_to(((bm_pos[0]+a)*tile_size,dy*tile_size))
        #    pg.draw.line(screen, grid_color,p1,p2,4)
        #for dx in range(bm_pos[0]-a,bm_pos[0]+a):
        #    p1 = self.translate_to((dx*tile_size,(bm_pos[1]-a)*tile_size))
        #    p2 = self.translate_to((dx*tile_size,(bm_pos[1]+a)*tile_size))
        #    pg.draw.line(screen, grid_color,p1,p2,4)

        sp_updates = {}

        for train in trains: # проходка по всем поездам

            if (self.pos[0]-21*tile_size < train.pos[0] < self.pos[0]+21*tile_size and 
                self.pos[1]-21*tile_size < train.pos[1] < self.pos[1]+21*tile_size and
                train.type != None): # если видно

                dl = ((self.pos[0]-train.pos[0])**2+(self.pos[1]-train.pos[1])**2+(self.pos[2]-train.pos[2])**2)**0.5
                if train.c in sp_updates:
                    if dl < sp_updates[train.c][1]: sp_updates[train.c][1] = dl
                else: sp_updates[train.c] = [train.vel, dl]

                
                dh = abs(int(train.pos[2])-int(self.pos[2])) # разница высот
                if 0 <= dh*2 <= tile_size:
                     
                    angle = round(train.angle//1) 
                    angle %= 360
                    center_pos = self.translate_to(train.pos) #центровина вагона

                    if 135 <= angle <= 135+180: door_sel = train.doors[(1+train.flipped)%2]
                    else: door_sel = train.doors[int(train.flipped)]
                    array_entry = self.train_sprites[train.type][door_sel] #нормализация угла
                    
                    center_pos = self.translate_to(train.pos) #центровина вагона
                    sprite = array_entry[0][angle][0].copy()
                    if dh != 0:
                        sprite.set_alpha(clamp(255*(1-dh*2/tile_size), 0,255))
                    
                    draw_queue.append([
                        [
                            train.pos[0]+abs(train.size[0]*math.sin(math.radians(train.angle)))/2+abs(train.size[1]*math.cos(math.radians(train.angle)))/2,
                            train.pos[1]+abs(train.size[0]*math.cos(math.radians(train.angle)))/2+abs(train.size[1]*math.sin(math.radians(train.angle)))/2+24,
                        ],
                        sprite,
                        (
                        round(center_pos[0]-array_entry[0][angle][0].get_width()//2),
                        round(center_pos[1]-array_entry[0][angle][1])
                        )
                    ])


        for c in sp_updates:
            tr = sp_updates[c]
            if c not in self.sound_play:
                self.sound_play[c] = [pg.mixer.find_channel(), round(tr[0]/7)]
                self.sound_play[c][0].play(self.sounds[f"engine_{max(0,min(29,self.sound_play[c][1]))}"],-1)
                if tr[0] == 0: self.sound_play[c][0].set_volume(0)
                else: self.sound_play[c][0].set_volume(1-tr[1]/256/8)
            else:
                if round(tr[0]/7) != self.sound_play[c][1]:
                    self.sound_play[c][1] = round(tr[0]/7)
                    self.sound_play[c][0].play(self.sounds[f"engine_{max(0,min(29,self.sound_play[c][1]))}"],-1)
                if tr[0] == 0: self.sound_play[c][0].set_volume(0)
                else:self.sound_play[c][0].set_volume(1-tr[1]/256/8)

        for_removal = []
        for c in self.sound_play:
            if c not in sp_updates:
                self.sound_play[c][0].stop()
                for_removal.append(c)

        for c in for_removal: self.sound_play.pop(c)
        

        for element in sorted(draw_queue,key=lambda x:x[0][1]+x[0][0]):
            if element[2][0] > self.camera_size[0] or element[2][1] > self.camera_size[1]: pass
            else: screen.blit(element[1],element[2])

                
        for element in sorted(aux_draw_queue,key=lambda x:x[0]):
            if element[2][0] > self.camera_size[0] or element[2][1] > self.camera_size[1]: pass
            else: screen.blit(element[1],element[2])

        
        # без масштабирование потому что FPS 60 -> ~0
        #for p in z:
        #    pg.draw.circle(screen,(255,0,0),p[0],6)
        #    pg.draw.line(screen,(255,0,0),p[0],p[1],4)
        #if self.scale > 1:
        #    dw, dh = [int(i/self.scale) for i in self.camera_size]
        #    screen = pg.transform.scale(screen.subsurface(dw/2,dh/2,dw,dh),self.camera_size)
        #elif self.scale < 1:
        #    screen = pg.transform.scale(screen,self.camera_size)

        if self.flag:screen.blit(self.z,(0,0))

        return screen




