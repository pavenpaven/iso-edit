import srd.world as world
from world import Voxel, v3_add

class Actor:
    GRAVITY = True
    
    def __init__(self, pos):
        self.pos = pos

    def as_voxel(self):
        return None

    def on_push(self, direction):
        pass

    def step(self, scene):
        if self.GRAVITY:
            newpos = v3_add(self.pos, (0,-1,0))
            if not scene.get_tile_by_pos(newpos):
                self.pos = newpos
                
        
class Block(Actor):
    def as_voxel(self):
        return Voxel(self.pos, voxel_id = 3)

    def on_push(self, direction):
        self.pos = (direction[0] + self.pos[0],
                    direction[1] + self.pos[1],
                    direction[2] + self.pos[2])
        
