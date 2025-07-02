import pygame as pg
import math

#ISOMETRIC shnyaga (45 gradusiv)
#sqrt(2) = 1.4
#stack_koef = 4

def clamp(base, mn, mx):
    return min(max(mn, base), mx)

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

        self.sprites = {}
        self.train_sprites = {}

        self.blockmap = {}
        self.undermap = {}

        self.rail_nodes = {}
        self.tracks = {}
        
        self.chunks = {
            "active": False,
            "size": 0,
            "data":{

            }
        }

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
        stacks, offset, scale = params
        temp_layers = []

        for i in range(stacks):
            temp_layers.append(
                img.subsurface((128/scale*i,0,128/scale,128/scale))
            )
            temp_layers[-1] = pg.transform.scale(temp_layers[-1],(128,128))
            temp_layers[-1] = pg.transform.rotate(temp_layers[-1],45-add_angle)

            w, h = temp_layers[-1].get_size()

            temp_layers[-1] = pg.transform.scale(temp_layers[-1],(w,h/2))

        tile_surface = pg.Surface((temp_layers[0].get_width(),temp_layers[0].get_height()+((stacks+offset)*4)), pg.SRCALPHA)
    
        for i in range(stacks*4*int(4/scale)):
            layer = temp_layers[int(i/4/int(4/scale))]

            tile_surface.blit(layer, (0,(stacks+offset)*4*int(4/scale)-i))

        w, h = tile_surface.get_size()
        tile_surface = pg.transform.scale(tile_surface,(w*2,h*2)).convert()
        tile_surface.set_colorkey((0,0,0))

        return [tile_surface, (stacks+offset)*4*2*int(4/scale), overdraw]

    def render_train(self, img, params):
        size, stacks, scale = params
        temp_layers = []
        img = img.convert_alpha()

        for i in range(stacks):
            temp_layers.append(
                img.subsurface((size[0]*i,0,size[0],size[1]))
            )
            temp_layers[-1] = pg.transform.scale(temp_layers[-1],(size[0]*scale,size[1]*scale))
        
        surfaces = []

        for ang in range(0,360,1):
            if False:#90 <= ang <= 270:
                surfaces.append(["no"])
            else:
                angle = (ang+45)%360
                layer = pg.transform.rotate(temp_layers[0],angle)


                tile_surface = pg.Surface((layer.get_width(),layer.get_height()/2+((stacks)*4)),pg.SRCALPHA)

                for i in range(stacks*int(4/scale)):
                    layer = temp_layers[i//int(4/scale)]
                    
                    layer = pg.transform.rotate(layer,angle)

                    w_s, h_s = layer.get_size()

                    layer = pg.transform.scale(layer,(w_s,h_s/2))

                    tile_surface.blit(layer, (0,(stacks)*4-i))

                w, h = tile_surface.get_size()
                tile_surface = pg.transform.scale(tile_surface, (w*2, h*2))
                tile_surface = tile_surface.convert()
                tile_surface.set_colorkey((0,0,0))
                surfaces.append((tile_surface,h_s/2))

        return [surfaces, (stacks)*4, size]

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
        player_coord = self.translate_to((0,0))
        dz = round(self.pos[2]/tile_size)

        for dy in range(bm_pos[1]-a,bm_pos[1]+a):

            for dx in range(bm_pos[0]-a,bm_pos[0]+a):
                bcrd = f"{dx}:{dy}:{dz}"


                crdb = self.translate_to((dx*tile_size, dy*tile_size))

                if bcrd in self.blockmap:
                    tile_center = [crdb[0], crdb[1]+90]
                    for tile in self.blockmap[bcrd]:
                        if tile in self.sprites:
                            tile_sprite = self.sprites[tile][0]

                            draw_queue.append([
                                (dx*tile_size+self.sprites[tile][2][0],dy*tile_size+self.sprites[tile][2][1]),
                                tile_sprite,
                                (
                                    round(tile_center[0]-m_tile_w//2),
                                    round(tile_center[1]-m_tile_h//2-self.sprites[tile][1])
                                )

                            ])

                
                if bcrd in self.undermap:
                    drc = (crdb[0]-180, crdb[1]-4)
                    if self.undermap[bcrd] == "base":
                        screen.blit(self.sprites["under_base"][0], drc)
                    elif self.undermap[bcrd] == "corner_a":
                        screen.blit(self.sprites["under_crna"][0], drc)
                    elif self.undermap[bcrd] == "corner_b":
                        screen.blit(self.sprites["under_crnb"][0], drc)
                    elif self.undermap[bcrd] == "corner_c":
                        screen.blit(self.sprites["under_crnc"][0], drc)
                    elif self.undermap[bcrd] == "corner_d":
                        screen.blit(self.sprites["under_crnd"][0], drc)

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
        for dy in range(bm_pos[1]-a,bm_pos[1]+a):
            p1 = self.translate_to(((bm_pos[0]-a)*tile_size,dy*tile_size))
            p2 = self.translate_to(((bm_pos[0]+a)*tile_size,dy*tile_size))
            pg.draw.line(screen, grid_color,p1,p2,4)

        for dx in range(bm_pos[0]-a,bm_pos[0]+a):
            p1 = self.translate_to((dx*tile_size,(bm_pos[1]-a)*tile_size))
            p2 = self.translate_to((dx*tile_size,(bm_pos[1]+a)*tile_size))
            pg.draw.line(screen, grid_color,p1,p2,4)

        for train in trains: # проходка по всем поездам

            if (self.pos[0]-21*tile_size < train.pos[0] < self.pos[0]+21*tile_size and 
                self.pos[1]-21*tile_size < train.pos[1] < self.pos[1]+21*tile_size and
                train.type != None): # если видно

                
                dh = abs(int(train.pos[2])-int(self.pos[2])) # разница высот
                if 0 <= dh*2 <= tile_size:
                     
                    angle = round(train.angle//1) 
                    angle %= 360
                    array_entry = self.train_sprites[train.type] #нормализация угла
                    
                    center_pos = self.translate_to(train.pos) #центровина вагона
                    sprite = pg.transform.scale(array_entry[0][angle][0],(
                        array_entry[0][angle][0].get_width(),
                        array_entry[0][angle][0].get_height())
                    )
                    if dh != 0:
                        sprite.set_alpha(clamp(255*(1-dh*2/tile_size), 0,255))
                    
                    draw_queue.append([
                        [
                            train.pos[0]+abs(train.size[0]*math.sin(math.radians(train.angle)))/2+abs(train.size[1]*math.cos(math.radians(train.angle)))/2,
                            train.pos[1]+abs(train.size[0]*math.cos(math.radians(train.angle)))/2+abs(train.size[1]*math.sin(math.radians(train.angle)))/2,
                        ],
                        sprite,
                        (
                        round(center_pos[0]-array_entry[0][angle][0].get_width()//2),
                        round(center_pos[1]-array_entry[0][angle][1]-array_entry[1]*2)
                        )
                    ])
        

        for element in sorted(draw_queue,key=lambda x:x[0][1]+x[0][0]):
            screen.blit(element[1],element[2])

        draw_queue = []
        
                
        for element in sorted(draw_queue,key=lambda x:x[0]):
            screen.blit(element[1],element[2])
        
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




