import pygame as pg
import rails

#ISOMETRIC shnyaga (45 gradusiv)
#sqrt(2) = 1.4
#stack_koef = 4

class Camera():
    def __init__(self, camera_size):
        self.pos = [0,0]
        self.camera_size = camera_size
        self.debug = False
        self.scale = 1

        self.sprites = {}
        self.train_sprites = {}

        self.blockmap = {}

        self.rail_nodes = {}
        self.tracks = {}
        
        self.z = pg.Surface(camera_size)
        self.z.fill((128,128,128))
        self.z.set_alpha(64)
        self.flag = False


    def translate_to(self, coordinates):
        x, y = coordinates
        x -= self.pos[0]
        y -= self.pos[1]

        scale = 90/128
        x *= scale
        y *= scale
        dx = ((x - y))
        dy = ((x + y)*0.5)
        dx += (self.camera_size[0]/min(1,self.scale))/2
        dy += (self.camera_size[1]/min(1,self.scale))/2

        return (dx, dy)

    def translate_from(self, coordinates):
        dx, dy = coordinates
        dx -= self.camera_size[0]/2
        dy -= self.camera_size[1]/2

        x = 0.7*(dx+dy*2)
        y = dy*2.8-x

        x, y = round(x),round(y)

        return (x, y)

    def render_tile(self, img, params):
        stacks, offset, scale = params
        temp_layers = []

        for i in range(stacks):
            temp_layers.append(
                img.subsurface((128/scale*i,0,128/scale,128/scale))
            )
            temp_layers[-1] = pg.transform.scale(temp_layers[-1],(128,128))
            temp_layers[-1] = pg.transform.rotate(temp_layers[-1],45)

            w, h = temp_layers[-1].get_size()

            temp_layers[-1] = pg.transform.scale(temp_layers[-1],(w,h/2))

        tile_surface = pg.Surface((temp_layers[0].get_width(),temp_layers[0].get_height()+((stacks+offset)*4)), pg.SRCALPHA)
    
        for i in range(stacks*4*int(4/scale)):
            layer = temp_layers[int(i/4/int(4/scale))]

            tile_surface.blit(layer, (0,(stacks+offset)*4*int(4/scale)-i))

        w, h = tile_surface.get_size()
        tile_surface = pg.transform.scale(tile_surface,(w*2,h*2)).convert()
        tile_surface.set_colorkey((0,0,0))

        return [tile_surface, (stacks+offset)*4*2*int(4/scale)]

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
                tile_surface = tile_surface.convert()
                tile_surface.set_colorkey((0,0,0))
                surfaces.append((tile_surface,h_s/2))

        return [surfaces, (stacks)*4, size]

    def draw_map(self, trains, font):
        ground_color = pg.Color("#f7f1d2")
        grid_color = pg.Color("#efe9cb")

        tile_size = 256
        bm_pos = (int(self.pos[0])//tile_size,int(self.pos[1])//tile_size)
        chunk_pos = (bm_pos[0]//21, bm_pos[1]//21)

        screen = pg.Surface([i/min(1,self.scale) for i in self.camera_size],pg.SRCALPHA).convert()
        screen.set_colorkey((0,0,0))
        screen.fill(ground_color)

        cnt = 0
        a = int(5/(self.scale/2))

        millimetrovka = self.sprites["millimetrovka"][0]
        m_tile_w, m_tile_h = [i for i in millimetrovka.get_size()]
        millimetrovka = pg.transform.scale(millimetrovka,(m_tile_w, m_tile_h-4))
        #m_tile_w, m_tile_h = [i*2 for i in millimetrovka.get_size()]
        #millimetrovka = pg.transform.scale(millimetrovka,(m_tile_w, m_tile_h-4))
        tracks = []

        draw_queue = []

        for dy in range(bm_pos[1]-a,bm_pos[1]+a):

            for dx in range(bm_pos[0]-a,bm_pos[0]+a):



                #screen.blit(millimetrovka,
                #    (
                #        round(tile_center[0]-m_tile_w//2),
                #        round(tile_center[1]-m_tile_h//2)
                #    )
                #)

                if f"{dx}:{dy}" in self.blockmap:
                    tile_center = self.translate_to(((dx+0.5)*tile_size,(dy+0.5)*tile_size))
                    for tile in self.blockmap[f"{dx}:{dy}"]:
                        if tile in self.sprites:
                            tile_sprite = self.sprites[tile][0]
                            #tile_w, tile_h = [i for i in tile_sprite.get_size()]
                            tile_w, tile_h = tile_sprite.get_size()

                            draw_queue.append([
                                (dx+dy+1)*256,
                                tile_sprite,
                                (
                                    round(tile_center[0]-tile_w//2),
                                    round(tile_center[1]-m_tile_h//2-self.sprites[tile][1])
                                )

                            ])

                if f"{dx}:{dy}" in self.rail_nodes:
                    for track in self.rail_nodes[f"{dx}:{dy}"]["x"][0]+self.rail_nodes[f"{dx}:{dy}"]["x"][1]+self.rail_nodes[f"{dx}:{dy}"]["y"][0]+self.rail_nodes[f"{dx}:{dy}"]["y"][1]:
                        tracks.append(track)

                cnt+=1

                if self.debug:

                    p1 = self.translate_to(((dx)*tile_size,dy*tile_size))
                    p2 = self.translate_to(((dx+1)*tile_size,dy*tile_size))
                    p3 = self.translate_to(((dx+1)*tile_size,(dy+1)*tile_size))
                    p4 = self.translate_to((dx*tile_size,(dy+1)*tile_size))

                    pg.draw.lines(screen, (0,0,0),True,(p1,p2,p3,p4),2)

                    #k = font.render(f"{dx}:{dy}",True,(0,0,255))
                    #screen.blit(k,(tile_center[0]-k.get_width()/2,tile_center[1]-k.get_height()))
                    #k = font.render(f"{cnt}",True,(0,0,255))
                    #screen.blit(k,(tile_center[0]-k.get_width()/2,tile_center[1]))
                
            

        for dy in range(bm_pos[1]-a,bm_pos[1]+a):
            p1 = self.translate_to(((bm_pos[0]-a)*tile_size,dy*tile_size))
            p2 = self.translate_to(((bm_pos[0]+a)*tile_size,dy*tile_size))
            pg.draw.line(screen, grid_color,p1,p2,4)

        for dx in range(bm_pos[0]-a,bm_pos[0]+a):
            p1 = self.translate_to((dx*tile_size,(bm_pos[1]-a)*tile_size))
            p2 = self.translate_to((dx*tile_size,(bm_pos[1]+a)*tile_size))
            pg.draw.line(screen, grid_color,p1,p2,4)
            
            

        for track in tracks:
            stack = ["",""]
            for point in self.tracks[track].points:
                #point = [i*2 for i in point]
                point = self.translate_to(point)
                stack = [stack[1],point]
                if stack[0] != "":
                    pg.draw.line(screen,(16,16,16),
                        stack[0],
                        stack[1],
                        int(8)
                    )

        z = []

        for train in trains:
            if (21*256*(chunk_pos[0]-1) < train.pos[0] < 21*256*(chunk_pos[0]+2) and 
                21*256*(chunk_pos[1]-1) < train.pos[1] < 21*256*(chunk_pos[1]+2) and
                train.type != None):
                #рисуем
                angle = round(train.angle//1) # угол//1 = инд. в массиве
                angle %= 360
                array_entry = self.train_sprites[train.type]
                
                center_pos = self.translate_to(train.pos)
                #center_pos = self.translate_to([i*2 for i in train.pos])

                #sprite = array_entry[0][angle][0] 
                sprite = pg.transform.scale(array_entry[0][angle][0],(
                    array_entry[0][angle][0].get_width()*2,
                    array_entry[0][angle][0].get_height()*2)
                )
                
                draw_queue.append([
                    (train.pos[0]+train.pos[1]),
                    sprite,
                    (
                    round(center_pos[0]-array_entry[0][angle][0].get_width()),
                    round(center_pos[1]-array_entry[0][angle][1]-array_entry[1]*2)
                    )
                ])

                z.append([self.translate_to(train.bogeys[0].pos),self.translate_to([train.bogeys[0].pos[i]+50*train.bogeys[0].vectors[i] for i in [0,1]])])
                z.append([self.translate_to(train.bogeys[1].pos),self.translate_to([train.bogeys[1].pos[i]+50*train.bogeys[1].vectors[i] for i in [0,1]])])


        for element in sorted(draw_queue,key=lambda x:x[0]):
            screen.blit(element[1],element[2])
        
        for p in z:
            pg.draw.circle(screen,(255,0,0),p[0],6)
            pg.draw.line(screen,(255,0,0),p[0],p[1],4)
        if self.scale > 1:
            dw, dh = [int(i/self.scale) for i in self.camera_size]
            screen = pg.transform.scale(screen.subsurface(dw/2,dh/2,dw,dh),self.camera_size)
        elif self.scale < 1:
            screen = pg.transform.scale(screen,self.camera_size)

        if self.flag:screen.blit(self.z,(0,0))

        return screen




