# leitmotif**2
# for ETN and ETN only

import pygame as pg

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