import math
import threading
import time
import random
import json
import pygame as pg
import electrical_system

nodes = {}
tracks = {}
switches = {}

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

class Bogey:
    def __init__(self, pos, cur_track, identifier):
        self.pos = pos
        self.angle = 0
        self.vectors = [0,0]

        self.velocity = 0
        self.velocity_vector = 1

        self.track = cur_track
        self.ride_mode = 0
        self.mod = 0

        self.is_alive = True
        self.debug = True
        self.identifier = identifier

        self.switch_state = 0

        self.thread = threading.Thread(target=self.cycle)
        self.thread.start()

    def cycle(self):
        global nodes, tracks, switches

        tile_size = 256
        if self.debug: print(f"{self.identifier} initialized")

        while self.is_alive:
            c_dx, c_dy = [int(self.pos[0]//tile_size),int(self.pos[1]//tile_size)]

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

                if angle_cone == "x":

                    if self.pos[0] < min(a[0], b[0]):
                        self.track = None
                        nxt = c_track.s_links if min(a[0], b[0]) == a[0] else c_track.e_links

                    elif self.pos[0] > max(a[0], b[0]):
                        self.track = None
                        nxt = c_track.s_links if max(a[0], b[0]) == a[0] else c_track.e_links

                    if self.track == None and self.debug:
                        print(f"{self.identifier}: changing on x-axis. {self.pos[0]}, {a[0]}, {b[0]}")

                if angle_cone == "y":

                    if self.pos[1] < min(a[1], b[1]):
                        self.track = None
                        nxt = c_track.s_links if min(a[1], b[1]) == a[1] else c_track.e_links
                        
                    elif self.pos[1] > max(a[1], b[1]):
                        self.track = None
                        nxt = c_track.s_links if max(a[1], b[1]) == a[1] else c_track.e_links

                    if self.track == None and self.debug: 
                        print(f"{self.identifier}: changing on y-axis. {self.pos[1]}, {a[1]}, {b[1]}")

                if self.track == None and self.debug: print(f"{self.identifier}: reached the end of {old}")

                if len(nxt) == 1:
                    self.track = nxt[0]
                    if self.debug: print(f"{self.identifier}: moved to {self.track}")
                elif len(nxt) > 1:
                    self.track = nxt[self.switch_state]
                    if self.debug: print(f"{self.identifier}: moved to {self.track}")
                elif self.track == None:
                    if self.debug: print(f"{self.identifier}: succesfully derailed!")

                if self.track != old and self.track != None:
                    if old in tracks[self.track].s_links:
                        self.ride_mode = 0
                        print(f"{self.identifier}: changed to {self.track} from front")
                    else:
                        self.ride_mode = 1
                        print(f"{self.identifier}: changed to {self.track} from tail")

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
    def __init__(self, pos, type, cur_track, bogey_displacement,identifier):
        self.pos = pos # абсолютная мировая
        self.angle = 0
        self.flipped = False

        self.velocity = 0
        self.velocity_vector = 0

        self.occupied_tracks = [None,None]
        self.identifier = identifier

        self.type = type
        self.is_alive = True
        self.clock = pg.time.Clock()

        self.bogeys = [
            Bogey([pos[0],pos[1]-bogey_displacement], cur_track, f"{identifier}_bogey_1"),
            Bogey([pos[0],pos[1]+bogey_displacement], cur_track, f"{identifier}_bogey_2")
        ]

        #self.thread = threading.Thread(target=self.cycle)
        #self.thread.start()


    def cycle(self, tick):
        for i, bogey in enumerate(self.bogeys):
            if bogey.track != None:
                bogey.velocity_vector = self.velocity_vector
                bogey.pos[0] += self.velocity*bogey.vectors[0]*self.velocity_vector/tick
                bogey.pos[1] += self.velocity*bogey.vectors[1]*self.velocity_vector/tick

                bogey.pos[0] = round(bogey.pos[0],2)
                bogey.pos[1] = round(bogey.pos[1],2)

                if bogey.angle in [90,270] and (bogey.pos[1]//256+0.6)*256 >= bogey.pos[1] >= (bogey.pos[1]//256+0.4)*256:
                    bogey.pos[1] = (bogey.pos[1]//256+0.5)*256
                elif bogey.angle in [0,180] and (bogey.pos[0]//256+0.6)*256 >= bogey.pos[0] >= (bogey.pos[0]//256+0.4)*256:
                    bogey.pos[0] = (bogey.pos[0]//256+0.5)*256

                self.occupied_tracks[i] = bogey.track

        self.pos = [
            round((self.bogeys[0].pos[0]+self.bogeys[1].pos[0])/2,2),
            round((self.bogeys[0].pos[1]+self.bogeys[1].pos[1])/2,2)
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

    def __init__(self, pos, trtype, cur_track, size, font):
        self.trains = []

        carriage_amt = 3
        self.pixel_velocity = 0
        self.velocity_vector = 0

        self.torque = 0
        self.axial_velocity = 0
        self.velocity = 0
        self.acceleration = 0

        self.reversor_vector = 0

        self.mass = 110000 # кг
        self.wheel_radius = 0.51
        self.reductional_coef = 3
        
        with open("elements.json", encoding="utf-8") as f:
            info = json.loads(f.read())

        self.air_friction_coef = 19#21.168
        self.electrical_system = electrical_system.ElectricalSystem(
            wire_amt = 30, 
            obj_list = info["elements"],
            ns = (12,9), 
            ds = (15,11), 
            tls = 64,
            tt = info["text_lines"], font=font
        )
        params = {
            "km":["res/kofemolka_ruchka.png", [0,0,31,9,8]],
            "km_box":["res/kofemolka.png", [0,0,32,47]],
        }

        self.electrical_system.add_sprites("res/electrical_tiles.png", params)
        self.electrical_system.load([['el_motor', [0, 0, 3, 2], [], [], 'dpt-7', [0.4, 7]], ['el_motor', [3, 0, 3, 2], [], [], 'dpt-7', [0.4, 7]], ['el_motor', [0, 2, 3, 2], [], [], 'dpt-7', [0.4, 7]], ['el_motor', [3, 2, 3, 2], [], [], 'dpt-7', [0.4, 7]], ['group_cn', [7, 0, 2, 2], [20, 3], [10, 11, 12, 13, 14, 15, 16, 0, 18, 19], 'grk-8', [8, [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 1, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 1, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 1, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 1, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 1, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]], ['resistor', [7, 2, 2, 2], [10, 11, 12, 13, 14, 15, 16], [], 'yas-7', [4, [86, 71, 57, 43, 29, 14, 0]]], ['hv_relay', [2, 5, 2, 1], [17], [], 'lk-2', []], ['gr_relay', [0, 5, 2, 1], [1, 18, 4], [20], 'gr-3', [0]], ['gr_relay', [0, 4, 2, 1], [2, 19, 4], [20], 'gr-3', [0]], ['cu_relay', [4, 4, 1, 1], [], [4], 'rt-5', [0, 230]], ['elswitch', [5, 4, 1, 1], [], [3], 'ep-1', []], ['elswitch', [5, 5, 1, 1], [], [2], 'ep-1', []], ['elswitch', [4, 5, 1, 1], [], [1], 'ep-1', []], ['akumbatt', [7, 4, 2, 2], [], [], 'akb-3', []], ['gr_relay', [2, 4, 2, 1], [1, 2, 0], [17], 'gr-3', [1]]])


        for i in range(carriage_amt):
            self.trains.append(Train(
                (pos[0],pos[1]+size*i),trtype if type(trtype) == str else trtype[i%len(trtype)],cur_track,int(size/2-2),f"carriage_{i}"
            ))
            if i%len(trtype) == len(trtype)-1: self.trains[-1].flipped = True

        self.internal_clock = pg.time.Clock()

        self.is_alive = True
        self.thread = threading.Thread(target=self.cycle)
        self.thread.start()

    def cycle(self):
        while self.is_alive:
            tick = max(1,self.internal_clock.get_fps())
            self.physical_think(tick)

            for train in self.trains:
                train.velocity = self.pixel_velocity
                train.velocity_vector = self.velocity_vector
                train.cycle(tick)

            self.internal_clock.tick(60)

        self.destroy()

    def physical_think(self, tick):
        self.torque = self.electrical_system.torque
        traction_force = (self.torque*self.reductional_coef/self.wheel_radius) - self.velocity**2*self.air_friction_coef
        self.acceleration = traction_force/self.mass
        self.velocity += self.acceleration/tick
        self.velocity = max(0, self.velocity)
        self.pixel_velocity = round(self.velocity*50,2)#round(self.velocity*21,2)

        self.electrical_system.axial_speed = self.velocity/self.wheel_radius*self.reductional_coef

    def destroy(self):
        self.is_alive = False
        self.electrical_system.working = False
        for train in self.trains:
            train.destroy()




