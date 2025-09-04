#EXP TO:[Nowhere]

import pygame as pg
import os
import threading
import random
import train
import isometry as isometry
import rails_iso as rails_m
import leitmotifplus as leitmotif
import json
import socket

win_size = (0,0)#(800,600)
version = "v0.6 Halle & Unity"


pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(win_size, pg.SRCALPHA | pg.HWSURFACE | pg.FULLSCREEN)
font = pg.font.Font("./res/font.ttf",20)
dfont = pg.font.Font("./res/dots.otf",28)
sfont = pg.font.Font("./res/font.ttf",24)

win_size = screen.get_size()
win_size = (win_size[0],win_size[1])

working = True
screenshot_mode = False
tile_size = 256
ct, fg, bg = (tile_size/2, tile_size/2), (tile_size, tile_size), (0,0)

route_map = {
    None:[" X "],

    "b": ["(B)"],
    "d": ["<D>"],
    "t": ["(T)"],

    "k": ["(K)"],
    "m": ["(M)"],
    "j": ["<J>"],

    "1": ["<1>"],
    "2": ["(2)"],
    "3": ["(3)"],

    "4": ["(4)"],

    "5": ["<5>"],
}

tile_sheet = pg.image.load("res/tiles.png")
subwmap = pg.image.load("res/map.png")
subwmap = pg.transform.smoothscale(subwmap, [i/2 for i in subwmap.get_size()])

player = isometry.Camera(win_size)

temp_trains = []
connected = False
connection_thread = None
ip = "127.0.0.1"

def socketThread(client_socket):
    global consists, temp_trains, connected, player, curc, mode, own_uid

    while connected:
        #try:
        tt = []
        a = []
        for c in consists:
            for enum, tr in enumerate(consists[c].trains):
                tt.append(plain_dummy_encode(tr, c, consists[c].axial_velocity))
                if c == curc and follow:
                    if consists[curc].reversor_vector == -1 and enum == 0: player.pos = tr.pos
                    if consists[curc].reversor_vector == 1 and enum+1 == len(consists[c].trains): player.pos = tr.pos
                a.append(Dummy(tr, c, consists[c].axial_velocity))

        client_socket.send((json.dumps(tt) + "=").encode())
        received = ""
        while True:
            received += client_socket.recv(16384).decode("utf-8")
            if not received:
                connected = False
            if received[-1] == "=":
                received = received[:-1]
                break
        received = json.loads(received)
        #print(received)
        for playerpack in received:
            for tr in playerpack: 
                if tr != [] and tr[0] != own_uid:a.append(DecoderDummy(tr))
        temp_trains = a

        #except Exception as exc:
        #    print("[ERROR]", "An unexpected error occured while client was connecting")
        #    print("[EXCEPTION]", exc)
        #    mode = "title"
        #    connected = False

sprite_load_params = [ # name - (x|y) - (stacks|offset|repeats) - rotation/flip - alignment
    ["cyrok_cx", (0,0), (5,6,1), 0, ct],
    ["cyrok_cy", (0,0), (5,6,1), 90, ct],
    ["cyrok_xr", (0,5), (5,6,1), 0, ct],
    ["cyrok_xl", (0,5), (5,6,1), 180, ct],
    ["cyrok_yl", (0,5), (5,6,1), 90, ct],
    ["cyrok_yr", (0,5), (5,6,1), 270, ct],
    ["halfcyrok_xr", (0,10), (5,6,1), 0, ct],
    ["halfcyrok_xl", (0,10), (5,6,1), 180, ct],
    ["halfcyrok_yl", (0,10), (5,6,1), 90, ct],
    ["halfcyrok_yr", (0,10), (5,6,1), 270, ct],
    ["sign_x", (0,15), (6,24,1), 0, ct],
    ["sign_y", (0,15), (6,24,1), 90, ct],
    
    ["u_base", (1,12), (1,0,1), 0, ct],
    ["u_corner_a", (1,13), (1,0,1), 90, ct],
    ["u_corner_b", (1,13), (1,0,1), 180, ct],
    ["u_corner_c", (1,13), (1,0,1), 270, ct],
    ["u_corner_d", (1,13), (1,0,1), 0, ct],

    ["u_bridge_base", (29,0), (8,-7,1), 0, ct],
    ["u_bridge_corner_a", (29,10), (8,-7,1), 90, ct],
    ["u_bridge_corner_b", (29,10), (8,-7,1), 180, ct],
    ["u_bridge_corner_c", (29,10), (8,-7,1), 270, ct],
    ["u_bridge_corner_d", (29,10), (8,-7,1), 0, ct],
    
    ["u_wall_a", (1,14), (1,0,6), 0, bg],
    ["u_wall_b", (1,14), (1,0,6), 270, bg],
    ["u_wall_c", (1,14), (1,0,6), 180, fg],
    ["u_wall_d", (1,14), (1,0,6), 90, fg],

    ["u_fence_a", (1,15), (3,0,1), 0, bg],
    ["u_fence_b", (1,15), (3,0,1), 270, bg],
    ["u_fence_c", (1,15), (3,0,1), 180, fg],
    ["u_fence_d", (1,15), (3,0,1), 90, fg],
    
    ["u_wall_ovg_a", (29,20), (5, 0,1), 0, bg],
    ["u_wall_ovg_b", (29,20), (5, 0,1), 270, bg],
    ["u_wall_ovg_c", (29,16), (9,-4,1), 180, fg],
    ["u_wall_ovg_d", (29,16), (9,-4,1), 90, fg],
    
    ["plt",     (1,0), (6,0,1),  0, ct],
    ["plt_exl", (1,6), (6,0,1),  0, fg],
    ["plt_exr", (1,6), (6,0,1), 180, bg],
    ["plt_eyl", (1,6), (6,0,1), 270, fg],
    ["plt_eyr", (1,6), (6,0,1),  90, bg],

    ["plt_und_a", (1,18), (6,0,1),  0, ct],
    ["plt_und_b", (1,18), (6,0,1), 90, ct],
    ["plt_und_c", (1,18), (6,0,1),180, ct],
    ["plt_und_d", (1,18), (6,0,1),270, ct],
    
    ["soundwall_xl", (2,0), (29,0,1),  0, bg],
    ["soundwall_xr", (2,0), ( 6,0,1),180, fg],
    ["soundwall_yl", (2,0), (29,0,1),270, bg],
    ["soundwall_yr", (2,0), ( 6,0,1), 90, fg],
    
    ["soundwall_sign_xr", (3,0), (29,0,1), 180, bg],
    ["soundwall_sign_yl", (3,0), (29,0,1), 270, bg],
    
    ["pillar_orange_xl", (0,21), (1,6,24),   0, fg],
    ["pillar_orange_xr", (0,21), (1,6,24), 180, bg],
    ["pillar_orange_yl", (0,21), (1,6,24), 270, bg],
    ["pillar_orange_yr", (0,21), (1,6,24),  90, fg],

    ["pillar_beige_xl", (0,22), (1,6,24),   0, fg],
    ["pillar_beige_xr", (0,22), (1,6,24), 180, bg],
    ["pillar_beige_yl", (0,22), (1,6,24), 270, bg],
    ["pillar_beige_yr", (0,22), (1,6,24),  90, fg],
    
    ["hloc-oct_xr", (4,0), (30,0,1),  0, bg],
    ["hloc-oct_xl", (4,0), (6,0,1),180, fg],

    ["cmkt_xr", (5,0), (24,6,1),  0, bg],
    ["cmkt_xl", (5,0), (24,6,1),180, fg],

    ["kirv_xr", (6,0), (24,6,1),  0, bg],
    ["kirv_xl", (6,0), (24,6,1),180, fg],
    ["kirv_pillar_xr", (0,23), (1,6,24),  0, bg],
    ["kirv_pillar_xl", (0,23), (1,6,24),180, fg],
    
    ["krnh-oct_xr", (7,0), (24,6,1),  0, bg],
    ["krnh-oct_xl", (7,0), (24,6,1),180, fg],
    ["krnh-oct_pillar_xr", (8,0), (24,6,1),  0, bg],
    ["krnh-oct_pillar_xl", (8,0), (24,6,1),180, fg],
    
    ["wemb_xr", (9,0), (24,6,1), 0, bg],
    ["wemb_xl", (9,0), (24,6,1), (1,0), fg],
    ["wemb_alt_xr", (10,0), (24,6,1), 0, bg],
    ["wemb_alt_xl", (10,0), (24,6,1), (1,0), fg],
    
    ["tast_xr", (11,0), (24,6,1), 0, bg],
    ["tast_xl", (11,0), (24,6,1), (1,0), fg],
    
    ["bnpk_xr", (12,0), (30,0,1), 0, bg],
    ["bnpk_xl", (12,0), (6,0,1), (1,0), fg],
    ["bnpk_pillar_xr", (13,0), (24,6,1), 0, bg],
    ["bnpk_pillar_xl", (13,0), (24,6,1), (1,0), fg],
    
    ["dage", (14,0), (24,6,1), 90, ct],
    ["dage_alt", (15,0), (24,6,1), 90, ct],
    
    ["mlwk", (16,0), (24,6,1), 90, ct],
    ["mlwk_alt", (17,0), (24,6,1), 90, ct],
    ["mlwk_exit_a", (18,0), (24,6,1), 90, ct],
    ["mlwk_exit_b", (18,0), (24,6,1), 270, ct],
    
    ["unmg_xr", (19,0), (24,6,1), 0, bg],
    ["unmg_xl", (19,0), (24,6,1), (1,0), fg],
    ["unmg_pillar_xr", (20,0), (24,6,1), 0, fg],
    ["unmg_pillar_xl", (20,0), (24,6,1), (1,0), bg],
    
    ["usmr_xr", (21,0), (24,6,1), 0, bg],
    ["usmr_xl", (21,0), (24,6,1), (1,0), fg],
    ["usmr_pillar_xr", (22,0), (24,6,1), 0, fg],
    ["usmr_pillar_xl", (22,0), (24,6,1), (1,0), bg],
    
    ["zrge-oct_xr", (23,0), (30,0,1), 0, bg],
    ["zrge-oct_xl", (23,0), (6 ,0,1), (1,0), fg],
    ["zrge-oct_pillar_xr", (24,0), (24,6,1), 0, fg],
    ["zrge-oct_pillar_xl", (24,0), (24,6,1), (1,0), bg],
    
    ["lesq_xr", (25,0), (24,0,1), 0, bg],
    ["lesq_xl", (25,0), (24,0,1), (1,0), fg],
    ["lesq_pillar_xr", (26,0), (24,6,1), 0, fg],
    ["lesq_pillar_xl", (26,0), (24,6,1), (1,0), bg],
    
    ["cuhl_xr", (27,0), (30,0,1), 0, bg],
    ["cuhl_xl", (27,0), (6 ,0,1), (1,0), fg],
    ["cuhl_pillar_xr", (0,24), (1,6,24), 0, fg],
    ["cuhl_pillar_xl", (0,24), (1,6,24), (1,0), bg],
    
    ["encg_yl", (28,0), (24,6,1), 0, fg],
    ["encg_yr", (28,0), (24,6,1), (0,1), bg],

    ["roof_center", (30,0), (24,6,1), 90, ct],
    ["roof_center_sign", (31,0), (24,6,1), 90, ct],
    ["roof_center_alt", (30,0), (24,6,1), 0, ct],
    ["roof_center_alt_sign", (31,0), (24,6,1), 0, ct],
    ["roof_side_xr", (32,0), (26,6,1), 0, ct],
    ["roof_side_sign_xr", (33,0), (26,6,1), 0, ct],
    ["roof_side_xl", (32,0), (26,6,1), (1,0), ct],
    ["roof_side_sign_xl", (33,0), (26,6,1), (1,0), ct],

    ["ovg_wall_xr", (34,0), (11,6,1), 0, ct],
    ["ovg_wall_corner_b_xr", (35,0), (11,6,1), 0, ct],
    ["ovg_wall_corner_a_xr", (35,0), (11,6,1), (0,1), ct],
    ["ovg_roof_xr", (36,0), (26,6,1), (0,1), ct],
    ["ovg_wall_xl", (34,0), (11,6,1), (1,0), ct],
    ["ovg_wall_corner_b_xl", (35,0), (11,6,1), (1,0), ct],
    ["ovg_wall_corner_a_xl", (35,0), (11,6,1), (1,1), ct],
    ["ovg_roof_xl", (36,0), (26,6,1), (1,0), ct],
    
    ["qrst_yr", (37,0), (30,0,1), 270, bg],
    ["qrst_yl", (37,0), (6 ,0,1), (1,0,270), fg],
    ["red_pillar_yr", (0,25), (1,6,24), 270, fg],
    ["red_pillar_yl", (0,25), (1,6,24), (1,0,270), bg],
    ["red_pillar_xr", (0,25), (1,6,24), 0, fg],
    ["red_pillar_xl", (0,25), (1,6,24), (1,0), bg],

    ["hfri-aks_yr", (38,0), (30,0,1), 270, bg],
    ["hfri-aks_yl", (38,0), (6 ,0,1), (1,0,270), fg],
    
    ["krnh-aks_yr", (39,0), (30,0,1), 270, bg],
    ["krnh-aks_yl", (39,0), (6 ,0,1), (1,0,270), fg],
    ["krnh-aks_pillar_yr", (40,0), (24,6,1), 270, fg],
    ["krnh-aks_pillar_yl", (40,0), (24,6,1), (1,0,270), bg],

    ["akgd_yr", (41,0), (30,0,1), 270, bg],
    ["akgd_yl", (41,0), (6 ,0,1), (1,0,270), fg],
    
    ["mhnb-aks_yr", (42,0), (30,0,1), 270, bg],
    ["mhnb-aks_yl", (42,0), (6 ,0,1), (1,0,270), fg],
    ["mhnb-aks_pillar_yr", (0,26), (1,6,24), 270, fg],
    ["mhnb-aks_pillar_yl", (0,26), (1,6,24), (1,0,270), bg],

    ["krzl_xr", (43,0), (24,6,1), 0, bg],
    ["krzl_xl", (43,0), (24,6,1), (1,0), fg],

    ["hbdn_xr", (44,0), (24,6,1), 0, bg],
    ["hbdn_xl", (44,0), (24,6,1), (1,0), fg],

    ["expo_xr", (45,0), (30,0,1), 0, bg],
    ["expo_xl", (45,0), (6,0,1), (1,0), fg],
    ["expo_pillar", (46,0), (24,0,1), 0, ct],

    ["bash_xr", (47,0), (30,0,1), 0, bg],
    ["bash_xl", (47,0), ( 6,0,1), (1,0), fg],

    ["akbt_xr", (48,0), (24,6,1), 0, bg],
    ["akbt_xl", (48,0), (24,6,1), (1,0), fg],
    ["akbt_pillar_xr", (49,0), (24,6,1), 0, fg],
    ["akbt_pillar_xl", (49,0), (24,6,1), (1,0), bg],

    ["zhkv_xr", (50,0), (24,6,1), 0, bg],
    ["zhkv_xl", (50,0), (24,6,1), (1,0), fg],

    ["kash_xr", (51,0), (30,0,1), 0, bg],
    ["kash_xl", (51,0), ( 6,0,1), (1,0), fg],
    ["kash_exit_xr", (52,0), (24,6,1), 0, bg],
    ["kash_exit_xl", (52,0), (24,6,1), (1,0), fg],
    ["kash_pillar_xr", (53,0), (24,6,1), 0, bg],
    ["kash_pillar_xl", (53,0), (24,6,1), (1,0), fg],
    
    ["mhnb-kms_xr", (54,0), (30,0,1), 0, bg],
    ["mhnb-kms_xl", (54,0), (6 ,0,1), (1,0), fg],
    ["green_pillar_xr", (0,27), (1,6,24), 0, fg],
    ["green_pillar_xl", (0,27), (1,6,24), (1,0), bg],
    
    ["14st_xr", (55,0), (24,6,1), 0, bg],
    ["14st_xl", (55,0), (24,6,1), (1,0), fg],
    
    ["eist_xr", (56,0), (30,0,1), 0, bg],
    ["eist_xl", (56,0), (6 ,0,1), (1,0), fg],
    ["eist_pillar_xr", (57,0), (24,6,1), 0, fg],
    ["eist_pillar_xl", (57,0), (24,6,1), (1,0), bg],
    
    ["hlkm-kms_xr", (58,0), (30,0,1), 0, bg],
    ["hlkm-kms_xl", (58,0), (6 ,0,1), (1,0), fg],
    ["hlkm-kms_down_a", (59,0), (12,0,1), 0, ct],
    ["hlkm-kms_down_b", (59,0), (12,0,1), (0,1), ct],
    ["turq_pillar_xr", (0,28), (1,6,24), 0, fg],
    ["turq_pillar_xl", (0,28), (1,6,24), (1,0), bg],
    ["turq_pillar_yr", (0,28), (1,6,24), 270, fg],
    ["turq_pillar_yl", (0,28), (1,6,24), (1,0,270), bg],
    
    ["50km_xr", (60,0), (24,6,1), 0, bg],
    ["50km_xl", (60,0), (24,6,1), (1,0), fg],
    ["50km_pillar_xr", (61,0), (24,6,1), 0, fg],
    ["50km_pillar_xl", (61,0), (24,6,1), (1,0), bg],
    
    ["glum_xr", (62,0), (30,0,1), 0, bg],
    ["glum_xl", (62,0), (6 ,0,1), (1,0), fg],
    ["glum_radio_c", (63,0), (24,6,1), 0, ct],
    ["glum_radio_e2", (64,0), (24,6,1), 0, ct],
    ["glum_radio_e1", (64,0), (24,6,1), (0,1), ct],
    
    ["yrzn_c_xr", (65,0), (30,0,1), 0, bg],
    ["yrzn_b_xr", (66,0), (30,0,1), 0, bg],
    ["yrzn_a_xr", (65,0), (30,0,1), (0,1), bg],
    ["yrzn_c_xl", (65,0), (6 ,0,1), (1,0), fg],
    ["yrzn_b_xl", (66,0), (6 ,0,1), (1,0), fg],
    ["yrzn_a_xl", (65,0), (6 ,0,1), (1,1), fg],
    ["yrzn_pillar_xr", (67,0), (24,6,1), 0, fg],
    ["yrzn_pillar_xl", (67,0), (24,6,1), (1,0), bg],
    
    ["hbst_xr", (68,0), (24,6,1), 0, bg],
    ["hbst_xl", (68,0), (24,6,1), (1,0), fg],
    
    ["bshm_xr", (69,0), (30,0,1), 0, bg],
    ["bshm_xl", (69,0), (6 ,0,1), (1,0), fg],
    ["bshm_pylon", (70,0), (24,6,1), 0, fg],
    
    ["avst_yr", (71,0), (30,0,1), 270, bg],
    ["avst_yl", (71,0), (6,0,1), (1,0,270), fg],
    ["avst_pillar_yr", (72,0), (24,6,1), 270, fg],
    ["avst_pillar_yl", (72,0), (24,6,1), (1,0,270), bg],
    
    ["alma_yr", (73,0), (24,6,1), 270, bg],
    ["alma_yl", (73,0), (24,6,1), (1,0,270), fg],
    
    ["dstk_upper_name_xr", (74,0), (30,0,1), 0, bg],
    ["dstk_upper_xr", (75,0), (30,0,1), 0, bg],
    ["dstk_upper_name_xl", (74,0), (6,0,1), (1,0), bg],
    ["dstk_upper_xl", (75,0), (6,0,1), (1,0), bg],
    ["dstk_lower_name_xr", (76,0), (30,0,1), 0, bg],
    ["dstk_lower_xr", (77,0), (30,0,1), 0, bg],
    ["dstk_lower_name_xl", (76,0), (6,0,1), (1,0), bg],
    ["dstk_lower_xl", (77,0), (6,0,1), (1,0), bg],
    ["dstk_underpass_ar", (78,0), (11,0,1), (1,0), ct],
    ["dstk_underpass_al", (78,0), (11,0,1), (0,0), ct],
    ["dstk_underpass_br", (78,0), (11,0,1), (1,1), ct],
    ["dstk_underpass_bl", (78,0), (11,0,1), (0,1), ct],
    ["dstk_platform", (78,11), (6,0,1), 0, ct],
    ["dstk_plt_er", (78,17), (6,0,1), 0, fg],
    ["dstk_plt_el", (78,17), (6,0,1), (1,0), bg],
    ["dstk_sign_br", (79,0), (9,6,1), (1,0), ct],
    ["dstk_sign_bl", (79,0), (9,6,1), (0,0), ct],
    ["dstk_sign_ar", (79,0), (9,6,1), (1,1), ct],
    ["dstk_sign_al", (79,0), (9,6,1), (0,1), ct],
    ["dstk_plt_r", (80,0), (6,0,1), (1,0), ct],
    ["dstk_plt_l", (80,0), (6,0,1), (0,0), ct],
    ["dstk_pillar_ar", (80,6), (24,6,1), (1,0), ct],
    ["dstk_pillar_al", (80,6), (24,6,1), (0,0), ct],
    ["dstk_stairs_ar", (81,6), (24,6,1), (1,0), ct],
    ["dstk_stairs_al", (81,6), (24,6,1), (0,0), ct],
    ["dstk_stairs_br", (81,6), (24,6,1), (1,1), ct],
    ["dstk_stairs_bl", (81,6), (24,6,1), (0,1), ct],
    
    ["agizel_bridge_r", (87,0), (30,0,1), 0, bg],
    ["agizel_bridge_l", (87,0), (30,0,1), (1,0), fg],
    ["agizel_bridge_ar", (88,0), (30,0,1), 0, bg],
    ["agizel_bridge_al", (88,0), (30,0,1), (1,0), fg],
    ["agizel_bridge_br", (88,0), (30,0,1), (0,1), bg],
    ["agizel_bridge_bl", (88,0), (30,0,1), (1,1), fg],
    
    ["coop_yr", (82,0), (24,6,1), 0, bg],
    ["coop_yl", (82,0), (24,6,1), (1,0), fg],
    ["coop_pillar_yr", (83,0), (24,6,1), 0, fg],
    ["coop_pillar_yl", (83,0), (24,6,1), (1,0), bg],
    
    ["oren_yr", (84,0), (24,6,1), 0, bg],
    ["oren_yl", (84,0), (24,6,1), (1,0), fg],
    ["oren_roof_yr", (85,0), (24,6,1), 0, fg],
    ["oren_roof_yl", (85,0), (24,6,1), (1,0), bg],
    
    ["kshi_yr", (86,0), (30,6,1), 0, bg],
    ["kshi_yl", (86,0), (30,6,1), (1,0), fg],

    ["bash-hal_r", (89,0), (30,0,1), 270, bg],
    ["bash-hal_l", (89,0), (6,0,1), (1,0, 270), fg],
    ["yellow_pillar_xr", (0,29), (1,6,24), 0, fg],
    ["yellow_pillar_xl", (0,29), (1,6,24), (1,0), bg],
    ["yellow_pillar_yr", (0,29), (1,6,24), 270, fg],
    ["yellow_pillar_yl", (0,29), (1,6,24), (1,0,270), bg],

    ["hlkm-hal_r", (90,0), (24,6,1), 270, bg],
    ["hlkm-hal_l", (90,0), (24,6,1), (1,0, 270), fg],
    ["hlkm-hal_stairs_r", (91,0), (24,6,1), (0,1, 270), bg],
    ["hlkm-hal_stairs_l", (91,0), (24,6,1), (1,0, 270), fg],
    
    ["hloc-hal_r", (92,0), (30,0,1), 270, bg],
    ["hloc-hal_l", (92,0), (6,0,1), (1,0, 270), fg],
    ["hloc-hal_pillar_r", (93,0), (24,6,1), (0,1, 270), bg],
    ["hloc-hal_pillar_l", (93,0), (24,6,1), (1,0, 270), fg],
    
    ["hlzr-hal_r", (94,0), (24,6,1), 270, bg],
    ["hlzr-hal_l", (94,0), (24,6,1), (1,0, 270), fg],
    ["hlzr-hal_pillar_r", (95,0), (24,6,1), (0,1, 270), bg],
    ["hlzr-hal_pillar_l", (95,0), (24,6,1), (1,0, 270), fg],
    
    ["eztn_r", (98,0), (30,6,1), 270, bg],
    ["eztn_l", (98,0), (30,6,1), (1,0, 270), fg],
    ["eztn_pillar_r", (99,0), (24,6,1), (0,1, 270), bg],
    ["eztn_pillar_l", (99,0), (24,6,1), (1,0, 270), fg],
    
    ["glasswall_r", (96,0), (30,0,1), 270, bg],
    ["glasswall_l", (96,0), (30,0,1), (1,0, 270), fg],
    ["glasswall_low_r", (97,0), (11,0,1), 270, bg],
    ["glasswall_low_l", (97,0), (11,0,1), (1,0, 270), fg],

    ["vavi_plt", (101,0), (6,0,1), 270, ct],
    ["vavi_edge", (101,12), (6,0,1), 90, bg],
    ["vavi_stan", (100,0), (30,6,1), 270, bg],
    
    ["ahmt", (102,0), (30,6,1), 0, ct],
    ["ahmt_edge2", (103,0), (30,6,1), (0,1), ct],
    ["ahmt_edge1", (103,0), (30,6,1), 0, ct],
    
    ["small_plt_r", (104,0), (6,0,1), 0, ct],
    ["small_plt_l", (104,0), (6,0,1), (1,0), ct],
    
    ["avtr_r", (105,0), (30,6,1), 0, ct],
    ["avtr_l", (105,0), (30,6,1), (1,0), ct],
    
    ["12st_r", (106,0), (30,6,1), 0, ct],
    ["12st_l", (106,0), (30,6,1), (1,0), ct],
    
    ["smkh_r", (107,0),       (30,6,1), 270, ct],
    ["smkh_bench_r", (108,0), (30,6,1), 270, ct],
    ["smkh_l", (107,0),       (30,6,1), (1,0,270), ct],
    ["smkh_bench_l", (108,0), (30,6,1), (1,0,270), ct],
    
    ["octb_r", (109,0), (30,6,1), 0, ct],
    ["octb_edge1_r", (110,0), (30,6,1), (0,1), ct],
    ["octb_edge2_r", (110,0), (30,6,1), 0, ct],
    ["octb_l", (109,0), (30,6,1), (1,0), ct],
    ["octb_edge1_l", (110,0), (30,6,1), (1,1), ct],
    ["octb_edge2_l", (110,0), (30,6,1), (1,0), ct],
    
    ["mist_r", (111,0), (30,6,1), 0, ct],
    ["mist_l", (111,0), (30,6,1), (1,0), ct],
    
    ["zbaf_r", (112,0), (30,6,1), 0, ct],
    ["zbaf_l", (112,0), (30,6,1), (1,0), ct],

]

train_spawn_info = []
consist_names = []

def load_thread():
    global player, tile_sheet, sprite_load_params, train_spawn_info, consists
    for param_pack in sprite_load_params:
        player.sprites[param_pack[0]] = player.render_tile(
            pg.transform.rotate(tile_sheet.subsurface(param_pack[1][0]*64,(param_pack[1][1]+1)*64,64,param_pack[2][0]*64),90) # base surface
            ,(param_pack[2][0],param_pack[2][1],2,param_pack[2][2]), # stacks-offset-FIXED SCALE-repeats
            param_pack[4], # rotation/flip
            param_pack[3]  # align
        )
        
    for folder in os.listdir("packages/"):
        if os.path.isdir("packages/"+folder):
            if "pack.json" in os.listdir("packages/"+folder):
                with open("packages/"+folder+"/pack.json") as f: pack_info = json.loads(f.read())

                for tr in pack_info["trains"]: player.render_train("packages/"+folder+"/",tr)
                for con in pack_info["consists"]: 
                    train_spawn_info.append(con[1])
                    consist_names.append(con[0])

lt = threading.Thread(target=load_thread)
lt.start()

with open("world.json") as f:
    q = json.loads(f.read())
    rail_nodes, blockmap, aux_blockmap, underay_map, stations = q

with open("route_switches.json") as f: route_switches = json.loads(f.read())

player.blockmap = blockmap
player.auxmap = aux_blockmap
player.undermap = underay_map

st_tilemap = {}

for stat in stations:
    for x in range(min(stat[0][0], stat[1][0]), max(stat[0][0], stat[1][0])):
        for y in range(min(stat[0][1], stat[1][1]), max(stat[0][1], stat[1][1])):
            for z in range(min(stat[0][2], stat[1][2]), max(stat[0][2], stat[1][2])+1):
                st_tilemap[(x,y,z)] = (stat[2], stat[3])

tracks = {}


for node in rail_nodes:
    bx, by, bz = map(int, node.split(":"))
    sx, sy, sz = (bx+0.5)*tile_size, (by+0.5)*tile_size, bz*tile_size
    for axis in ["x","y"]:
        for rail_id in rail_nodes[node][axis][1]:
            if rail_id not in tracks: tracks[rail_id] = rails_m.Rail(rail_id)
            if tracks[rail_id].s_pos == None:
                tracks[rail_id].s_pos = (sx,sy,sz)
                tracks[rail_id].s_axis = axis
                tracks[rail_id].s_links = rail_nodes[node][axis][0]
            else:
                tracks[rail_id].e_pos = (sx,sy,sz)
                tracks[rail_id].e_axis = axis
                tracks[rail_id].e_links = rail_nodes[node][axis][0]

        for rail_id in rail_nodes[node][axis][0]:
            if rail_id not in tracks: tracks[rail_id] = rails_m.Rail(rail_id)
            if tracks[rail_id].s_pos == None:
                tracks[rail_id].s_pos = (sx,sy,sz)
                tracks[rail_id].s_axis = axis
                tracks[rail_id].s_links = rail_nodes[node][axis][1]
            else:
                tracks[rail_id].e_pos = (sx,sy,sz)
                tracks[rail_id].e_axis = axis
                tracks[rail_id].e_links = rail_nodes[node][axis][1]

do_not_draw = [301, 302, 297, 298]

for rail_id in tracks:
    tracks[rail_id].build()
    if rail_id in do_not_draw: tracks[rail_id].enable_underlay = False

player.rail_nodes = rail_nodes
player.tracks = tracks
train.tracks = tracks
train.nodes = rail_nodes
player.pos = [0*256,0,0]

player.scale = 1

class Dummy:
    def __init__(self, tr, c, vel):
        self.c = c
        self.vel = vel
        self.pos = [round(i,2) for i in tr.pos]
        self.size = tr.size
        self.angle = (tr.angle+tr.flipped*180-90)%360
        self.flipped = tr.flipped
        self.type = tr.type
        self.doors = tr.doors

class DecoderDummy:
    def __init__(self, plain):
        self.c, self.vel, self.pos, self.size, self.angle, self.flipped, self.type, self.doors = plain

def plain_dummy_encode(tr, c, vel):
    return [c, vel, [round(i,2) for i in tr.pos], tr.size, (tr.angle+tr.flipped*180-90)%360, tr.flipped, tr.type, tr.doors]



a = pg.Surface(win_size, pg.SRCALPHA)
a.fill((64,64,64,32))

consists = {}
curc = -1
q = 0

follow = True
spawn = False

spawnpoints = [
    ["[OCT] Energy College", 288], ["[OCT] City Culture Hall", 275], ["[OCT] Balanovo-Park", 553], ["[OCT] Milowsk Hwy", 160], # October Av & Dim
    ["[ZRG] Zorge St", 294], ["[ZRG] Hafuri St", 386], # Zorge & Hafuri
    ["[AKS] Quarry St", 438], ["[AKS] Karuanhorai", 389], ["[AKS] Kashkadan Lake", 535], # Aksakov & Mendeleev
    ["[KMS] Avrora St", 793], ["[KMS] Koishi St", 837], ["[KMS] Glumilino", 704], ["[KMS] Bashmebel'", 754],  # Komsomol, Orenburg & Avrora
    ["[HAL] Bashkortostan Mall", 845], ["[HAL] Vavilovskaja", 1005], ["[HAL] South Mihailovka", 1076], ["[HAL] Zabelskiy Airfield", 1106],  # Halle & Unity
]

spawn_window = leitmotif.Window((screen.get_width()-300-4, screen.get_height()/2-200, 300, 400), font, 26, {
    "label_title":{
        "active":True,"type":"label","align":"center","text":"Train spawner",
        "rect":[0,"indent","w","line_height"]
    },
    "list_station": {
        "active":True,"type":"item_list","items":[i[0] for i in spawnpoints],
        "rect":[0,"indent+line_height*1.33","w","line_height*6"]
    },
    "list_train": {
        "active":True,"type":"item_list","items":consist_names,
        "rect":[0,"indent+line_height*7.66","w","line_height*6"]
    },
    "button_spawn":{
        "active":True,"type":"button","text":"Spawn","align":"center",
        "rect":["2","indent+line_height*14","w/2-4","line_height"]
    },
    "button_spawn_arcade":{
        "active":True,"type":"button","text":"Spawn Arcade","align":"center",
        "rect":["w/2+2","indent+line_height*14","w/2-4","line_height"]
    },
})
spawn_window.recalculate()

i=0
while lt.is_alive() and working:
    for evt in pg.event.get():
        if evt.type == pg.QUIT:
            working = False

    screen.fill((32,32,32))
    t1 = font.render("Loading trains and tiles.",True, (255,255,255))
    t2 = font.render("(might take a while)",True, (255,255,255))
    t3 = font.render(["-","/","|","\\"][int(i)],True, (255,255,255)) 
    screen.blit(t1, (win_size[0]/2-t1.get_width()/2, win_size[1]/2-t1.get_height()*1.5))
    screen.blit(t2, (win_size[0]/2-t2.get_width()/2, win_size[1]/2-t1.get_height()*0.5))
    screen.blit(t3, (win_size[0]/2-t3.get_width()/2, win_size[1]/2+t1.get_height()*0.5))

    i = (i+1/15)%4

    pg.display.update()
    clock.tick(60)

mode = "title"
sound_play = {}
temp_trains = []

while working:
    clicked = False
    released = False
    pressed = []
    unicode = ""
    scroll = 0
    if curc == -1 or mode not in ["playing", "playing_mp"]: follow = False

    for evt in pg.event.get():
        if evt.type == pg.QUIT:
            working = False

        elif evt.type == pg.KEYDOWN:
            pressed.append(evt.key)
            if 32 <= evt.key%1000 <= 64 or evt.key in [1073,1078] or 91 <= evt.key%1000 <= 122:unicode+=evt.unicode

        elif evt.type == pg.MOUSEBUTTONDOWN:
            clicked = True

        elif evt.type == pg.MOUSEBUTTONUP:
            released = True

        elif evt.type == pg.MOUSEWHEEL:
            scroll = evt.y

    m_pos = pg.mouse.get_pos()
    m_btn = pg.mouse.get_pressed()

    mouse_state = (m_pos[0], m_pos[1], clicked, (m_btn[0] or m_btn[1] or m_btn[2]), (m_btn[0], m_btn[1], m_btn[2]))

    screen.fill((0,0,0))

    if mode == "title":
        for tr in consists:
            consists[tr].is_alive = False
            
        screen.fill((40,40,40))
        t = sfont.render("Express to Nowhere", True, (240,240,240))
        screen.blit(t, (20,win_size[1]/2-75))
        t = sfont.render(version, True, (240,240,240))
        screen.blit(t, (20,win_size[1]/2-45))
        t = sfont.render("> Singleplayer", True, (240,240,240))
        screen.blit(t, (20,win_size[1]/2-15))
        if m_btn[0] and 20 <= m_pos[0] <= 20+t.get_width() and win_size[1]/2-15 <= m_pos[1] <= win_size[1]/2-15+t.get_height():
            mode = "playing"
            player.pos = [0,0,0]
            curc = -1
            consists = {}
        t = sfont.render("> Multiplayer", True, (240,240,240))
        screen.blit(t, (20,win_size[1]/2+15))
        if m_btn[0] and 20 <= m_pos[0] <= 20+t.get_width() and win_size[1]/2+15 <= m_pos[1] <= win_size[1]/2+15+t.get_height():
            mode = "ip_input"
            ip = ""
            curc = -1
            consists = {}
        t = sfont.render("> Exit", True, (240,240,240))
        screen.blit(t, (20,win_size[1]/2+45))
        if m_btn[0] and 20 <= m_pos[0] <= 20+t.get_width() and win_size[1]/2+45 <= m_pos[1] <= win_size[1]/2+45+t.get_height():
            working = False

        screen.blit(subwmap, (win_size[0]-subwmap.get_width()-50, win_size[1]/2-subwmap.get_height()/2))

    elif mode == "ip_input":
        screen.fill((40,40,40))

        t = sfont.render("Enter server IP (your own is 127.0.0.1)", True, (240,240,240))
        screen.blit(t, (20,win_size[1]/2-15))
        t = sfont.render(f"> {ip} <", True, (240,240,240))
        screen.blit(t, (20,win_size[1]/2+15))
        
        ip+=unicode
        if pg.K_BACKSPACE in pressed and ip != "": ip=ip[:-1]
        if pg.K_RETURN in pressed: mode = "connect"

    elif mode == "connect":
        clientSocket = socket.socket()                  
        try:
            port = 29760
            clientSocket.connect((ip, int(port)))
            clientSocket.settimeout(5)
            clientSocket.send("Player".encode())
            received = ""
            all_right = True
            while True:
                # print("cycling")
                received += clientSocket.recv(16384).decode("utf-8")
                if not received:
                    all_right = False
                    break
                # print(received[-1])
                if received[-1] == "=":
                    received = received[:-1]
                    break
            # print("debug")
            # print(received)
            if all_right:
                own_uid = json.loads(received)[0]
                connected = True
                connection_thread = threading.Thread(target=socketThread, args=[clientSocket])
                connection_thread.start()
                mode = "playing_mp"

        except Exception as exc:
            print("[ERROR]", "An unexpected error occured while client was connecting")
            print("[EXCEPTION]", exc)
            print("fucked up")
            mode = "title"
        
    elif mode == "playing" or mode == "playing_mp":
        if pg.K_LEFTBRACKET in pressed and follow and curc != -1:
            consists[curc].route = list(route_map.keys())[(list(route_map.keys()).index(consists[curc].route)-1)%len(route_map)]
            if consists[curc].route in route_switches:consists[curc].routing_switches = route_switches[consists[curc].route]
            else: consists[curc].routing_switches = {}
        if pg.K_RIGHTBRACKET in pressed and follow and curc != -1:
            consists[curc].route = list(route_map.keys())[(list(route_map.keys()).index(consists[curc].route)+1)%len(route_map)]
            if consists[curc].route in route_switches:consists[curc].routing_switches = route_switches[consists[curc].route]
            else: consists[curc].routing_switches = {}
        if pg.K_z in pressed and follow and curc != -1: consists[curc].reversor_vector = [0,-1,1][consists[curc].reversor_vector]
        if pg.K_d in pressed: player.debug = not player.debug
        if pg.K_q in pressed and not follow: player.pos[2] -= tile_size
        if pg.K_e in pressed and not follow: player.pos[2] += tile_size
        if pg.K_p in pressed: follow = not follow
        if pg.K_s in pressed: spawn = not spawn
        if pg.K_o in pressed: screenshot_mode = not screenshot_mode
        if pg.K_ESCAPE in pressed:
            mode = "title"
        if pg.K_DELETE in pressed and curc != -1:
            consists[curc].is_alive = False
            consists.pop(curc)
            curc = -1

        occupied_tracks = []
        sp_info = {}

        if mode == "playing":
            temp_trains = []
            for c in consists:
                dl = 256*8
                for enum, tr in enumerate(consists[c].trains):
                    temp_trains.append(Dummy(tr, c, consists[c].velocity*3.6*1.8))
                    if c == curc and follow:
                        if consists[curc].reversor_vector == -1 and enum == 0: player.pos = temp_trains[-1].pos
                        if consists[curc].reversor_vector == 1 and enum+1 == len(consists[c].trains): player.pos = temp_trains[-1].pos

                    occupied_tracks.append(tr.occupied_tracks[0])
                    occupied_tracks.append(tr.occupied_tracks[1])            
        
        player.draw_map(temp_trains,screen, q)
        player_block = [int(i//tile_size) for i in player.pos]
        player_block = (player_block[0], player_block[1], player_block[2])

        kbd = pg.key.get_pressed()

        if follow and curc != -1:
            consists[curc].player_cycle(screen, pressed, kbd, (m_pos, m_btn, clicked, scroll), unicode)
            consists[curc].switch = kbd[pg.K_LALT] if consists[curc].route == None else 0

        fps = round(clock.get_fps())
        speed = 64 if kbd[pg.K_LSHIFT] else 16 if not kbd[pg.K_LALT] else 1

        if not follow:
            if kbd[pg.K_DOWN]: 
                player.pos[0] += speed
                player.pos[1] += speed
            elif kbd[pg.K_UP]: 
                player.pos[0] -= speed
                player.pos[1] -= speed
                
            if kbd[pg.K_RIGHT]: 
                player.pos[0] += speed
                player.pos[1] -= speed
            if kbd[pg.K_LEFT]: 
                player.pos[0] -= speed
                player.pos[1] += speed


        z = [version, f"pos: {player.pos}", f"fps: {fps}",]

        char = dfont.render("A",True, (0,0,0))

        if spawn:
            spawn_window.update(screen, mouse_state, pressed)
            if spawn_window.get_state("button_spawn") and spawn_window.get_state("list_station") != "" and spawn_window.get_state("list_train") != "" and curc == -1:
                trackid = spawnpoints[spawn_window.objects["list_station"]["items"].index(spawn_window.get_state("list_station"))][1]
                trainpar = train_spawn_info[spawn_window.objects["list_train"]["items"].index(spawn_window.get_state("list_train"))]
                tmp = train.spawn_train(
                    trainpar[0],
                    trackid if type(trackid) == int else random.choice(trackid), 
                    (trainpar[1],64), trainpar[-1])
                if tmp != None:
                    curc = random.randint(0, 9999) if mode != "playing_mp" else own_uid
                    consists[curc] = tmp
                    consists[curc].door_time = trainpar[2]
                    consists[curc].reversor_vector = 1
                    follow = True
            if spawn_window.get_state("button_spawn_arcade") and spawn_window.get_state("list_station") != "" and spawn_window.get_state("list_train") != "" and curc == -1:
                trackid = spawnpoints[spawn_window.objects["list_station"]["items"].index(spawn_window.get_state("list_station"))][1]
                trainpar = train_spawn_info[spawn_window.objects["list_train"]["items"].index(spawn_window.get_state("list_train"))]
                tmp = train.spawn_train(
                    trainpar[0],
                    trackid if type(trackid) == int else random.choice(trackid), 
                    (trainpar[1],64), trainpar[-1])
                if tmp != None:
                    curc = random.randint(0, 9999) if mode != "playing_mp" else own_uid
                    consists[curc] = tmp
                    consists[curc].door_time = trainpar[2]
                    consists[curc].reversor_vector = 1
                    consists[curc].internal.arcade = [False, False]
                    follow = True


        if curc != -1:
            bh = 20
            maxchar = 34
            dlt = int(char.get_width()*1)
            w = dlt*(maxchar)+char.get_height()
            h = char.get_height()*1.5
            bx = screen.get_width()-w-20
            pg.draw.rect(screen, (128,128,128), (bx-4, bh-4, w+8, h+8))
            pg.draw.rect(screen, (96,96,96), (bx, bh, w, h))
            name = route_map[consists[curc].route][0]+" "
            if player_block in st_tilemap:
                name += st_tilemap[player_block][0]
            
            for i in range(maxchar):
                pg.draw.rect(screen, (91,127,0), (bx+char.get_height()/2+dlt*(i), bh+char.get_height()*0.25, char.get_width(), char.get_height()))
                if i < len(name):
                    let = dfont.render(name[i].upper(), True, (182,255,0))
                    screen.blit(let, (bx+char.get_height()/2+dlt*(i+0.5)-let.get_width()/2, bh+char.get_height()*0.25))


        if not screenshot_mode:
            for enum, line in enumerate(z): 
                ptext = font.render(line,True,(240,240,240),(0,0,0))
                screen.blit(ptext,(20,20+30*enum))

            altstate = 'pressed' if kbd[pg.K_LALT] else 'released'
            if curc != -1 and consists[curc].route != None: altstate = "DISABLED"
            ptext = font.render(f"alt {altstate}",True,(240,240,240),(84,109,255) if altstate == 'pressed' else(0,0,0))
            screen.blit(ptext,(20,20+30*len(z)))

    pg.display.update()
    clock.tick(60)

pg.quit()
connected = False
for tr in consists:
    consists[tr].is_alive = False