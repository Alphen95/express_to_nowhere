import pygame as pg
import threading
import time

#internal system v2
win_size = (0,0)

pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(win_size, pg.SRCALPHA | pg.HWSURFACE) #| pg.FULLSCREEN)
font = pg.font.Font("res/font.ttf",20)

win_size = screen.get_size()

def scrd(x, y, scale):
    return (x*scale, y*scale)

def offset(base, offset):
    return (base[0]+offset[0], base[1]+offset[1])

rst_load_params = {
    "corner_upper":[2, 2, 6, 5],
    "corner_lower":[2,20, 6, 7],
    "side":[2, 7, 6, 5],
    "top_slider":[8, 2, 5, 5],
    "top":[13, 2, 5, 5],
    "bottom":[8, 20, 10, 7],
    "slider_small":[8, 7, 5, 5],
    "slider":[8, 12, 5, 8],
    "dash_small":[13, 7, 5, 5],
    "dash":[13, 12, 5, 8],
    "green":[18, 7, 5, 5],
    "c_upper":[23, 2, 44, 2],
    "c_middle":[23, 4, 44, 8],
    "c_lower":[23, 20, 44, 7],
    "knob":[23, 32, 5, 6],
    "con_alt":[2, 32, 10, 6],
    "btn_alt":[15, 32, 5, 6],
}

class Internal():
    def __init__(self):
        self.arcade = False

        self.network_voltage = 1200
        self.eng_current = 0
        self.eng_voltage = 0
        self.pressure = 0

        self.velocity = 0

        self.electrical = {
            "reostat":{
                "traction":[],
                "brake":[]
            },
            "driver":{
                "traction":[],
                "brake":[]
            },
            "engine":{
                "constant":10,
                "resistance":1
            },
            "parameters":{
                "type": "reostat",
                "traction":[ 12, 3],
                "brake":[ 12, 3]
            },
            "drv_position":0,
            "con_position":0,
            "drv_limits":[0,0],
            "peril_current": 200
        }

        self.pneumatic = {
            "mapout":[
                (7, 2),
                (5.25, 2),
                (3.5, 2),
                (1.75, 2),
                (0, 2),
            ],
            "pos":4,
            "area":0.1,
            "coefficient":0.15

        }

        self.physical = {
            "air_friction_coef":19,
            "brake_cyllinders":8,
            "engines":4,
            "mass":34000,
            "radius":0.51,
            "reductor":70/19,

            "cars":1,
            "motorised":1,
            "pressurised":1,
        }
        
        self.drv_edges = [9, 38],  [9, 14]
        self.drv_pos = []
        
        self.prs_edges = [80, 38],  [80, 14]
        self.prs_pos = []

        self.selection = -1

        self.doors = [0,0]

        self.KEYMAP = {
            "forwards":pg.K_UP,
            "neutral":pg.K_HELP, #задел на Q/A/Z или W/S/X
            "backwards": pg.K_DOWN,

            "pressure_up": pg.K_r,
            "pressure_down": pg.K_f
        }

        spritesheet = pg.image.load("res/internal_sprites.png")
        self.sprites = {"traction_reostat":{},"brake_reostat":{},"reostat":{}, "internals_box":{}, "driver_controls":{}}

        for parameter in rst_load_params:
            self.sprites["traction_reostat"][parameter] = spritesheet.subsurface(rst_load_params[parameter])
            a,b,c,d = rst_load_params[parameter]
            self.sprites["brake_reostat"][parameter] = spritesheet.subsurface([a+65,b,c,d])

        for i in range(10): self.sprites["reostat"][f"digit_{i}"] = spritesheet.subsurface(85+4*i, 50, 3, 5)
        for i in range(10): self.sprites["reostat"][f"active_digit_{i}"] = spritesheet.subsurface(85+4*i, 56, 3, 5)

        self.sprites["internals_box"]["underlay"] = spritesheet.subsurface(167, 14, 88, 69)
        self.sprites["internals_box"]["traction_controller"] = spritesheet.subsurface(2, 50, 39, 27)
        self.sprites["internals_box"]["brake_controller"] = spritesheet.subsurface(43, 50, 39, 27)
        
        for cat in self.sprites:
            for sp in self.sprites[cat]:
                self.sprites[cat][sp] = pg.transform.scale(self.sprites[cat][sp], [i*4 for i in self.sprites[cat][sp].get_size()])
        
        self.sprites["driver_controls"]["base"] = spritesheet.subsurface(0, 86, 96, 51)
        self.sprites["driver_controls"]["neutral_mark"] = spritesheet.subsurface(101, 132, 3, 1)
        self.sprites["driver_controls"]["active_mark"] = spritesheet.subsurface(101, 134, 3, 1)
        self.sprites["driver_controls"]["accel_handle"] = spritesheet.subsurface(96, 86, 20, 10)
        self.sprites["driver_controls"]["brake_handle"] = spritesheet.subsurface(96, 96, 20, 10)
        self.sprites["driver_controls"]["door_light"] = spritesheet.subsurface(122, 110, 5, 7)
        
        for i in range(10): self.sprites["driver_controls"][f"digit_{i}"] = spritesheet.subsurface(96+4*i, 118, 3, 5)
        for i in range(10): self.sprites["driver_controls"][f"speeding_digit_{i}"] = spritesheet.subsurface(96+4*i, 124, 3, 5)
        
        self.drv_scale = 5

        for sp in self.sprites["driver_controls"]:
            self.sprites["driver_controls"][sp] = pg.transform.scale(self.sprites["driver_controls"][sp], [i*self.drv_scale for i in self.sprites["driver_controls"][sp].get_size()])
        

        self.editing = [None, 0]

        self.panel_sprite = {
            "traction": None,
            "brake":None
        }

        self.max_resistance = 600

        self.alive = True

        self.thread = threading.Thread(target=self.cycle)
        self.thread.start()

    def reset(self, soft = False):
        #s = self.scale
        
        if not soft:

            self.electrical["reostat"] = {
                "traction":[],
                "brake":[]
            }
            for i in range(self.electrical["parameters"]["traction"][0]): self.electrical["reostat"]["traction"].append([0, 0, 100])
            for i in range(self.electrical["parameters"]["brake"][0]   ): self.electrical["reostat"]["brake"].append([0, 0, 100])

            # девелопер комментари: ВАМ [red] НЕ НУЖНО ПАРАЛЛЕЛЬНОЕ СОЕД-Е В ТОРМОЗЕ
            # ПОТОМУ ЭТО ПНЕВМАТИЧЕСКИЙ ДОТОРМОЗ

            self.electrical["driver"] = {
                "traction":[],
                "brake":[]
            }

            for i in range(self.electrical["parameters"]["traction"][1]): self.electrical["driver"]["traction"].append(1)
            for i in range(self.electrical["parameters"]["brake"][1]): self.electrical["driver"]["brake"].append(1)

        self.electrical["drv_limits"] = [-self.electrical["parameters"]["brake"][1], self.electrical["parameters"]["traction"][1]]

        sp = (self.drv_edges[0][1]-self.drv_edges[1][1])/(self.electrical["parameters"]["brake"][1]+self.electrical["parameters"]["traction"][1])

        for i in range(self.electrical["parameters"]["brake"][1]+self.electrical["parameters"]["traction"][1]+1):
            self.drv_pos.append([self.drv_edges[0][0],self.drv_edges[0][1]-sp*i])

        sp = (self.prs_edges[0][1]-self.prs_edges[1][1])/(len(self.pneumatic["mapout"])-1)

        for i in range(len(self.pneumatic["mapout"])):
            self.prs_pos.append([self.prs_edges[0][0],self.prs_edges[0][1]-sp*i])

        self.predraw()

    def predraw(self):
        for tp in ["traction","brake"]:
            reo_type = f"{tp}_reostat"

            if self.electrical["parameters"][tp][0] != 0:
                pw, ph = 212, 36+32*self.electrical["parameters"][tp][0]
                if self.electrical["parameters"]["type"] != "direct": pw += self.electrical["parameters"][tp][1]*40
                panel_sprite = pg.Surface((pw, ph)) 

                if self.electrical["parameters"]["type"] != "direct":
                    panel_sprite.blit(self.sprites[reo_type]["corner_upper"], (0,0))
                    panel_sprite.blit(pg.transform.scale(self.sprites[reo_type]["side"], (24, ph-48)), (0,20))
                    panel_sprite.blit(self.sprites[reo_type]["corner_lower"], (0, ph-28))

                    for i in range(self.electrical["parameters"][tp][1]):
                        panel_sprite.blit(self.sprites[reo_type]["top_slider"], (24+i*40, 0))
                        panel_sprite.blit(self.sprites[reo_type]["top"], (44+i*40, 0))
                        panel_sprite.blit(self.sprites[reo_type]["slider_small"], (24+i*40, 20))
                        panel_sprite.blit(self.sprites[reo_type]["dash_small"], (44+i*40, 20))

                        for l in range(self.electrical["parameters"][tp][0]-1):
                            panel_sprite.blit(self.sprites[reo_type]["slider"], (24+i*40, 40+l*32))
                            panel_sprite.blit(self.sprites[reo_type]["dash"], (44+i*40, 40+l*32))

                        panel_sprite.blit(self.sprites[reo_type]["bottom"], (24+i*40, ph-28))

                    panel_sprite.blit(self.sprites[reo_type]["top"], (pw-188, 0))
                    panel_sprite.blit(pg.transform.scale(self.sprites[reo_type]["green"], (20, ph-48)), (pw-188, 20))
                    panel_sprite.blit(self.sprites[reo_type]["bottom"], (pw-188, ph-28))
                
                panel_sprite.blit(self.sprites[reo_type]["c_upper"], (pw-168, 0))

                for l in range(self.electrical["parameters"][tp][0]):
                    panel_sprite.blit(self.sprites[reo_type]["c_middle"], (pw-168, 8+l*32))
                    
                panel_sprite.blit(self.sprites[reo_type]["c_lower"], (pw-168, ph-28))
            else:
                panel_sprite = None
            
            self.panel_sprite[tp] = panel_sprite
    
    def driver_controller(self, target, m_state, keyboard, keyheld, unicode):
        if self.editing[0] == None:
            sw, sh = target.get_size()
            pw, ph = self.sprites["driver_controls"]["base"].get_size()
            
            base = (sw/2-pw/2, sh-ph)
            bx, by = base
            target.blit(self.sprites["driver_controls"]["base"], base)

            neutral = -self.electrical["drv_limits"][0]

            if not self.arcade:
                for i in range(len(self.drv_pos)):
                    target.blit(self.sprites["driver_controls"]["active_mark" if i != neutral else "neutral_mark"], 
                        (bx+(self.drv_pos[i][0]-3)*self.drv_scale, by+(self.drv_pos[i][1]-2)*self.drv_scale))

                pos = neutral+self.electrical["drv_position"]
                    
                target.blit(self.sprites["driver_controls"]["accel_handle"], 
                    (bx+self.drv_pos[pos][0]*self.drv_scale, by+(self.drv_pos[pos][1]-10)*self.drv_scale))
            else:
                pos = self.arcade[0]
                target.blit(self.sprites["driver_controls"]["accel_handle"], 
                    (bx+(self.drv_edges[pos][0])*self.drv_scale, by+(self.drv_edges[pos][1]-10)*self.drv_scale))

            pos = self.pneumatic["pos"]

            if not self.arcade:
                for i in range(len(self.prs_pos)):
                    target.blit(self.sprites["driver_controls"]["active_mark"], 
                        (bx+(self.prs_pos[i][0]+7)*self.drv_scale, by+(self.prs_pos[i][1]-2)*self.drv_scale))
                
                target.blit(self.sprites["driver_controls"]["brake_handle"], 
                    (bx+(self.prs_pos[pos][0]-13)*self.drv_scale, by+(self.prs_pos[pos][1]-10)*self.drv_scale))
            else:
                pos = self.arcade[1]
                target.blit(self.sprites["driver_controls"]["brake_handle"], 
                    (bx+(self.prs_edges[pos][0]-13)*self.drv_scale, by+(self.prs_edges[pos][1]-10)*self.drv_scale))

            sp = str(round(self.velocity*3.6)+100)

            target.blit(self.sprites["driver_controls"][f"digit_{sp[-2]}"], 
                (bx+39*self.drv_scale, by+7*self.drv_scale))
            target.blit(self.sprites["driver_controls"][f"digit_{sp[-1]}"], 
                (bx+43*self.drv_scale, by+7*self.drv_scale))

                
            sp = str(round(self.pressure*10)+100)

            target.blit(self.sprites["driver_controls"][f"digit_{sp[-2]}"], 
                (bx+50*self.drv_scale, by+7*self.drv_scale))
            target.blit(self.sprites["driver_controls"][f"digit_{sp[-1]}"], 
                (bx+54*self.drv_scale, by+7*self.drv_scale))

                
            if self.doors[1]:
                target.blit(self.sprites["driver_controls"]["door_light"], (bx+32*self.drv_scale, by+6*self.drv_scale))
            if self.doors[0]:
                target.blit(self.sprites["driver_controls"]["door_light"], (bx+59*self.drv_scale, by+6*self.drv_scale))

            #if pg.K_e in keyboard: self.editing = ["general", 0]
            if not self.arcade:

                if self.KEYMAP["forwards"] in keyboard and self.electrical["drv_position"]+1 <= self.electrical["drv_limits"][1]:
                    self.electrical["drv_position"]+=1 
                
                if self.KEYMAP["backwards"]  in keyboard and self.electrical["drv_position"]-1 >= self.electrical["drv_limits"][0]:
                    self.electrical["drv_position"]-=1 
                    
                if self.KEYMAP["neutral"] in keyboard:
                    self.electrical["drv_position"] = 0 

                
                if self.KEYMAP["pressure_up"] in keyboard and self.pneumatic["pos"]+1 < len(self.pneumatic["mapout"]):
                    self.pneumatic["pos"]+=1 
                
                if self.KEYMAP["pressure_down"]  in keyboard and self.pneumatic["pos"]-1 >= 0:
                    self.pneumatic["pos"]-=1 
            
            else:  
                if keyheld[self.KEYMAP["forwards"]]:
                    self.arcade[0] = True
                else:
                    self.arcade[0] = False
                
                if keyheld[self.KEYMAP["backwards"]]:
                    self.arcade[1] = True
                else:
                    self.arcade[1] = False
                
                
            #if pg.K_p in keyboard:
            #    self.velocity = 10

        else: self.controller_editor(target, m_state, keyboard, unicode)


    def controller_editor(self, target, m_state, keyboard, unicode):
        if self.editing[0] in ["traction", "brake"] and self.panel_sprite[self.editing[0]] != None:
            con_type = self.editing[0]
            reo_type = f"{con_type}_reostat"

            sw, sh = target.get_size()
            pw, ph = self.panel_sprite[con_type].get_size()

            scroll = True
            
            base = (sw/2-pw/2, sh/2-ph/2-self.editing[1] *4)
            bx, by = base
            target.blit(self.panel_sprite[con_type], base)

            for l in range(len(self.electrical["reostat"][con_type])):
                a= str(self.electrical["reostat"][con_type][l][0])
                digit_base = f"{'active_' if self.selection == l else ''}digit"
                while len(a) < 4: a = "0"+a
                if a[0] != " ": target.blit(self.sprites["reostat"][f"{digit_base}_{int(a[0])}"], (bx+pw-136, by+ph-52-l*32))
                if a[1] != " ": target.blit(self.sprites["reostat"][f"{digit_base}_{int(a[1])}"], (bx+pw-120, by+ph-52-l*32))
                if a[2] != " ": target.blit(self.sprites["reostat"][f"{digit_base}_{int(a[2])}"], (bx+pw-104, by+ph-52-l*32))
                if a[3] != " ": target.blit(self.sprites["reostat"][f"{digit_base}_{int(a[3])}"], (bx+pw-88, by+ph-52-l*32))
                
                if self.electrical["reostat"][con_type][l][1]:
                    target.blit(self.sprites[reo_type]["con_alt"], (bx+pw-48, by+ph-52-l*32))

                if m_state[2] and 0 <= m_state[0][0]-(bx+pw-48) <= 40 and 0 <= m_state[0][1]-(by+ph-56-l*32) <= 24:
                    if self.electrical["reostat"][con_type][l][1]:
                        self.electrical["reostat"][con_type][l][1] = 0
                    else:self.electrical["reostat"][con_type][l][1] = 1
                
                for i in range(len(self.electrical["driver"][con_type])):
                    if m_state[1][0] and 0 <= m_state[0][0]-(bx+24+40*i) <= 20 and 0 <= m_state[0][1]-(by+ph-52-32*l) <= 32:
                        if ((i == 0 and l+1 <= self.electrical["driver"][con_type][i+1]) or
                            (i == len(self.electrical["driver"][con_type])-1 and l+1 >= self.electrical["driver"][con_type][i-1]) or
                            (self.electrical["driver"][con_type][i-1] <= l+1 <= self.electrical["driver"][con_type][i+1])
                            ):
                            self.electrical["driver"][con_type][i] = l+1
                
                if m_state[2] and 0 <= m_state[0][0]-(bx+pw-148) <= 76 and 0 <= m_state[0][1]-(by+ph-56-l*32) <= 28: self.selection = l

                if self.selection == l:
                    for char in unicode:
                        if char.isdigit(): self.electrical["reostat"][con_type][l][0] = self.electrical["reostat"][con_type][l][0]*10+int(unicode[0])

                    if pg.K_BACKSPACE in keyboard: self.electrical["reostat"][con_type][l][0] //= 10
                    
                    if pg.K_ESCAPE in keyboard or pg.K_RETURN in keyboard:
                        self.selection = -1

                    self.electrical["reostat"][con_type][l][0] = min(self.max_resistance, self.electrical["reostat"][con_type][l][0])

                elif self.selection == -1 and pg.K_ESCAPE in keyboard: self.editing = ["general", 0]
            
            for i in range(len(self.electrical["driver"][con_type])):
                target.blit(self.sprites[reo_type]["knob"], (bx+24+40*i, by+ph-52-32*(self.electrical["driver"][con_type][i]-1)))

            if scroll: self.editing[1] -= m_state[3]*4

        elif self.editing[0] == "general":
            sw, sh = target.get_size()
            pw, ph = self.sprites["internals_box"]["underlay"].get_size()
            bx, by = (sw-pw)/2, (sh-ph)/2

            target.blit(self.sprites["internals_box"]["underlay"], (bx, by))

            if self.electrical["parameters"]["traction"][0] != 0:
                target.blit(self.sprites["internals_box"]["traction_controller"], (bx+44*4, by+5*4))
                if bx+44*4 <= m_state[0][0] <= bx+83*4 and by+5*4 <= m_state[0][1] < by+32*4 and m_state[2]:
                    self.editing = ["traction", 0]
                    self.selection = -1
            
            if self.electrical["parameters"]["brake"][0] != 0:
                target.blit(self.sprites["internals_box"]["brake_controller"], (bx+44*4, by+32*4))
                if bx+44*4 <= m_state[0][0] <= bx+83*4 and by+32*4 <= m_state[0][1] < by+59*4 and m_state[2]:
                    self.editing = ["brake", 0]
                    self.selection = -1

            if pg.K_ESCAPE in keyboard or pg.K_RETURN in keyboard:
                self.editing = [None, 0]

    def cycle(self):
        dt = 1/20

        while self.alive:
            axial_velocity = self.velocity/self.physical["radius"]*self.physical["reductor"]
            consist_mass = self.physical["mass"]*self.physical["cars"]
            traction_force = 0
            air_friction = 0
            torque = 0
            air_friction = self.velocity**2*self.physical["air_friction_coef"]

            # девелопер комментари для будущего ящпера:
            # в ходовом режиме второй [1] параметр - сериесное/параллельное
            # в тормозном режиме второй [1] параметр - включение дотормоза

            # параллельное соед-е - ВСЕГЛА две параллельные ветви.
            # я не хочу делать отдельно полусериесное и честнопараллельное.
            # и вроде никакие [red] не делали вагоны со честнопараллельным приводом.

            if self.editing[0] == None and not self.arcade:
                pressure_friction = 0
                traction_force = 0

                if self.electrical["drv_position"] == 0: # [не]сбор СХ на нейтраль
                    self.electrical["con_position"] = 0

                elif self.electrical["drv_position"] > 0: # сбор СХ на ход

                    if self.electrical["con_position"] < 1: self.electrical["con_position"] = 1 #прокрутить контроллер до 1ой позиции

                    reostat = self.electrical["reostat"]["traction"][self.electrical["con_position"]-1] # дёргнуть реостатную позицию

                    engine_resistance = self.electrical["engine"]["resistance"]*self.physical["engines"]
                    if reostat[1]: engine_resistance /= 4
                    resistance = reostat[0]+engine_resistance # сбор сопротивлений
                    resistance /= 100 # приведение к СИ

                    emf = axial_velocity*self.electrical["engine"]["constant"]*self.physical["engines"]
                    if reostat[1]: emf /= 2 # сбор ЭДС
                    emf *= reostat[2]/100 # применение ослабления

                    self.eng_current = round((self.network_voltage-emf)/resistance,2) # I = (U-E)/R

                    if reostat[1]: self.eng_current /= 2 # [red] половину тока если параллель

                    if 0 <= self.eng_current < 2000:
                        torque = self.electrical["engine"]["constant"]*self.eng_current
                    else: self.eng_current = -7

                    torque *= reostat[2]/100 # применение ослабления

                    traction_force = torque*self.physical["engines"]*self.physical["motorised"]*self.physical["radius"]*self.physical["reductor"]

                    if (self.eng_current < self.electrical["peril_current"] and 
                        self.electrical["con_position"] < self.electrical["driver"]["traction"][self.electrical["drv_position"]-1]):
                        self.electrical["con_position"] += 1
                        
                elif self.electrical["drv_position"] < 0: # сбор СХ на ход

                    if self.electrical["con_position"] < 1: self.electrical["con_position"] = 1 #прокрутить контроллер до 1ой позиции

                    reostat = self.electrical["reostat"]["brake"][self.electrical["con_position"]-1] # дёргнуть реостатную позицию

                    engine_resistance = self.electrical["engine"]["resistance"]*self.physical["engines"]
                    if len(reostat) >= 4 and reostat[3]: engine_resistance /= 4
                    resistance = reostat[0]+engine_resistance # сбор сопротивлений
                    resistance /= 100 # приведение к СИ

                    emf = axial_velocity*self.electrical["engine"]["constant"]*self.physical["engines"] # сбор ЭДС
                    if len(reostat) >= 4 and reostat[3]: emf /= 2 # сбор ЭДС
                    emf *= reostat[2]/100 # применение ослабления

                    self.eng_current = round((-emf)/resistance,2) # I = (-E)/R

                    torque = self.electrical["engine"]["constant"]*self.eng_current
                    if len(reostat) >= 4 and reostat[3]: self.eng_current /= 2 # [red] половину тока если параллель

                    if reostat[1]: torque -= 2000

                    traction_force = torque*self.physical["engines"]*self.physical["motorised"]*self.physical["radius"]*self.physical["reductor"]

                    if (abs(self.eng_current) < self.electrical["peril_current"] and 
                        self.electrical["con_position"] < self.electrical["driver"]["brake"][abs(self.electrical["drv_position"])-1]):
                        self.electrical["con_position"] += 1

                
                self.pressure += (self.pneumatic["mapout"][self.pneumatic["pos"]][0]-self.pressure)*self.pneumatic["mapout"][self.pneumatic["pos"]][1]*dt
                if self.pressure < 0.2 and self.pneumatic["mapout"][self.pneumatic["pos"]][0] == 0: self.pressure = 0
                self.pressure = round(self.pressure, 2)

                

            elif self.arcade:
                if self.arcade[0]: traction_force = 10000*self.physical["engines"]*self.physical["motorised"]

                if self.arcade[1]: self.pressure = 9.9
                else: self.pressure = 0
            
            pressure_friction = self.pressure*self.pneumatic["area"]*self.pneumatic["coefficient"]*self.physical["brake_cyllinders"]*self.physical["pressurised"]*100000

            result_force = traction_force - pressure_friction - air_friction

            self.velocity += result_force/consist_mass*dt

            self.velocity = max(0, self.velocity)

            time.sleep(dt)

    def dump(self):
        return self.electrical

    def load(self, elec, phys):
        self.electrical["parameters"] = elec["parameters"]
        self.reset()

        if elec["reostat"]["traction"] != []: self.electrical["reostat"]["traction"] = elec["reostat"]["traction"]
        if elec["reostat"]["brake"] != []: self.electrical["reostat"]["brake"] = elec["reostat"]["brake"]

        if elec["driver"]["traction"] != []: self.electrical["driver"]["traction"] = elec["driver"]["traction"]
        if elec["driver"]["brake"] != []: self.electrical["driver"]["brake"] = elec["driver"]["brake"]
        
        self.electrical["engine"] = elec["engine"]
        self.electrical["peril_current"] = elec["peril_current"]


        self.electrical["drv_position"] = 0
        self.electrical["con_position"] = 0

        if phys != {}: self.physical = phys
'''

system = Internal()
system.load({'reostat': {'traction': [[370, 1, 100], [221, 1, 100], [170, 1, 100], [131, 1, 100], [108, 1, 100], [81, 1, 100], [66, 1, 100], [51, 1, 100], [36, 1, 100], [24, 1, 100], [13, 1, 100], [6, 1, 100], [0, 1, 100], [0, 1, 85], [0, 1, 70], [0, 1, 55], [0, 1, 40]], 'brake': [[370, 0, 100, 1], [221, 0, 100, 1], [170, 0, 100, 1], [131, 0, 100, 1], [108, 1, 100, 1], [81, 1, 100, 1], [66, 1, 100, 1], [51, 1, 100, 1], [36, 1, 100, 1], [24, 1, 100, 1], [13, 1, 100, 1], [6, 1, 100, 1]]}, 'driver': {'traction': [1, 9, 13, 17], 'brake': [1, 5, 9, 12]}, 'engine': {'constant': 3, 'resistance': 10}, 'parameters': {'type': 'reostat', 'traction': [17, 4], 'brake': [12, 4]}, 'drv_position': -4, 'con_position': 12, 'drv_limits': [-4, 4], 'peril_current': 330},{
            "air_friction_coef":18,
            "brake_cyllinders":8,
            "engines":4,
            "mass":28000,
            "radius":0.51,
            "reductor":7.143,

            "cars":2,
            "motorised":2,
            "pressurised":2,
        })

working = True

while working:
    clicked = False
    released = False
    scroll = 0
    pressed = []
    uni = ""

    screen.fill((0,0,0))

    for evt in pg.event.get():
        if evt.type == pg.QUIT:
            working = False
        elif evt.type == pg.KEYDOWN:
            pressed.append(evt.key)

            uni += evt.unicode
            if evt.key == pg.K_d: print(system.controller)
        elif evt.type == pg.MOUSEBUTTONDOWN and evt.button in [1,2,3]:
            clicked = True
        elif evt.type == pg.MOUSEBUTTONUP and evt.button in [1,2,3]:
            released = True
        elif evt.type == pg.MOUSEWHEEL:
            scroll = evt.y
    m_pos = pg.mouse.get_pos()
    m_btn = pg.mouse.get_pressed()
    kbd = pg.key.get_pressed()

    system.driver_controller(screen, (m_pos, m_btn, clicked, scroll), pressed, uni)

    #system.controller_editor(screen, (m_pos, m_btn, clicked, scroll), pressed, uni)

    z = [
        f"fps: {round(clock.get_fps())}",
        f"amp: {system.eng_current}",
        f"vel: {round(system.velocity*3.6,2)}",
        f"RKP: {system.electrical['con_position']}",
        f"TKP: {system.pneumatic['pos']}",
    ]

    for enum, line in enumerate(z):
        ptext = font.render(line,True,(240,240,240),(0,0,0))
        screen.blit(ptext,(20,20+30*enum))

    pg.display.update()
    clock.tick(60)


system.alive = False
print(system.dump())
pg.quit()'''
