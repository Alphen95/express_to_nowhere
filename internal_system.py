import random
import pygame as pg
import threading
import math

def sgn(x):
    if x > 0: return 1
    elif x < 0: return -1
    else: return 0
class EditorTable:
    def __init__(self, heading, objects_a, objects_b, wire_amt, font):
        self.heading = heading
        self.objects_a = objects_a
        self.objects_b = objects_b
        self.font = font
        self.wire_amt = wire_amt
        self.char_size = font.render("Z", True, (0,0,0)).get_size()

        self.selection = -1

    def update(self, kbd, mouse):

        max_name_len = (len(max(self.objects_a, key=lambda x: len(x)))+2)*self.char_size[0]
        tmp = []
        for line in self.objects_b:
            linelen = 0
            for o in line:
                if o[0] == "label": linelen += max(3,len(o[1]))
                elif o[0] == "wirelen_box": linelen += 3.5
                elif o[0] == "percent_box": linelen += 3.5
                elif o[0] == "grk_toggle": linelen += 3.5
                elif o[0] == "current_box": linelen += 4
                elif o[0] == "toggle": linelen += len(max(o[2], key = lambda x: len(x)))+2
            tmp.append(linelen)
        max_param_len = (max(tmp))*self.char_size[0]

        width = max(max_name_len+max_param_len, len(self.heading)*self.char_size[0])
        
        surf = pg.Surface((width+8, 8+(len(self.objects_a)+1)*(self.char_size[1]+4)))
        s_w, s_h = surf.get_size()

        surf.fill((122,102,82))
        surf.fill((133,112,88), (2,2,s_w-4,s_h-4))
        surf.fill((216,173,130), (4,4,s_w-8,s_h-8))

        for i in range(len(self.objects_a)):
            y = 3+(self.char_size[1]+4)*(i+1)
            pg.draw.line(surf, (76, 61, 46), (4,y),(s_w-5,y),2)

        pg.draw.line(surf, (76, 61, 46), (3+max_name_len,3+(self.char_size[1]+4)),(3+max_name_len,3+(self.char_size[1]+4)*len(self.objects_a+[""])),2)

        name = self.font.render(self.heading, True, (76, 61, 46))
        surf.blit(name, ((s_w-name.get_width())/2, 6))

        for i, l_param in enumerate(self.objects_a):
            line = self.font.render(l_param, True, (76, 61, 46))
            surf.blit(line, ((max_name_len-line.get_width())/2, 6+(i+1)*(self.char_size[1]+4)))

        mx, my = mouse[0][0] + s_w/2, mouse[0][1] + s_h/2 
            
        for i, r_param in enumerate(self.objects_b):
            partial_offset = (width-max_name_len)/len(r_param)
            for j, obj in enumerate(r_param):
                pg.draw.line(surf, (76, 61, 46), 
                    (4+max_name_len+partial_offset*j-1, 4+(i+1)*(self.char_size[1]+4)),
                    (4+max_name_len+partial_offset*j-1, 4+(i+2)*(self.char_size[1]+4)), 2
                )

                bx = 4+max_name_len+partial_offset*j
                by = 6+(i+1)*(self.char_size[1]+4)

                if self.selection == [i, j]:
                    pg.draw.rect(surf, (242, 195, 147),
                        (bx+1, by, partial_offset-2, self.char_size[1])
                    )
                    for keypress in kbd:
                        if pg.key.name(keypress) in [str(i) for i in range(10)]:
                            max_v = 0
                            if obj[0] == "wirelen_box": max_v = self.wire_amt
                            if obj[0] == "current_box": max_v = 1000
                            if obj[0] == "percent_box": max_v = 100
                            
                            obj[1] = int(str(obj[1])+pg.key.name(keypress))
                            obj[1] = min(max_v, obj[1])
                        elif pg.key.name(keypress) == "backspace":
                            obj[1] = str(obj[1])[:-1]
                            obj[1] = 0 if obj[1] == "" else str(obj[1])
                        elif pg.key.name(keypress) == "return":
                            self.selection = -1
 
                if obj[0] == "toggle": line = obj[2][obj[1]]
                elif obj[0] == "grk_toggle": line = [" ", "X"][obj[1]]
                else: line = str(obj[1])
                rline = self.font.render(line, True, (76, 61, 46))
                surf.blit(rline, (bx+(partial_offset-rline.get_width())/2, by))

                if 0 < mx-bx < partial_offset and 0 < my-by < self.char_size[1] and mouse[2] and obj[0] != "label":
                    if obj[0] in ["toggle", "grk_toggle"]:
                        obj[1] = 1-obj[1]
                    else:
                        self.selection = [i, j]


        return surf

class ElectricalObject:
    def __init__(self, tp, rect, inp, out, sprite, info = [], underlay = []):
        self.type = tp
        self.rect = rect

        self.inputs = inp
        self.outputs = out
        self.state = 0
        self.old_state = 0

        self.info = info

        self.sprite = sprite
        self.underlay = None if underlay == [] else random.choice(underlay)

class InternalSystem:
    def __init__(self, wire_amt, obj_list, ns, ds, tls, tt, font):
        self.objects = [] # объекты
        self.net_size = ns # размер сетки ящика

        self.wires = self.generate_wire_block(wire_amt) # поездные провода
        self.wire_amt = wire_amt # количество проводов

        self.base_obj_list = obj_list # инфо для создания объектов
        self.tooltip_lines = tt # текста для подсказок
        self.font = font # шрифт для всех текстов
        self.tile_size = tls # размер клетки в пикселях
        self.display_size = ds # размер просмотра

        self.network_voltage = 1500 # вольтаж к/с
        self.total_resistance = 0 # суммарное (балластное) сопротивление
        self.engine_amt = 0 # количество двигателей
        self.high_voltage = False # сборка схемы (True - собрана)
        self.connection_mode = 1 #0 - последовательное, 1 - комбинированное, 2 - параллельное
        self.current = 0 #ток двигателей
        
        self.torque = 0 # вырабатываемый крутящий момент
        self.pressure = 0 # давление в ТЦ
        self.axial_speed = 0 # получаемая угловая скорость
        self.linear_velocity = 0 # получаемая линейная скорость

        self.open = False # состояние редактора
        self.held = -1 # держимый объект
        self.editing = -1 # редактируемый объект
        self.editor_window = None # штучка для редактирования (переменная окна)
        self.ui_scale = 5 # масштабирование интерфейса

        self.rk_channel = pg.mixer.Channel(0)
        self.eng_channel = pg.mixer.Channel(1)
        self.eng_sound = 0
        self.rk_channel.set_volume(0.1)
        self.dumb = False #глупенький режим

        self.km = { # ВСЕ параметры КМ
            "pos":0,
            "dumbdraw":[11,35,15,-1],
            "dumbmapout":10000,
            "draw":[
                [11,36],
                [11,33],
                [11,30],
                [11,27],
                [11,24],
                [11,21],
                [11,18],
            ],
            "delta": [2,10],
            "mapout":[
                1,
                2,
                3,
                4,
                5
            ],
        }

        self.tk = { # ВСЕ параметры ТК
            "pos":0,
            "dumbdraw":[82,35,15,1],
            "dumbmapout":9.9,
            "draw":[
                [82,13],
                [82,20],
                [82,25],
                [82,29],
                [82,35],
            ],
            "delta": [15,10],
            "mapout":[
                (0, 2),
                (1.75, 2),
                (3.5, 2),
                (5.25, 2),
                (7, 2),
            ],
            #"mapout":[
            #    (0, 0.7),
            #    (0, 0.35),
            #    (0, 0),
            #    (7, 0.35),
            #    (7, 0.7),
            #],
        }

        self.gauge_info = [
            [(39,7),(43,7)],
            [(50,7),(54,7)],
            [(32,6),(59,6)]
        ]
        self.doors = [0,0]

        self.tile_net = {}

        self.sprites = {}
        self.ui_sprites = {}
        self.sounds = {
            "relay_on":pg.mixer.Sound("res/sound/relay_on.mp3"),
            "relay_off":pg.mixer.Sound("res/sound/relay_off.mp3"),
            "rk_start":pg.mixer.Sound("res/sound/rk_start.wav"),
            "rk_stop":pg.mixer.Sound("res/sound/rk_stop.wav"),
            "rk_spin":pg.mixer.Sound("res/sound/rk_spin.wav"),
        }
        self.sounds["rk_start"].set_volume(0.02)
        self.sounds["rk_stop"].set_volume(0.02)
        self.sounds["rk_spin"].set_volume(0.02)
        self.sounds["relay_on"].set_volume(0.02)
        self.sounds["relay_off"].set_volume(0.02)

        self.working = True
        self.thread = threading.Thread(target=self.cycle)
        self.thread.start()

    def add_sprites(self, sprite_file, uisp):
        sheet = pg.image.load(sprite_file)
        self.sprites = {}
        sprite_load_info = [ # name, pos+size
            ["inv_tile",(0,0,1,1)],
        ]

        for el in self.base_obj_list: sprite_load_info.append([el, self.base_obj_list[el]["sprite"]])

        for ifp in sprite_load_info:
            self.sprites[ifp[0]] = pg.transform.scale(sheet.subsurface([i*32 for i in ifp[1][:4]]),[i*self.tile_size for i in ifp[1][2:4]])

        for ifp in uisp:
            scale = self.ui_scale
            isoscale = [0,0,scale,scale]
            sheet = pg.image.load(uisp[ifp][0])
            if len(uisp[ifp][1]) == 4:
                self.ui_sprites[ifp] = pg.transform.scale(sheet.subsurface(uisp[ifp][1]), [uisp[ifp][1][j]*scale for j in (2,3)])
            else:
                layers = []
                images = []
                for i in range(uisp[ifp][1][4]):
                    coords = [uisp[ifp][1][0]+i*uisp[ifp][1][2],uisp[ifp][1][1],uisp[ifp][1][2],uisp[ifp][1][3]]
                    layers.append(pg.transform.scale(sheet.subsurface(coords), [uisp[ifp][1][j]*isoscale[j] for j in (2,3)]))

                for ang in range(360):
                    size = pg.transform.rotate(layers[0], ang).get_size()
                    size = (size[0], size[1]+uisp[ifp][1][4]*scale-1)
                    s = pg.Surface(size, pg.SRCALPHA)
                    for i in range(uisp[ifp][1][4]*scale):
                        img_id = int(i/scale)
                        s.blit(pg.transform.rotate(layers[img_id],ang),(0,uisp[ifp][1][4]*scale-i-1))

                    images.append(s)

                self.ui_sprites[ifp] = {"i":images, "h":uisp[ifp][1][4]*scale}             

    def generate_wire_block(self, amount):
        wires = {}
        for i in range(amount+1): wires[i] = 0
        wires["+"] = 0
        wires["-"] = 0
        
        return wires

    def cycle(self):
        while self.working:
            self.calculate_tilenet()

            if self.editing == -1 and not self.dumb:
                self.wires[0] = 0
                wire_changes = self.generate_wire_block(self.wire_amt)
                sum_resistance = 0
                connection_mode = 0
                engines = []
                circuit_bridged = True

                # "gr_relay", "me_relay", "hv_relay", "cu_relay", "resistor", "akumbatt", "signlamp", "elswitch", "group_cn", "el_motor"

                for obj in self.objects:

                    if obj.type == "gr_relay":
                        if obj.inputs != [] and obj.outputs != [] and obj.outputs[0] not in ["+","-"]:
                            target = obj.outputs[0]
                            old_state = obj.state
                            if all([self.wires[i] > 0 for i in obj.inputs if i != 0]) and obj.info[0] == 0:
                                wire_changes[target] +=1
                                obj.state = 1
                            elif any([self.wires[i] > 0 for i in obj.inputs if i != 0]) and obj.info[0] == 1:
                                wire_changes[target] +=1
                                obj.state = 1
                            else:
                                obj.state = 0
                            
                            if old_state > obj.state: self.sounds["relay_off"].play()
                            elif old_state < obj.state: self.sounds["relay_on"].play()

                    elif obj.type == "cu_relay":
                        if obj.outputs != [] and obj.outputs[0] not in ["+","-"]:
                            target = obj.outputs[0]
                            old_state = obj.state
                            if self.current < obj.info[1] and obj.info[0] == 0: # мин. реле
                                wire_changes[target] +=1
                                obj.state = 1
                            elif self.current > obj.info[1] and obj.info[0] == 1: # макс. реле
                                wire_changes[target] +=1
                                obj.state = 1
                            else:
                                obj.state = 0
                            
                            if old_state > obj.state: self.sounds["relay_off"].play()
                            elif old_state < obj.state: self.sounds["relay_on"].play()

                    elif obj.type == "hv_relay":
                        if obj.inputs != []:
                            old_state = obj.state
                            if self.wires[obj.inputs[0]]:
                                obj.state = 1
                            else:
                                obj.state = 0
                                circuit_bridged = False

                            if old_state > obj.state: self.sounds["relay_off"].play()
                            elif old_state < obj.state: self.sounds["relay_on"].play()

                    elif obj.type == "me_relay":
                        if obj.inputs != [] and obj.outputs != [] and obj.outputs[0] not in ["+","-"]:
                            target = obj.outputs[0]
                            old_state = obj.state

                            if self.wires[obj.inputs[0]]:
                                obj.state = 1
                            if self.wires[obj.inputs[1]]:
                                obj.state = 0

                            if old_state > obj.state: self.sounds["relay_off"].play()
                            elif old_state < obj.state: self.sounds["relay_on"].play()
                            
                            if obj.state > 0 and self.wires["+"]:
                                wire_changes[target] +=1

                    
                    elif obj.type == "combiner":
                        if obj.inputs != []:
                            old_state = obj.state

                            if self.wires[obj.inputs[1]]: obj.state = 2
                            elif self.wires[obj.inputs[0]]: obj.state = 1
                            else: obj.state = 0

                            if old_state != obj.state: 
                                if obj.state == 0: self.sounds["relay_off"].play()
                                else: self.sounds["relay_on"].play()
                            
                            connection_mode = obj.state

                    elif obj.type == "elswitch":
                        if obj.outputs != [] and obj.outputs[0] not in ["+","-"]:
                            target = obj.outputs[0]
                            if obj.state > 0 and self.wires["+"]:
                                wire_changes[target] +=1
                    
                    elif obj.type == "group_cn":
                        if obj.inputs != []:
                            spin = 0
                            rk_pos = int((obj.state+5)/10)
                            if self.wires[obj.inputs[0]] and (obj.info[0]-1)*10 > obj.state+1:
                                obj.state+=1
                                spin += 1
                            if self.wires[obj.inputs[1]] and obj.state > 0:
                                obj.state-=1
                                spin -= 1

                            if obj.old_state == 0 and spin != 0:
                                self.rk_channel.play(self.sounds["rk_start"])
                                self.rk_channel.queue(self.sounds["rk_spin"])
                            elif spin == 0 and obj.old_state != 0:
                                self.rk_channel.stop()
                                self.rk_channel.play(self.sounds["rk_stop"])

                            if spin != 0: self.rk_channel.queue(self.sounds["rk_spin"])
                            obj.old_state = spin

                            
                        if obj.outputs != []:
                            rk_pos = int((obj.state+5)/10)
                            if obj.info[0] > rk_pos:
                                for target_id, target in enumerate(obj.outputs):
                                    if obj.info[rk_pos+1][target_id]:
                                        wire_changes[target] +=1

                    elif obj.type == "resistor":
                        if obj.inputs != []:
                            obj.state = obj.info[0]
                            for source_id, source in enumerate(obj.inputs):
                                if self.wires[source] > 0:
                                    obj.state = obj.info[0]*obj.info[1][source_id]/100

                        else:
                            obj.state = obj.info[0]
                        sum_resistance += obj.state

                    
                    elif obj.type == "el_motor":
                        engines.append(obj)

                    elif obj.type == "akumbatt":
                        wire_changes["+"] = 1

                self.wires = wire_changes
                self.total_resistance = sum_resistance
                self.engine_amt = len(engines)
                self.high_voltage = circuit_bridged
                self.connection_mode = connection_mode
                current = 0
                eng_koefficient = 0

                self.wires[self.km["mapout"][self.km["pos"]]] = 1

                if self.engine_amt > 0 and self.high_voltage:
                    eng_type = engines[0].sprite
                    is_good = True

                    for engine in engines:
                        if engine.sprite != eng_type: is_good = False

                    if is_good:
                        eng_resistance = engines[0].info[0]
                        eng_koefficient = engines[0].info[1]
                        resistance = 1
                        counter_emf = 0
                        
                        if self.connection_mode == 2:
                            counter_emf = eng_koefficient*self.axial_speed
                            resistance = sum_resistance+eng_resistance/self.engine_amt

                        elif self.connection_mode == 1 and self.engine_amt%2==0:
                            counter_emf = 2*eng_koefficient*self.axial_speed
                            resistance = sum_resistance+(2*eng_resistance)/(self.engine_amt//2)

                        else:
                            counter_emf = self.engine_amt*eng_koefficient*self.axial_speed
                            resistance = sum_resistance+self.engine_amt*eng_resistance

                        current = (self.network_voltage- counter_emf)/resistance

                for engine in engines: engine.state = current
                self.torque = self.engine_amt*eng_koefficient*current
                self.current = current
                
                    
                tick = 1/20
                self.pressure += (self.tk["mapout"][self.tk["pos"]][0]-self.pressure)*self.tk["mapout"][self.tk["pos"]][1]*tick
                if self.pressure < 0.2 and self.tk["mapout"][self.tk["pos"]][0] == 0: self.pressure = 0
                self.pressure = round(self.pressure, 2)


            elif self.editing != -1 :
                self.rk_channel.stop()
                self.eng_channel.stop()
                self.current = 0
                self.torque = 0
                self.pressure = 0

            elif self.dumb:
                #print("a")
                pass



            pg.time.wait(50)

        self.rk_channel.stop()
        self.eng_channel.stop()

    def draw_grid(self):
        surf = pg.Surface([i*self.tile_size for i in self.display_size])
        surf.fill((102,102,102))
        dx, dy = [self.tile_size*i for i in ((self.display_size[0]-self.net_size[0])/2, (self.display_size[1]-self.net_size[1])/2+0.5)]
        surf.fill((128,128,128),(dx,dy,self.net_size[0]*self.tile_size,self.net_size[1]*self.tile_size))

        for x in range(self.net_size[0]):
            if x == 0:
                surf.blit(self.sprites["wire_l"],(dx+x*self.tile_size,dy-self.tile_size))
            elif x == self.net_size[0]-1:
                surf.blit(self.sprites["wire_r"],(dx+x*self.tile_size,dy-self.tile_size))
            else:
                surf.blit(self.sprites["wire_m"],(dx+x*self.tile_size,dy-self.tile_size))

            for y in range(self.net_size[1]):
                surf.blit(self.sprites["inv_tile"],(dx+x*self.tile_size,dy+y*self.tile_size))

        for enum, obj in enumerate(self.objects):
            if obj.sprite in self.sprites:

                obj_pos = [i*self.tile_size for i in obj.rect[:2]]
                sprite = obj.sprite
                if obj.type == "signlamp" and self.wires[obj.inputs[0]] > 0: 
                    sprite+="+"
                if obj.type == "elswitch" and obj.state > 0: 
                    sprite+="+"

                if enum == self.held:
                    tmp = pg.Surface(self.sprites[sprite].get_size())
                    tmp.blit(self.sprites[sprite],(0,0))
                    tmp.set_alpha(64)
                    surf.blit(tmp,(obj_pos[0]+dx, obj_pos[1]+dy))

                else:
                    surf.blit(self.sprites[sprite],(obj_pos[0]+dx, obj_pos[1]+dy))

        return surf

    def draw_editor(self, mouse, keypresses):
        surf = pg.Surface([i*self.tile_size for i in self.display_size],pg.SRCALPHA)
        if self.editing != -1:
            e_obj = self.objects[self.editing]
            tl = self.tooltip_lines

            if e_obj.type in ["gr_relay", "me_relay", "hv_relay", "cu_relay", "resistor", "signlamp", "elswitch", "combiner"]:
                if self.editor_window == None:
                    left = []
                    right = []

                    if e_obj.type == "gr_relay":
                        left.append(tl["type"])
                        right.append([["toggle", e_obj.info[0], [tl["relay_0"], tl["relay_1"]], "info:0"]])
                    elif e_obj.type == "cu_relay":
                        left.append(tl["type"])
                        left.append(tl["peril_current"])
                        right.append([["toggle", e_obj.info[0], [tl["min"], tl["max"]], "info:0"]])
                        right.append([["current_box", e_obj.info[1], "info:1"]])
                    elif e_obj.type == "resistor":
                        left.append(tl["res_max"])
                        left.append(tl["res_percent"])
                        right.append([["label", str(e_obj.info[0])+" "+tl["ohm"], "nope:7"]])
                        right.append([["percent_box", j, f"info:1:{i}"] for i, j in enumerate(e_obj.info[1])])

                    if e_obj.inputs != []: 
                        left.append(tl["inputs"])
                        right.append([["wirelen_box", j, f"inputs:{i}"] for i, j in enumerate(e_obj.inputs)])

                    if e_obj.outputs != []: 
                        left.append(tl["outputs"])
                        right.append([["wirelen_box", j, f"outputs:{i}"] for i, j in enumerate(e_obj.outputs)])

                    self.editor_window = EditorTable(tl["names"][e_obj.sprite], left, right, self.wire_amt, self.font)

            elif e_obj.type == "group_cn":
                if self.editor_window == None:
                    left = []
                    right = []

                    left.append(tl["pos"])
                    right.append([["label", "   ", "nope:7"]]+[["label", str(i+1), "nah:6"] for i in range(e_obj.info[0])])
                    for wire_num in range(len(e_obj.info[1])):
                        left.append(tl["contact"]+str(wire_num+1))
                        tmp = [["wirelen_box",e_obj.outputs[wire_num],f"outputs:{wire_num}"]]
                        for rk_pos in range(e_obj.info[0]):
                            tmp.append(["grk_toggle",e_obj.info[rk_pos+1][wire_num],f"info:{rk_pos+1}:{wire_num}"])
                        right.append(tmp)

                    if e_obj.inputs != []: 
                        left.append(tl["inputs"])
                        right.append([["wirelen_box", j, f"inputs:{i}"] for i, j in enumerate(e_obj.inputs)])
                            

                    self.editor_window = EditorTable(tl["names"][e_obj.sprite], left, right, self.wire_amt, self.font)


            if self.editor_window != None:
                mouse[0] = [mouse[0][0]-self.display_size[0]/2*self.tile_size,mouse[0][1]-self.display_size[1]/2*self.tile_size]
 
                s = self.editor_window.update(keypresses, mouse)
                surf.blit(s, [(self.display_size[i]*self.tile_size-s.get_size()[i])/2 for i in [0,1]])

                

            for keypress in keypresses:
                if keypress == pg.K_ESCAPE: 
                    if self.editor_window != None and self.editor_window.selection != -1: self.editor_window.selection = -1
                    else: 
                        for line in self.editor_window.objects_b:
                            for obj in line:
                                params = obj[-1].split(":")
                                if params[0] == "inputs": e_obj.inputs[int(params[1])] = obj[1]
                                elif params[0] == "outputs": e_obj.outputs[int(params[1])] = obj[1]
                                elif params[0] == "info":
                                    if len(params) == 2: e_obj.info[int(params[1])] = obj[1]
                                    if len(params) == 3: e_obj.info[int(params[1])][int(params[2])] = obj[1]
                        self.editor_window = None
                        self.editing = -1
                    
        return surf

    def render_graphics(self, target, screen_size, draw_pos, kbd, kbd_pressed, mouse):
        draw_surf = target

        if not self.dumb:

            if "box" in self.ui_sprites:
                size = self.ui_sprites["box"].get_size()
                base_pos = [
                    screen_size[0]/2-size[0]/2, 
                    screen_size[1]-size[1]
                ]
                draw_surf.blit(self.ui_sprites["box"], base_pos)

                if "km" in self.ui_sprites:
                    img = self.ui_sprites["km"]
                    draw_surf.blit(img, (
                        base_pos[0]+(self.km["draw"][self.km["pos"]][0]-self.km["delta"][0])*self.ui_scale,
                        base_pos[1]+(self.km["draw"][self.km["pos"]][1]-self.km["delta"][1])*self.ui_scale
                    ))

                if "tk" in self.ui_sprites:
                    img = self.ui_sprites["tk"]
                    draw_surf.blit(img, (
                        base_pos[0]+(self.tk["draw"][self.tk["pos"]][0]-self.tk["delta"][0])*self.ui_scale,
                        base_pos[1]+(self.tk["draw"][self.tk["pos"]][1]-self.tk["delta"][1])*self.ui_scale
                    ))

            if self.open:

                m_old = mouse[0]
                d = self.draw_grid()
                if type(draw_pos) == str:
                    draw_pos = [screen_size[0]/2-d.get_width()/2, screen_size[1]/2-d.get_height()/2]
                draw_surf.blit(d, draw_pos)
                mouse = [[mouse[0][i]-draw_pos[i] for i in (0,1)], mouse[1], mouse[2], mouse[3]]
                e = self.draw_editor(mouse, kbd)
                draw_surf.blit(e, draw_pos)

                if self.held != -1:
                    obj = self.objects[self.held]
                    sp = self.sprites[obj.sprite]
                    draw_surf.blit(sp,[m_old[i]-self.tile_size/2 for i in [0,1]])

                mod = {
                    "alt":kbd_pressed[pg.K_LALT] or kbd_pressed[pg.K_RALT], 
                    "ctrl":kbd_pressed[pg.K_LCTRL] or kbd_pressed[pg.K_RCTRL], 
                }

                if mouse[2] and not(mod["alt"] or mod["ctrl"]): 
                    oe = self.locate(mouse[0])
                    if oe != -1:
                        if self.objects[oe].type in "elswitch":
                            self.objects[oe].state = abs(1-self.objects[oe].state)

                elif mod["alt"]:
                    if mouse[2]: 
                        self.held = self.locate(mouse[0])
                    elif mouse[3]: 
                        self.move(mouse[0])

                elif mouse[2] and mod["ctrl"] and not mod["alt"] and self.editing == -1: 
                    self.editing = self.locate(mouse[0])
                    
                elif self.editing == -1:
                    if not mod["alt"]: self.held = -1
                    tt = self.tooltip(mouse[0])
                    if tt != None: 
                        tt_pos = [min(screen_size[i]-tt.get_size()[i],m_old[i]+20) for i in (0,1)]
                        draw_surf.blit(tt,tt_pos)
            else:
                pass

            #if pg.K_e in kbd: self.open = 1 - self.open

            if pg.K_UP in kbd and self.km["pos"] < len(self.km["mapout"])-1: self.km["pos"] += 1
            if pg.K_DOWN in kbd and self.km["pos"] > 0: self.km["pos"] -= 1
            
            if pg.K_f in kbd and self.tk["pos"] < len(self.tk["mapout"])-1: self.tk["pos"] += 1
            if pg.K_r in kbd and self.tk["pos"] > 0: self.tk["pos"] -= 1
        else:
            if "box" in self.ui_sprites:
                size = self.ui_sprites["box"].get_size()
                base_pos = [
                    screen_size[0]/2-size[0]/2, 
                    screen_size[1]-size[1]
                ]
                draw_surf.blit(self.ui_sprites["box"], base_pos)

                if "km" in self.ui_sprites:
                    img = self.ui_sprites["km"]
                    draw_surf.blit(img, (
                        base_pos[0]+(self.km["dumbdraw"][0]-self.km["delta"][0])*self.ui_scale,
                        base_pos[1]+(self.km["pos"]-self.km["delta"][1])*self.ui_scale
                    ))

                if "tk" in self.ui_sprites:
                    img = self.ui_sprites["tk"]
                    draw_surf.blit(img, (
                        base_pos[0]+(self.tk["dumbdraw"][0]-self.tk["delta"][0])*self.ui_scale,
                        base_pos[1]+(self.tk["pos"]-self.tk["delta"][1])*self.ui_scale
                    ))

            if kbd_pressed[pg.K_UP]:
                self.torque = self.km["dumbmapout"]
                self.km["pos"] += abs(self.km["dumbdraw"][3])*sgn(self.km["dumbdraw"][2]-self.km["pos"])
            else:
                self.torque = 0
                self.km["pos"] += abs(self.km["dumbdraw"][3])*sgn(self.km["dumbdraw"][1]-self.km["pos"])

            if kbd_pressed[pg.K_DOWN]:
                self.pressure = self.tk["dumbmapout"]*(self.tk["pos"]-self.tk["dumbdraw"][1])/(self.tk["dumbdraw"][2]-self.tk["dumbdraw"][1])
                self.tk["pos"] += abs(self.tk["dumbdraw"][3])*sgn(self.tk["dumbdraw"][2]-self.tk["pos"])
            else:
                self.pressure = 0
                self.tk["pos"] += abs(self.tk["dumbdraw"][3])*sgn(self.tk["dumbdraw"][1]-self.tk["pos"])
        
        speed = str(round(self.linear_velocity))
        while len(speed) < 2: speed = "0"+speed
        draw_surf.blit(self.ui_sprites[f"digit_{speed[-2]}"], (
            base_pos[0]+self.gauge_info[0][0][0]*self.ui_scale,
            base_pos[1]+self.gauge_info[0][0][1]*self.ui_scale
        ))
        draw_surf.blit(self.ui_sprites[f"digit_{speed[-1]}"], (
            base_pos[0]+self.gauge_info[0][1][0]*self.ui_scale,
            base_pos[1]+self.gauge_info[0][1][1]*self.ui_scale
        ))
        
        press = str(round(self.pressure*10))
        while len(press) < 2: press = "0"+press
        draw_surf.blit(self.ui_sprites[f"digit_{press[-2]}"], (
            base_pos[0]+self.gauge_info[1][0][0]*self.ui_scale,
            base_pos[1]+self.gauge_info[1][0][1]*self.ui_scale
        ))
        draw_surf.blit(self.ui_sprites[f"digit_{press[-1]}"], (
            base_pos[0]+self.gauge_info[1][1][0]*self.ui_scale,
            base_pos[1]+self.gauge_info[1][1][1]*self.ui_scale
        ))

        if self.doors[1]:
            draw_surf.blit(self.ui_sprites["vfd_lit"], (
                base_pos[0]+self.gauge_info[2][0][0]*self.ui_scale,
                base_pos[1]+self.gauge_info[2][0][1]*self.ui_scale
            ))
        if self.doors[0]:
            draw_surf.blit(self.ui_sprites["vfd_lit"], (
                base_pos[0]+self.gauge_info[2][1][0]*self.ui_scale,
                base_pos[1]+self.gauge_info[2][1][1]*self.ui_scale
            ))

    def get_selected(self, m_pos):
        deltas = [self.tile_size*i for i in ((self.display_size[0]-self.net_size[0])/2, (self.display_size[1]-self.net_size[1])/2+0.5)]

        return [int((m_pos[i]-deltas[i])/self.tile_size) for i in (0,1)] #Selected Tile

    def locate(self, m_pos):
        st = self.get_selected(m_pos)

        if all([0 <= st[i] < self.net_size[i] for i in (0,1)]):
            if f"{st[0]}:{st[1]}" in self.tile_net:
                return self.tile_net[f"{st[0]}:{st[1]}"] #Object Enumerator
            else:
                return -1
        else:
            return -1

    def tooltip(self, m_pos):
        oe = self.locate(m_pos)
        if oe != -1:
            obj = self.objects[oe]
            lines = [""]

            if obj.sprite in self.tooltip_lines["names"]: lines += [self.tooltip_lines["names"][obj.sprite]]
            else: lines += [f"Type: {obj.type}"]

            if [i for i in obj.inputs if i != 0]: 
                lines.append(self.tooltip_lines["inputs"]+f" {', '.join(map(str,[i for i in obj.inputs if i != 0]))}")

            if [i for i in obj.outputs if i != 0]:
                lines.append(self.tooltip_lines["outputs"]+f" {', '.join(map(str,[i for i in obj.outputs if i != 0]))}")

            if obj.type in ["gr_relay","hv_relay","me_relay","cu_relay"]:
                if obj.state > 0: lines.append(self.tooltip_lines["active"])
                else: lines.append(self.tooltip_lines["inactive"])
            elif obj.type == "group_cn":
                lines.append(self.tooltip_lines["group_controller"].format(int((obj.state+5)/10)+1))
            elif obj.type == "el_motor":
                lines.append(self.tooltip_lines["engine"].format(round(obj.state,2)))

            lines = [self.font.render(i,True,(2,2,2)) for i in lines]
            ml = max(*[i.get_width() for i in lines])
            lines = lines[1:]
            h = lines[0].get_height()+2
            surf = pg.Surface((ml+6,h*len(lines)+6))
            surf.fill((99,98,89))
            surf.fill((214,211,192),(2,2,ml+2,h*len(lines)+2))
            for i in range(len(lines)): surf.blit(lines[i],(3,h*i+3))
            return surf
        else:
            return None

    def calculate_tilenet(self):
        tile_net = {}
        for enum, obj in enumerate(self.objects):
            for tdx in range(obj.rect[2]):
                for tdy in range(obj.rect[3]):
                    tile_net[f"{obj.rect[0]+tdx}:{obj.rect[1]+tdy}"] = enum

        self.tile_net = tile_net

    def move(self, new_pos):
        diff = [self.get_selected(new_pos)[i]-self.objects[self.held].rect[i] for i in (0,1)]

        if diff[0] != 0 or diff[1] != 0:
            if self.held != -1:
                obj = self.objects[self.held]
                flag = True
                x, y = [obj.rect[i]+diff[i] for i in (0,1)]
                for dx in range(obj.rect[2]):
                    for dy in range(obj.rect[3]):
                        if ((f"{x+dx}:{y+dy}" in self.tile_net and self.tile_net[f"{x+dx}:{y+dy}"] != self.held) or
                            not(0 <= x+dx < self.net_size[0] and 0 <= y+dy < self.net_size[1])):
                            flag = False
                            break
                    if not flag: break
                if flag: obj.rect = [x,y]+obj.rect[2:]
        
        self.held = -1

    def add(self, add_obj, pos=[]):
        if add_obj in self.base_obj_list:
            self.calculate_tilenet() 

            obj = self.base_obj_list[add_obj]
            w, h = obj["sprite"][2], obj["sprite"][3]
            if pos != [] and all([0 <= pos[i] <= self.net_size[i] for i in (0,1)]):
                flag = True

                for b_dx in range(w):
                    for b_dy in range(h):
                        if not all([0 <= pos[i]+[b_dx, b_dy][i] < self.net_size[i] for i in (0,1)]+[f"{pos[0]+b_dx}:{pos[1]+b_dy}" not in self.tile_net]):flag = False
            elif pos == []:
                flag = False
                for n_y in range(self.net_size[1]):
                    for n_x in range(self.net_size[0]):
                        pos = [n_x, n_y]
                        sflag = True

                        for b_dx in range(w):
                            for b_dy in range(h):
                                if not all([0 <= pos[i]+[b_dx, b_dy][i] < self.net_size[i] for i in (0,1)]+[f"{pos[0]+b_dx}:{pos[1]+b_dy}" not in self.tile_net]): sflag = False

                        if sflag:
                            flag = True
                            break
                    if flag: break

            if flag:
                info_pack = obj["info"].copy()
                if obj["type"] == "resistor":
                    info_pack.append([0]*obj["in"])
                elif obj["type"] == "group_cn":
                    for i in range(obj["info"][0]):info_pack.append([0]*obj["out"])
                self.objects.append(ElectricalObject(
                    obj["type"], [pos[0], pos[1], w, h], [0]*obj["in"], [0]*obj["out"], add_obj, info_pack
                ))

    def dump(self):
        decompiled_objects = []
        for obj in self.objects:
            decompiled_objects.append([
                obj.type,
                obj.rect,
                obj.inputs,
                obj.outputs,
                obj.sprite,
                obj.info
            ])

        return decompiled_objects

    def load(self, info):
        self.objects = []
        for obj in info:
            self.objects.append(ElectricalObject(
                obj[0], obj[1], obj[2], obj[3], obj[4], obj[5]
            ))