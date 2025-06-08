#шняга-утилита для вольтажей

win_size = (800,600)
import pygame as pg
pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(win_size, pg.SRCALPHA)
font = pg.font.SysFont("verdana",20)

radius = 0.51
koef = 70/19

eng_const = 7
eng_res = 0.4

peril_current = [300]*11+[200]*2

resistances_series = [3.43, 2.86, 2.29, 1.71, 1.14, 0.56, 0, 0.97, 0.55, 0.35, 0.15, 0.0, 0.0]
voltages = [""]*13
engine_res_coef = [4]*7+[1]*6
engine_eds_coef = [4]*7+[2]*6
#funny_thing_i_forgor = [1]*7+[2]*6
spec_divide = [1]*7+[2]*6
f = [0]*12+[0.15]

rk = 0
cv = 0

def calc():
    rk = 0
    points = []

    for velocity in range(600):
        #voltage = v[rk] #(1500*eng_res/(engine_amt[rk]*eng_res+resistances_series[rk]))/spec_divide[rk]
        #voltages[rk] =voltage
        rads = velocity/10/3.6/radius*koef

        amps = (1500-engine_eds_coef[rk]*rads*eng_const*(1-f[rk]))/(engine_res_coef[rk]*eng_res+resistances_series[rk])
        if amps < peril_current[rk] and rk+1 < len(resistances_series):
            rk+=1
        points.append([amps,580-velocity])


    screen.fill((32,32,32))
    for i in range(12): pg.draw.line(screen,(255,210+(45 if i%2==0 else 0),210), (0,580-50*i),(800,580-50*i))
    for i in range(10): pg.draw.line(screen,(210,210,255), (0+i*100,0),(0+i*100,1000))
    pg.draw.lines(screen,(210,210,210),False,points,2)
    for i, q in enumerate([f"current {cv+1}", f"res {resistances_series[cv]}"]):
        t = font.render(q,True,(250,250,250),(0,0,0))
        screen.blit(t, (20,20*i))
    pg.display.update()

calc()
print(voltages)

working = True
while working:
    for evt in pg.event.get():
        if evt.type == pg.QUIT: working = False
        elif evt.type == pg.KEYDOWN:
            if pg.key.get_pressed()[pg.K_LALT]:
                if evt.key == pg.K_UP:eng_const+=0.05
                if evt.key == pg.K_DOWN:eng_const-=0.05
                if evt.key == pg.K_RIGHT:eng_res+=0.01
                if evt.key == pg.K_LEFT:eng_res-=0.01
            else:
                if evt.key == pg.K_UP:cv+=1
                if evt.key == pg.K_DOWN:cv-=1
                if evt.key == pg.K_RIGHT:resistances_series[cv]+=0.01
                if evt.key == pg.K_LEFT:resistances_series[cv]-=0.01
            calc()

pg.quit()
print(resistances_series)
print(eng_const, eng_res)
