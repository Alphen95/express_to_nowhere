import json

with open("world.json") as f:
    q = json.loads(f.read())
    rail_nodes, blockmap, underay_map, stations = q

new_rn, new_bm, new_um, new_st = {}, {}, {}, []

def cond(coords):
    if -160 >= int(coords[0]) >= -160-224 and 16 >= int(coords[1]) >= 16-129:
        return True
    else: return False

for node in rail_nodes:
    coords = node.split(":")
    if not cond(coords):
        new_rn[node] = rail_nodes[node]

for node in blockmap:
    coords = node.split(":")
    if not cond(coords):
        new_bm[node] = blockmap[node]

for node in underay_map:
    coords = node.split(":")
    if not cond(coords):
        new_um[node] = underay_map[node]

new_st = stations

with open("world.json", mode="w", encoding="utf-8") as f:
    f.write(json.dumps([new_rn, new_bm, new_um, new_st], indent=2))