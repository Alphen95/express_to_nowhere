import os
import json
import pygame as pg

print("Package prerendering utility")
packs = os.listdir("packages/")
print("Select a package to prerender:")
print("0: Exit")
for i, p in enumerate(packs):
    print(f"{i+1}: {p}")

selection = input("> ")
if selection == "0":
    pass
else:
    if selection.isdigit() and 0 < int(selection) <= len(packs):
        folder = packs[int(selection)-1]
        print(f"Selected {folder}.")
        if os.path.isdir(f"packages/{folder}"):
            pack_contents = os.listdir(f"packages/{folder}")
            if "pack.json" in pack_contents:
                with open("packages/"+folder+"/pack.json") as f: pack_info = json.loads(f.read())
                print("Pack found. Contents:")
                print(f"{len(pack_info['trains'])} traincars.")

                if "prerender_train" not in pack_contents: os.mkdir("packages/"+folder+"/prerender_train")
                if "prerender_train2x" not in pack_contents: os.mkdir("packages/"+folder+"/prerender_train2x")
                if "prerender_tile" not in pack_contents: os.mkdir("packages/"+folder+"/prerender_tile")
                
                pg.init()
                
                for train in pack_info["trains"]:
                    print("Prerendering",train["id"])
                    base_img = pg.image.load("packages/"+folder+"/"+train["spritesheet"])
                    for state_name in train["sprite_maps"]:
                        state = train["sprite_maps"][state_name]
                        state_img = base_img.subsurface(state[0],state[1],state[2][0]*state[3],state[2][1])
                        temp_layers = []


                        scale = state[4]

                        for i in range(state[3]):
                            temp_layers.append(pg.transform.scale(state_img.subsurface(i*state[2][0],0,state[2][0],state[2][1]),[i*state[4] for i in state[2]]))

                        for ang in range(0,360,1):
                            angle = (ang+45)%360

                            layer = pg.transform.rotate(temp_layers[0],angle)
                            height = len(temp_layers)*scale
                            surf = pg.Surface((layer.get_width(), layer.get_height()/2+height), pg.SRCALPHA)
                            ii = 0

                            for layer in temp_layers:
                                layer = pg.transform.rotate(layer,angle)
                                layer = pg.transform.scale(layer, (layer.get_width(), layer.get_height()/2))

                                for i in range(scale):
                                    surf.blit(layer, (0,height-ii))
                                    ii+=1
                            
                            pg.transform.scale(surf, (surf.get_width()*2, surf.get_height()*2))
                            surf.set_colorkey((0,0,0))
                            pg.image.save(surf, f"packages/{folder}/prerender_train/{train['id']}_{state_name}_{angle}.png")
                            

                        scale = state[4]*2
                        temp_layers = []


                        for i in range(state[3]):
                            temp_layers.append(pg.transform.scale(state_img.subsurface(i*state[2][0],0,state[2][0],state[2][1]),[i*scale for i in state[2]]))

                        for ang in range(0,360,1):
                            angle = (ang+45)%360

                            layer = pg.transform.rotate(temp_layers[0],angle)
                            height = len(temp_layers)*scale
                            surf = pg.Surface((layer.get_width(), layer.get_height()/2+height), pg.SRCALPHA)
                            ii = 0

                            for layer in temp_layers:
                                layer = pg.transform.rotate(layer,angle)
                                layer = pg.transform.scale(layer, (layer.get_width(), layer.get_height()/2))

                                for i in range(scale):
                                    surf.blit(layer, (0,height-ii))
                                    ii+=1
                            
                            surf.set_colorkey((0,0,0))
                            pg.image.save(surf, f"packages/{folder}/prerender_train2x/{train['id']}_{state_name}_{ang}.png")

                pg.quit()
            else:
                print("Pack is empty!")
        else:
            print("Selection is not a folder!")
    else:
        print("Invalid selection!")
