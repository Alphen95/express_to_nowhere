import math

class Rail:
    def __init__(self, identifier):
        self.pos_a = (0,0)
        self.pos_b = (0,0)
        self.identifier = identifier


    def build(self):
        if self.pos_a < self.pos_b:
            self.start = self.pos_a
            self.end = self.pos_b
        else:
            self.start = self.pos_b
            self.end = self.pos_a


        self.discrete = 20

        start = self.start
        end = self.end

        self.render_points = []

        if self.start[1] == self.end[1]:
            self.render_points = [start, end]
        else:
            self.render_points = [start, ((start[0]+end[0])/2,start[1]), ((start[0]+end[0])/2,end[1]), end]


        self.render()

        if len(self.render_points) == 2:
            print(f"track {self.identifier} initialized, type - straight")
        else:
            print(f"track {self.identifier} initialized, type - bezier")

    def render(self):
        self.points = []
        self.angles = []

        if len(self.render_points) == 2:

            self.points = self.render_points

        elif len(self.render_points) == 4:

            x1,y1 = self.render_points[0]
            x2,y2 = self.render_points[1]
            x3,y3 = self.render_points[2]
            x4,y4 = self.render_points[3]

            for i in range(self.discrete+1):
                t = i/self.discrete
                self.points.append((
                    round(x1*(1-t)**3+3*x2*t*((1-t)**2)+3*x3*(1-t)*(t**2)+x4*t**3),
                    round(y1*(1-t)**3+3*y2*t*((1-t)**2)+3*y3*(1-t)*(t**2)+y4*t**3)
                ))
        
        stack = ["",""]

        for point in self.points:
            stack = [stack[1],point]
            if stack[0] != "":
                if (stack[0][1]-stack[1][1]) != 0:
                    self.angles.append(round(
                        (90+math.degrees(math.atan((stack[0][0]-stack[1][0])/(stack[0][1]-stack[1][1]))))
                    ))
                    self.angles[-1] += 180 if stack[0][1]-stack[1][1] < 0 else 0
                else:
                    self.angles.append(0)
