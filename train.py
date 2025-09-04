import math
import threading
import time
import random
import json
import pygame as pg
import internal2

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

def spawn_train(trtype, track, trainlen, int_params):
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
        con = Consist(pos, trtype, track, trainlen, int_params, True if tracks[track].angles[0][0] in [90, 270] else False)
        if tracks[track].angles[0][0] in [180, 270]:
            for bg in con.bogeys: bg.ride_mode = 1

        return con

def sgn(x):
    if x > 0: return 1
    elif x < 0: return -1
    else: return 0

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

    def __init__(self, pos, trtype, cur_track, size, int_params, drct):
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

        self.base_reverse = 1

        self.internal = internal2.Internal()
        self.internal.load(int_params[0], int_params[1])

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

        self.internal_clock = pg.time.Clock()
        self.derailed = False

        self.is_alive = True
        self.thread = threading.Thread(target=self.cycle)
        self.thread.start()

    def cycle(self):
        while self.is_alive:
            if not self.derailed:
                tick = max(1,self.internal_clock.get_fps())
                self.velocity = self.internal.velocity
                self.velocity = min(max(0, self.velocity), self.speed_cap)
                self.pixel_velocity = round(self.velocity*30,2)
                
                if self.velocity == 0: self.velocity_vector = 0
                else:
                    if self.velocity_vector == 0: self.velocity_vector = self.reversor_vector
                    self.acceleration *= self.reversor_vector*self.velocity_vector

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

    def player_cycle(self, display, kbd, keyheld, mouse_state, uni):
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
        self.internal.driver_controller(display, mouse_state, kbd, keyheld, uni)

    def destroy(self):
        self.is_alive = False
        self.internal.alive = False
        for train in self.trains:
            train.destroy()
        self.door_channels[0].stop()
        self.door_channels[1].stop()




