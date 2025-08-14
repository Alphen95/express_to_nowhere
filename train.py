import math
import threading
import time
import random
import json
import pygame as pg

nodes = {}
tracks = {}
switches = {}
pg.mixer.init(buffer=65536)

def clamp(base, mn, mx):
    return min(max(mn, base), mx)

def sgn(x):
    if x > 0: return 1
    elif x < 0: return -1
    else: return 0

def xor(a, b):
    return 1 if (a == 1 and b == 0) or (a == 0 and b == 1) else 0

def angle(sin, cos):
    a_acos = math.acos(cos)
    if sin < 0:
        ang = math.degrees(-a_acos) % 360
    else: 
        ang = math.degrees(a_acos)
    return ang

def spawn_train(trtype, track, trainlen, font):
    pos = None
    if track in tracks:
        if tracks[track].s_axis == "x" == tracks[track].e_axis and tracks[track].s_pos[1] == tracks[track].e_pos[1]:
            print("vertical (x axis) track")
            pos = [
                (tracks[track].s_pos[0]+tracks[track].e_pos[0])/2-trainlen[0]*(len(trtype)/2-0.5),
                (tracks[track].s_pos[1]+tracks[track].e_pos[1])/2,
                tracks[track].s_pos[2]
            ]
        elif tracks[track].s_axis == "y" == tracks[track].e_axis and tracks[track].s_pos[0] == tracks[track].e_pos[0]:
            print("horizontal (y axis) track")
            pos = [
                (tracks[track].s_pos[0]+tracks[track].e_pos[0])/2,
                (tracks[track].s_pos[1]+tracks[track].e_pos[1])/2-trainlen[0]*len(trtype)/2,
                tracks[track].s_pos[2]
            ]
        else:
            print(f"Track {track} is not straight!")
    else:
        print("Nonexistant track!")

    if pos != None:
        con = Consist(pos, trtype, track, trainlen, font, True if tracks[track].angles[0][0] in [90, 270] else False)
        if tracks[track].angles[0][0] in [180, 270]:
            for bg in con.bogeys: bg.ride_mode = 1

        return con

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

class Bogey:
    def __init__(self, pos, cur_track, identifier):
        self.pos = pos
        self.angle = 0
        self.vectors = [0,0]

        self.velocity = 0
        self.velocity_vector = 1

        self.track = cur_track
        self.ride_mode = 0

        self.is_alive = True
        self.debug = False
        self.identifier = identifier

        self.front = False
        self.track_seq = []

        self.switch_state = 0

        self.switches = {}

        self.thread = threading.Thread(target=self.cycle)
        self.thread.start()

    def cycle(self):
        global nodes, tracks, switches

        tile_size = 256
        if self.debug: print(f"{self.identifier} initialized")

        while self.is_alive:

            if self.track != None:
                c_track = tracks[self.track]
                
                a, b = c_track.s_pos, c_track.e_pos

                stack = ["",""]
                angle_cone = "x" if (45 <= self.angle%360 <= 135 or 225 <= self.angle%360 <= 315) else "y"
                
                for enum, point in enumerate(c_track.points):
                    stack = [stack[1],point]
                    if stack[0] != "":

                        if angle_cone == "x" and min(stack[0][0],stack[1][0]) <= self.pos[0] <= max(stack[0][0],stack[1][0]):
                            self.angle = (c_track.angles[self.ride_mode][enum-1])%360
                            self.vectors = c_track.vectors[self.ride_mode][enum-1]

                        if angle_cone == "y" and min(stack[0][1],stack[1][1]) <= self.pos[1] <= max(stack[0][1],stack[1][1]):
                            self.angle = (c_track.angles[self.ride_mode][enum-1])%360
                            self.vectors = c_track.vectors[self.ride_mode][enum-1]


                nxt = []
                old = self.track
                must_change = False

                if angle_cone == "x":

                    if self.pos[0] < min(a[0], b[0]):
                        if self.debug: print(f"{self.identifier}: reached the end of {old}")
                        must_change = True 
                        nxt = c_track.s_links if min(a[0], b[0]) == a[0] else c_track.e_links

                    elif self.pos[0] > max(a[0], b[0]):
                        if self.debug: print(f"{self.identifier}: reached the end of {old}")
                        must_change = True 
                        nxt = c_track.s_links if max(a[0], b[0]) == a[0] else c_track.e_links

                    if must_change and self.debug:
                        print(f"{self.identifier}: changing on x-axis. {self.pos[0]}, {a[0]}, {b[0]}")

                if angle_cone == "y":

                    if self.pos[1] < min(a[1], b[1]):
                        if self.debug: print(f"{self.identifier}: reached the end of {old}")
                        must_change = True 
                        nxt = c_track.s_links if min(a[1], b[1]) == a[1] else c_track.e_links
                        
                    elif self.pos[1] > max(a[1], b[1]):
                        if self.debug: print(f"{self.identifier}: reached the end of {old}")
                        must_change = True 
                        nxt = c_track.s_links if max(a[1], b[1]) == a[1] else c_track.e_links

                    if must_change and self.debug: 
                        print(f"{self.identifier}: changing on y-axis. {self.pos[1]}, {a[1]}, {b[1]}")

                if must_change:

                    if self.front or old not in self.track_seq or old in self.track_seq and self.track_seq[-1] == old:
                        if self.debug and old not in self.track_seq:
                            print(f"{self.identifier}: choosing for myself here!")
                        if self.debug and old in self.track_seq and self.track_seq[-1] == old:
                            print(f"{self.identifier}: fuck sjit cunt bitchs")

                        #print(self.track, self.switches, str(self.track) in self.switches)

                        if str(self.track) in self.switches and self.switches[str(self.track)] in nxt:
                            self.track = self.switches[str(self.track)]
                        elif len(nxt) == 1:
                            self.track = nxt[0]
                        elif len(nxt) > 1:
                            self.track = nxt[self.switch_state]
                        
                    else:
                        self.track = self.track_seq[self.track_seq.index(old)+1]

                if must_change and self.track == old: self.track = None

                if self.track != old and self.debug:
                    if self.track != None:
                        if self.debug: print(f"{self.identifier}: moved to {self.track}")
                    else:
                        if self.debug: print(f"{self.identifier}: succesfully derailed! {self.front}")

                if self.track != old and self.track != None:
                    if old in tracks[self.track].s_links:
                        self.ride_mode = 0
                        if self.debug: print(f"{self.identifier}: changed to {self.track} from front")
                    else:
                        self.ride_mode = 1
                        if self.debug: print(f"{self.identifier}: changed to {self.track} from tail")

                    self.ride_mode = xor(self.ride_mode, self.velocity_vector==-1)

            else:
                if self.velocity > 0: self.velocity -= 0.01
                self.velocity = max(self.velocity, 0)
            
            #self.pos[0] += self.velocity*math.cos(math.radians(self.angle))*self.velocity_vector
            #self.pos[1] += -self.velocity*math.sin(math.radians(self.angle))*self.velocity_vector

            #self.pos[0] = round(self.pos[0],2)
            #self.pos[1] = round(self.pos[1],2)

            time.sleep(1/120)

class Train:
    def __init__(self, pos, type, cur_track, bg1, bg2,identifier, size):
        self.pos = pos # абсолютная мировая
        self.angle = 0
        self.flipped = False
        self.size = size
        self.block_coord = [0,0]
        self.doors = [0,0]

        self.velocity = 0
        self.velocity_vector = 0

        self.occupied_tracks = [None,None]
        self.identifier = identifier

        self.type = type
        self.is_alive = True
        self.clock = pg.time.Clock()

        self.bogeys = [
            bg1,
            bg2
        ]

        #self.thread = threading.Thread(target=self.cycle)
        #self.thread.start()


    def cycle(self, tick):
        self.pos = [
            round((self.bogeys[0].pos[0]+self.bogeys[1].pos[0])/2,2),
            round((self.bogeys[0].pos[1]+self.bogeys[1].pos[1])/2,2),
            max(self.bogeys[0].pos[2],self.bogeys[1].pos[2])
        ]

        if self.bogeys[0].pos[1]-self.bogeys[1].pos[1] == 0 or self.bogeys[0].pos[0]-self.bogeys[1].pos[0] == 0:
            self.angle = self.bogeys[0].angle
        else:
            dx = self.bogeys[0].pos[0]-self.bogeys[1].pos[0]
            dy = self.bogeys[0].pos[1]-self.bogeys[1].pos[1]
            l = (dx**2+dy**2)**0.5
            self.angle = angle(dx/l, dy/l)+180
            


    def destroy(self):
        self.is_alive = False
        for bogey in self.bogeys:
            bogey.is_alive = False

class Consist:

    def __init__(self, pos, trtype, cur_track, size, font, drct):
        self.trains = []

        self.pixel_velocity = 0
        self.velocity_vector = 0
        self.reversor_vector = 0

        self.torque = 0
        self.axial_velocity = 0
        self.velocity = 0
        self.acceleration = 0

        self.size = size

        self.motorised = 0
        self.pressurised = 0

        self.route = None

        self.mass = 37000*len(trtype) # кг
        self.wheel_radius = 0.51
        self.reductional_coef = 3

        self.switch = False
        self.routing_switches = {}

        self.door_states = [0,0,0,0]
        self.door_dir = [-1,-1]
        self.door_time = (1,30)
        self.door_sounds = [
            pg.mixer.Sound("res/sound/d_roll.wav"),
            pg.mixer.Sound("res/sound/d_open.wav"),
            pg.mixer.Sound("res/sound/d_close.wav"),
        ]
        self.door_sounds[0].set_volume(0.02)
        self.door_sounds[1].set_volume(0.1)
        self.door_sounds[2].set_volume(0.1)
        self.door_channels = [pg.mixer.Channel(2), pg.mixer.Channel(3)]

        self.track_seq = []
        
        with open("elements.json", encoding="utf-8") as f:
            info = json.loads(f.read())

        self.air_friction_coef = 19#21.168
        self.brake_coefficient = 0.2
        self.brake_area = 0.1

        self.base_reverse = 1

        self.internal = InternalSystem(
            wire_amt = 30, 
            obj_list = info["elements"],
            ns = (12,9), 
            ds = (15,11), 
            tls = 64,
            tt = info["text_lines"], font=font
        )
        params = {
            "km":["res/controls.png", [96,0,20,10]],
            "tk":["res/controls.png", [96,10,20,10]],
            "box":["res/controls.png", [0,0,96,51]],
            "digit_0":["res/controls.png", [ 96,20,3,5]],
            "digit_1":["res/controls.png", [100,20,3,5]],
            "digit_2":["res/controls.png", [104,20,3,5]],
            "digit_3":["res/controls.png", [108,20,3,5]],
            "digit_4":["res/controls.png", [112,20,3,5]],
            "digit_5":["res/controls.png", [ 96,26,3,5]],
            "digit_6":["res/controls.png", [100,26,3,5]],
            "digit_7":["res/controls.png", [104,26,3,5]],
            "digit_8":["res/controls.png", [108,26,3,5]],
            "digit_9":["res/controls.png", [112,26,3,5]],
            "vfd_lit":["res/controls.png", [122,24,5,7]],
        }

        self.internal.add_sprites("res/electrical_tiles.png", params)
        self.internal.load([['el_motor', [0, 0, 3, 2], [], [], 'dpt-7', [0.4, 7]], ['el_motor', [3, 0, 3, 2], [], [], 'dpt-7', [0.4, 7]], ['el_motor', [0, 2, 3, 2], [], [], 'dpt-7', [0.4, 7]], ['el_motor', [3, 2, 3, 2], [], [], 'dpt-7', [0.4, 7]], ['group_cn', [6, 0, 2, 3], [20, 1], [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 0, 0, 0, 0, 0, 0, 0, 0], 'grk-14', [14, [0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]]], ['resistor', [6, 3, 2, 2], [12, 13, 14, 15, 16, 17, 18], [], 'yas-7', [4, [100, 84, 66, 50, 33, 16, 0]]], ['hv_relay', [0, 4, 2, 1], [7], [], 'lk-2', []], ['gr_relay', [2, 4, 2, 1], [2, 3, 4], [7], 'gr-3', [1]], ['gr_relay', [4, 4, 2, 1], [5, 0, 0], [7], 'gr-3', [1]], ['gr_relay', [0, 5, 2, 1], [2, 6, 8], [20], 'gr-3', [0]], ['gr_relay', [2, 5, 2, 1], [3, 6, 9], [20], 'gr-3', [0]], ['gr_relay', [4, 5, 2, 1], [4, 6, 10], [20], 'gr-3', [0]], ['gr_relay', [6, 5, 2, 1], [5, 6, 11], [20], 'gr-3', [0]], ['cu_relay', [8, 0, 1, 1], [], [6], 'rt-5', [0, 200]], ['elswitch', [9, 0, 1, 1], [], [1], 'ep-1', []], ['akumbatt', [8, 1, 2, 2], [], [], 'akb-3', []], ['combiner', [8, 3, 2, 2], [19, 0], [], 'kd-30', []]])
        self.speed_cap = 41.6

        self.bogeys = []

        for i in range(len(trtype)+1):
            self.bogeys.append(Bogey(
                [
                    pos[0]+(size[0]*i-int(size[0]/2))*(drct),
                    pos[1]+(size[0]*i-int(size[0]/2))*(1-drct),
                    pos[2]
                ],
                cur_track,
                f"consist_x_bogey_{i}"
            ))
        
        for i,e in enumerate(trtype):
            self.trains.append(Train(
                (pos[0]+size[0]*i,pos[1]),e[0],cur_track,self.bogeys[i],self.bogeys[i+1],f"carriage_{i}", size
            ))
            if e[1]: self.trains[-1].flipped = True
            if e[2]: self.motorised += 1
            if e[3]: self.pressurised += 1

        self.internal_clock = pg.time.Clock()
        self.derailed = False

        self.is_alive = True
        self.thread = threading.Thread(target=self.cycle)
        self.thread.start()

    def cycle(self):
        while self.is_alive:
            if not self.derailed:
                tick = max(1,self.internal_clock.get_fps())
                self.physical_think(tick)

                if self.velocity_vector == -1:
                    self.bogeys[0].front = True
                    self.bogeys[-1].front = False

                    head = self.bogeys[0].track
                    rear = self.bogeys[-1].track

                    if len(self.track_seq) > 0 and self.track_seq[0] != head or len(self.track_seq) == 0:
                        self.track_seq = [head]+self.track_seq

                    if len(self.track_seq) > 1 and self.track_seq[-2] == rear:
                        self.track_seq = self.track_seq[:-1]

                if self.velocity_vector == 1:
                    self.bogeys[0].front = False
                    self.bogeys[-1].front = True

                    head = self.bogeys[-1].track
                    rear = self.bogeys[0].track

                    if len(self.track_seq) > 0 and self.track_seq[-1] != head or len(self.track_seq) == 0:
                        self.track_seq.append(head)

                    if len(self.track_seq) > 1 and self.track_seq[1] == rear:
                        self.track_seq = self.track_seq[1:]

                for i, bogey in enumerate(self.bogeys):
                    if bogey.track != None:
                        bogey.velocity_vector = self.velocity_vector
                        bogey.track_seq = self.track_seq[::(self.velocity_vector if self.velocity_vector != 0 else 1)]
                        bogey.switch_state = 1 if self.switch else 0
                        bogey.switches = self.routing_switches

                        bogey.pos[0] += self.pixel_velocity*bogey.vectors[0]*self.velocity_vector*self.base_reverse/tick
                        bogey.pos[1] += self.pixel_velocity*bogey.vectors[1]*self.velocity_vector*self.base_reverse/tick
                        bogey.pos[2] += self.pixel_velocity*bogey.vectors[2]*self.velocity_vector*self.base_reverse/tick

                        bogey.pos[0] = round(bogey.pos[0],2)
                        bogey.pos[1] = round(bogey.pos[1],2)
                        bogey.pos[2] = round(bogey.pos[2],2)

                        tile_size = 256

                        if bogey.angle in [90,270] and (bogey.pos[1]//tile_size+0.6)*tile_size >= bogey.pos[1] >= (bogey.pos[1]//tile_size+0.4)*tile_size:
                            bogey.pos[1] = (bogey.pos[1]//tile_size+0.5)*tile_size
                        elif bogey.angle in [0,180] and (bogey.pos[0]//tile_size+0.6)*tile_size >= bogey.pos[0] >= (bogey.pos[0]//tile_size+0.4)*tile_size:
                            bogey.pos[0] = (bogey.pos[0]//tile_size+0.5)*tile_size

                        if bogey.vectors[2] == 0: bogey.pos[2] = round(bogey.pos[2]/tile_size)*tile_size

                        #self.occupied_tracks[i] = bogey.track
                    else:
                        self.derailed = True

                for train in self.trains:
                    train.doors = self.door_states
                    train.velocity = self.pixel_velocity
                    train.velocity_vector = self.velocity_vector
                    train.cycle(tick)

            for i in [0,1]:
                self.door_states[2+i] = clamp(self.door_states[2+i]+self.door_dir[i], 0, self.door_time[1])
                self.door_states[i] = round(self.door_states[2+i]/self.door_time[1]*(self.door_time[0]-1))
                if self.door_dir[i] == 1 and self.door_states[2+i] == self.door_time[1]:
                    self.door_channels[i].play(self.door_sounds[1])
                    self.door_dir[i] = 0
                if self.door_dir[i] == -1 and self.door_states[2+i] == 0:
                    self.door_channels[i].play(self.door_sounds[2])
                    self.door_dir[i] = 0

            self.internal_clock.tick(60)

        self.destroy()

    def physical_think(self, tick):
        self.torque = self.internal.torque*self.motorised
        self.pressure = self.internal.pressure*100000

        traction_force = (self.torque*self.reductional_coef/self.wheel_radius) - self.velocity**2*self.air_friction_coef - self.pressure*self.brake_area*self.brake_coefficient*8*self.pressurised

        self.acceleration = traction_force/self.mass

        if self.acceleration > 0:
            if self.velocity_vector == 0: self.velocity_vector = self.reversor_vector
            self.acceleration *= self.reversor_vector*self.velocity_vector

        self.velocity += self.acceleration/tick
        self.velocity = min(max(0, self.velocity), self.speed_cap)
        self.pixel_velocity = round(self.velocity*30,2)

        if self.velocity == 0: self.velocity_vector = 0

        self.internal.axial_speed = self.velocity/self.wheel_radius*self.reductional_coef
        self.axial_velocity = self.internal.axial_speed
        self.internal.linear_velocity = self.velocity*3.6

    def player_cycle(self, display, screen_size, draw_pos, kbd, kbd_pressed, mouse_state):
        door_mapper = {(0,0):-1, (0,1):1, (1,0): -1, (1,1): -1, (-1,0): 1, (-1, 1): 1}

        if pg.K_n in kbd:
            if self.reversor_vector == 0: pass
            elif self.reversor_vector == -1:
                if self.door_dir[0] == 0: self.door_channels[0].play(self.door_sounds[0],-1)
                self.door_dir[0] = door_mapper[self.door_dir[0], int(self.door_states[0]==0)]
            elif self.reversor_vector ==  1: 
                if self.door_dir[1] == 0: self.door_channels[1].play(self.door_sounds[0],-1)
                self.door_dir[1] = door_mapper[self.door_dir[1], int(self.door_states[1]==0)]

        if pg.K_m in kbd:
            if self.reversor_vector == 0: pass
            elif self.reversor_vector ==  1:
                if self.door_dir[0] == 0: self.door_channels[0].play(self.door_sounds[0],-1)
                self.door_dir[0] = door_mapper[self.door_dir[0], int(self.door_states[0]==0)]
            elif self.reversor_vector == -1: 
                if self.door_dir[1] == 0: self.door_channels[1].play(self.door_sounds[0],-1)
                self.door_dir[1] = door_mapper[self.door_dir[1], int(self.door_states[1]==0)]
        
        self.internal.doors = [self.door_states[0],self.door_states[1]][::self.reversor_vector]
        self.internal.render_graphics(display, screen_size, draw_pos, kbd, kbd_pressed, mouse_state)

    def destroy(self):
        self.is_alive = False
        self.internal.working = False
        for train in self.trains:
            train.destroy()
        self.door_channels[0].stop()
        self.door_channels[1].stop()




