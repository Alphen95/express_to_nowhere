import math

def angle(sin, cos):
    a_acos = math.acos(cos)
    if sin < 0:
        ang = math.degrees(-a_acos) % 360
    else: 
        ang = math.degrees(a_acos)
    return ang

def create_rail(idt, start, end):
    rail = Rail(idt)

    rail.s_pos, rail.s_axis, rail.s_links = start
    rail.e_pos, rail.e_axis, rail.e_links = end

    rail.s_pos = [i*256+0.5 for i in rail.s_pos]
    rail.e_pos = [i*256+0.5 for i in rail.e_pos]

    rail.build()
    return rail


class Rail:
    def __init__(self, identifier):
        self.s_pos = None # голова рельсины
        self.s_axis = None # ось [x/y] головы рельсины
        self.s_links = [] # к кому голова рельсы коннектится

        self.e_pos = None # хвост рельсины
        self.e_axis = None # ось [x/y] хвоста рельсины
        self.e_links = [] # к кому хвост рельсы коннектится

        self.rd = 28
        self.ud = 128

        self.identifier = identifier
        self.discrete = 10

    def build(self):
        ma_x = max(self.s_pos[0], self.e_pos[0]) # max x
        mi_x = min(self.s_pos[0], self.e_pos[0]) # min x

        ma_y = max(self.s_pos[1], self.e_pos[1]) # max y
        mi_y = min(self.s_pos[1], self.e_pos[1]) # min y

        a = self.s_pos
        b = self.e_pos

        self.render_points = []

        if self.s_axis == self.e_axis:
            #single-axial actions

            if ((self.s_axis == "x" and ma_y == mi_y) or (self.e_axis == "y" and ma_x == mi_x)) and a[2] == b[2]:
                # straight
                self.render_points = [a, b]
            elif self.s_axis == "x":
                # spline in X axis
                self.render_points = [
                    a, 
                    ((a[0]+b[0])/2, a[1], (a[2]+b[2])/2), 
                    ((a[0]+b[0])/2, b[1], (a[2]+b[2])/2), 
                    b
                ]
            elif self.s_axis == "y":
                # spline in Y axis
                self.render_points = [
                    a, 
                    (a[0], (a[1]+b[1])/2, (a[2]+b[2])/2), 
                    (b[0], (a[1]+b[1])/2, (a[2]+b[2])/2), 
                    b
                ]

        else:
            #two-axial actions

            if self.s_axis == "y" and self.e_axis == "x":
                if ma_x == self.s_pos[0]:
                    # u-shape
                    self.render_points = [
                        self.s_pos,
                        (ma_x, self.e_pos[1], (a[2]+b[2])/2),
                        self.e_pos
                    ]
                else:
                    # n-shape
                    self.render_points = [
                        self.s_pos, 
                        (mi_x, self.e_pos[1], (a[2]+b[2])/2), 
                        self.e_pos
                    ]
                
            elif self.s_axis == "x" and self.e_axis == "y":
                if ma_y == self.s_pos[1]:
                    # <-shape
                    self.render_points = [
                        self.s_pos, 
                        (self.e_pos[0], ma_y, (a[2]+b[2])/2), 
                        self.e_pos
                    ]
                else:
                    # >-shape
                    self.render_points = [
                        self.s_pos, 
                        (self.e_pos[0], mi_y, (a[2]+b[2])/2), 
                        self.e_pos
                    ]


            #self.render_points = [start, ((start[0]+end[0])/2,start[1]), ((start[0]+end[0])/2,end[1]), end]


        self.render()

        if len(self.render_points) == 2:
            print(f"track {self.identifier} initialized, type - straight")
        elif len(self.render_points) == 3:
            print(f"track {self.identifier} initialized, type - curve")
        else:
            print(f"track {self.identifier} initialized, type - bezier")

    def render(self):
        self.points = []
        self.draw_points = []
        self.underlay_points = []
        l, r, ll, rr = [], [], [], []
        self.angles = []

        if len(self.render_points) == 2:

            self.points = self.render_points

            if self.points[0][0] - self.points[1][0] == 0:
                l = [
                    (self.points[0][0]-self.rd, self.points[0][1], self.points[0][2]),
                    (self.points[1][0]-self.rd, self.points[1][1], self.points[0][2]),
                ]
                r = [
                    (self.points[0][0]+self.rd, self.points[0][1], self.points[0][2]),
                    (self.points[1][0]+self.rd, self.points[1][1], self.points[0][2]),
                ]
                ll = [
                    (self.points[0][0]-self.ud, self.points[0][1], self.points[0][2]),
                    (self.points[1][0]-self.ud, self.points[1][1], self.points[0][2]),
                ]
                rr = [
                    (self.points[0][0]+self.ud, self.points[0][1], self.points[0][2]),
                    (self.points[1][0]+self.ud, self.points[1][1], self.points[0][2]),
                ]
            else:
                l = [
                    (self.points[0][0], self.points[0][1]-self.rd, self.points[0][2]),
                    (self.points[1][0], self.points[1][1]-self.rd, self.points[0][2]),
                ]
                r = [
                    (self.points[0][0], self.points[0][1]+self.rd, self.points[0][2]),
                    (self.points[1][0], self.points[1][1]+self.rd, self.points[0][2]),
                ]
                ll = [
                    (self.points[0][0], self.points[0][1]-self.ud, self.points[0][2]),
                    (self.points[1][0], self.points[1][1]-self.ud, self.points[0][2]),
                ]
                rr = [
                    (self.points[0][0], self.points[0][1]+self.ud, self.points[0][2]),
                    (self.points[1][0], self.points[1][1]+self.ud, self.points[0][2]),
                ]

        elif len(self.render_points) == 3:

            x1, y1, z1 = self.render_points[0]
            x2, y2, z2 = self.render_points[1]
            x3, y3, z3 = self.render_points[2]

            dc = self.discrete

            for i in range(dc+1):
                t = i/dc

                dy = 2*((x3-2*x2+x1)*t+x2-x1)
                dx = -2*((y3-2*y2+y1)*t+y2-y1)
                dl = (dy**2+dx**2)**0.5
                dy /= dl
                dx /= dl

                self.points.append((
                    round(x1*(1-t)**2+2*x2*t*(1-t)+x3*(t**2)),
                    round(y1*(1-t)**2+2*y2*t*(1-t)+y3*(t**2)),
                    round(z1*(1-t)**2+2*z2*t*(1-t)+z3*(t**2)),
                ))

                l.append((self.points[-1][0]+self.rd*dx, self.points[-1][1]+self.rd*dy, self.points[-1][2]))
                r.append((self.points[-1][0]-self.rd*dx, self.points[-1][1]-self.rd*dy, self.points[-1][2]))
                ll.append((self.points[-1][0]+self.ud*dx,self.points[-1][1]+self.ud*dy, self.points[-1][2]))
                rr.append((self.points[-1][0]-self.ud*dx,self.points[-1][1]-self.ud*dy, self.points[-1][2]))

        elif len(self.render_points) == 4:

            x1,y1,z1 = self.render_points[0]
            x2,y2,z2 = self.render_points[1]
            x3,y3,z3 = self.render_points[2]
            x4,y4,z4 = self.render_points[3]

            dc = self.discrete

            for i in range(dc+1):
                t = i/dc

                dy = 3*(1-t)**2*(x2-x1)+6*t*(1-t)*(x3-x2)+3*t*t*(x4-x3)
                dx = -(3*(1-t)*(1-t)*(y2-y1)+6*t*(1-t)*(y3-y2)+3*t*t*(y4-y3))
                dl = (dy**2+dx**2)**0.5
                dy /= dl
                dx /= dl

                self.points.append((
                    round(x1*(1-t)**3+3*x2*t*((1-t)**2)+3*x3*(1-t)*(t**2)+x4*t**3),
                    round(y1*(1-t)**3+3*y2*t*((1-t)**2)+3*y3*(1-t)*(t**2)+y4*t**3),
                    round(z1*(1-t)**3+3*z2*t*((1-t)**2)+3*z3*(1-t)*(t**2)+z4*t**3)
                ))

                l.append((self.points[-1][0]+self.rd*dx, self.points[-1][1]+self.rd*dy, self.points[-1][2]))
                r.append((self.points[-1][0]-self.rd*dx, self.points[-1][1]-self.rd*dy, self.points[-1][2]))
                ll.append((self.points[-1][0]+self.ud*dx,self.points[-1][1]+self.ud*dy, self.points[-1][2]))
                rr.append((self.points[-1][0]-self.ud*dx,self.points[-1][1]-self.ud*dy, self.points[-1][2]))
        
        stack = ["",""]

        self.angles = [[],[]]

        self.vectors = [[],[]]

        for point in self.points:
            stack = [stack[1],point]
            if stack[0] != "":
                #if (stack[0][1]-stack[1][1]) != 0:
                dx = stack[1][0]-stack[0][0]
                dy = stack[1][1]-stack[0][1]
                dz = stack[1][2]-stack[0][2]
                dl = (dx**2+dy**2)**0.5

                self.angles[0].append(round(angle(dx/dl, dy/dl),2))
                self.vectors[0].append((dx/dl, dy/dl, dz/dl))

                #else:
                #    self.angles.append(0)

        stack = ["",""]

        for point in reversed(self.points):
            stack = [stack[1],point]
            if stack[0] != "":
                #if (stack[0][1]-stack[1][1]) != 0:
                dx = stack[1][0]-stack[0][0]
                dy = stack[1][1]-stack[0][1]
                dz = stack[1][2]-stack[0][2]
                dl = (dx**2+dy**2)**0.5

                self.angles[1].append(round(angle(dx/dl, dy/dl),2))
                self.vectors[1].append((dx/dl, dy/dl, dz/dl))

        self.angles[1] = self.angles[1][::-1]
        self.vectors[1] = self.vectors[1][::-1]

        scale = 90/128
        for point in self.points:
            x, y, z = point
            
            x *= scale
            y *= scale
            dx = ((x - y))
            dy = ((x + y)*0.5)
            self.draw_points.append((dx, dy, z))

        self.l_track = []
        self.r_track = []
        self.raw_up_l = ll
        self.raw_up_r = rr

        for point in l:
            x, y, z = point
            
            x *= scale
            y *= scale
            dx = ((x - y))
            dy = ((x + y)*0.5)
            self.l_track.append((int(dx),int(dy), z))
            
        for point in r:
            x, y, z = point
            
            x *= scale
            y *= scale
            dx = ((x - y))
            dy = ((x + y)*0.5)
            self.r_track.append((int(dx),int(dy), z))
        
        self.underlay_points_l = []
        self.underlay_points_r = []

        for point in ll:
            x, y, z = point
            
            x *= scale
            y *= scale
            dx = ((x - y))
            dy = ((x + y)*0.5)
            self.underlay_points_l.append((int(dx),int(dy), z))

        for point in rr:
            x, y, z = point
            
            x *= scale
            y *= scale
            dx = ((x - y))
            dy = ((x + y)*0.5)
            self.underlay_points_r.append((int(dx),int(dy), z))
        
                    
