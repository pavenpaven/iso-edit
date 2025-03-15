import pygame
from math import cos, sin, pi
import json
import src.animation as animation
from src.voxel import Voxel, v3_add, tile, TILE_TEXTURES, ISO_TEXTURES, iso_tile_scale, iso_tile
import src.actors as actors

print("**********************************")
print("The tile art is entirely made by Dani Maccari. Link to their itch io: https://dani-maccari.itch.io/")
print("**********************************")


def bounded(x): # maybe you can make something cheaper
    return ( 1/(1-x) if x < 0 else -1/(1+x) + 2)/2

def convert_to_diagonal_order(l):
    return sorted(l, key = lambda x: x.pos[1] + bounded(x.pos[0] + x.pos[2])) # math magic basicly sigmoid between 0 and 1

#def convert_to_diagonal_order(l):
#    return sorted(l, key = lambda x: x.pos[1] + sigmoid(max(x.pos[0], x.pos[2]))) # math magic basicly sigmoid between 0 and 1

def apply_rotation(l):
    return [Voxel((x.pos[0]*cos(pi/4) - x.pos[2]*sin(pi/4),
                  x.pos[1],
                  x.pos[2]*cos(pi/4) + x.pos[0]*sin(pi/4)),
                  x.voxel_id) for x in l]
    
class Map:
    BKG_COLOR = (40,10,10)
    def __init__(self, size):
        self.surface = pygame.Surface(size)
        self.tile_map = []
        self.actors   = []
        self.current_layer = 0
        self.iso_mode = False
        self.camera = (0,0)
        self.size = size


    def to_json(self):
        return json.dumps({"tile_map": [i.as_dict() for i in self.tile_map],
                           "actors": [i.to_dict() for i in self.actors]})

    def load(self, txt):
        self.tile_map = [Voxel(tuple(i["pos"]), i["voxel_id"]) for i in json.loads(txt)["tile_map"]]
        self.actors = [actors.from_dict(i) for i in json.loads(txt)["actors"]]
        print([i.pos for i in self.tile_map])
    

    def update_actors(self):
        for i in self.actors:
            i.step(self)
        
    def update_surface(self, framecount):
        for i in TILE_TEXTURES:
            i.update(framecount)
        for i in ISO_TEXTURES:
            i.update(framecount)
        if not self.iso_mode:
            self.surface.fill(self.BKG_COLOR)
            for i in self.tile_map + [i.as_voxel() for i in self.actors if i.as_voxel()]:
                if i.pos[1] == self.current_layer:
                    self.surface.blit(i.texture, (i.pos[0] * tile, i.pos[2] * tile))
        else:
            self.surface.fill(self.BKG_COLOR)
            diagonal = apply_rotation(convert_to_diagonal_order(self.tile_map + [i.as_voxel() for i in self.actors if i.as_voxel()]))
            for i in diagonal:
                self.surface.blit(i.iso_texture,
                                  ((2*iso_tile/3.2)*i.pos[0]+(self.size[0]/2),
                                   (iso_tile/3.5)*i.pos[2]+50 - i.pos[1]*(2*iso_tile/3.67)))            
                

    def get_tile_by_pos(self, pos):
        possible_tiles = list(filter(lambda x: x.pos == pos, self.tile_map))
        if possible_tiles:
            return possible_tiles[0]
        return None

    def change_tile_by_pos(self, pos, voxel_id):
        other_tiles = list(filter(lambda x: x.pos != pos, self.tile_map))
        if voxel_id: # voxel_id 0 means no voxel
            self.tile_map = other_tiles + [Voxel(pos, voxel_id)]
        else:
            self.tile_map = other_tiles
    
