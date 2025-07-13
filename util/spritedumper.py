import isometry
import pygame as pg

pg.init()


tile_sheet = pg.image.load("res/tiles.png")
player = isometry.Camera((100,100))
player.sprites["millimetrovka"] = player.render_tile(tile_sheet.subsurface(0,0,64,64),(1,0,2))

pg.image.save(player.sprites["millimetrovka"][0], "tile.png")
pg.quit()

