import pygame
from math import cos, sin, pi
import json
import src.animation as animation


tile = 30



TILE_FILENAMES = [
    "Art/pixil-frame-0.png",
    "Art/iso_birchbirch.png",            
    "Art/iso_cobblecobble.png",          
    "Art/iso_cobblecobbleslabslab.png",  
    "Art/iso_dirtdirt.png",              
    "Art/iso_flowerflower1.png",         
    "Art/iso_flowerflower2.png",         
    "Art/iso_flowerflower3.png",         
    "Art/iso_flowerflower4.png",         
    "Art/iso_flowerflower5.png",         
    "Art/iso_flowerflower6.png",         
    "Art/iso_goldgold.png",              
    "Art/iso_grassgrassemptyempty.png",  
    "Art/iso_grassgrass.png",            
    "Art/iso_grassgrassredred.png",      
    "Art/iso_grassgrasssnowsnow.png",    
    "Art/iso_grassgrassyellowyellow.png",
    "Art/iso_hayhay.png",                
    "Art/iso_lavalava.png",              
    "Art/iso_leafleafoldold.png",        
    "Art/iso_leafleaforangeorange.png",  
    "Art/iso_leafleafpinkpink.png",      
    "Art/iso_leafleaf.png",                  
    "Art/iso_leafleafroserose.png",      
    "Art/iso_leafleafwhitewhite.png",    
    "Art/iso_leafleafyellowyellow.png",  
    "Art/iso_mossmoss.png",              
    "Art/iso_redstoneredstonemossmoss.png",
    "Art/iso_redstoneredstone.png",
    "Art/iso_redstoneredstoneslabslab.png",      
    "Art/iso_sandsand.png",              
    "Art/iso_shadowsshadow.png",         
    "Art/iso_snowsnow.png",              
    "Art/iso_stonestone_emptyempty.png", 
    "Art/iso_stonestone.png",            
    "Art/iso_waterwater",
    "Art/iso_waterwaterfullfull",            
    "Art/iso_woodwoodplanksplanks.png",  
    "Art/iso_woodwood.png",
    "Art/iso_grassgrassslabslab.png",
    "Art/iso_grassgrassyellowyellowslabslab.png",
    "Art/iso_woodwoodslabslab.png"]

def v3_add(v, w):
    return (v[0] + w[0], v[1] + w[1], v[2] + w[2])


TILE_TEXTURES = [animation.Animation.from_file(i, (tile,tile), 4) if len(i.split(".")) > 1
                 else animation.Animation.from_dir(i, (tile, tile), 4)
                     for i in TILE_FILENAMES]

iso_tile_scale = 2

iso_tile = iso_tile_scale*tile


ISO_TEXTURES = [animation.Animation.from_file(i, (iso_tile,iso_tile), 4) if len(i.split(".")) > 1
                 else animation.Animation.from_dir(i, (iso_tile, iso_tile), 4)
                     for i in TILE_FILENAMES]


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

class Voxel:
    is_player = False #magic nothing wrong here
    def __init__(self, pos, voxel_id):
        self.pos      = pos
        self.voxel_id = voxel_id

    def as_dict(self):
        return {"pos": self.pos, "voxel_id": self.voxel_id}
        
    @property
    def texture(self):
        return TILE_TEXTURES[self.voxel_id - 1].texture

    @property
    def iso_texture(self):
        return ISO_TEXTURES[self.voxel_id - 1].texture

    
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
                           "actors": []})

    def load(self, txt):
        self.tile_map = [Voxel(tuple(i["pos"]), i["voxel_id"]) for i in json.loads(txt)]
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
            for i in self.tile_map:
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
    
