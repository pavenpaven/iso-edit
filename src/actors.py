from src.voxel import Voxel, v3_add

class Actor:
    GRAVITY = True
    NAME = "default"
    
    def __init__(self, pos):
        self.pos = pos

    def to_dict(self):
        return {"pos": self.pos, "name": self.NAME}

    def as_voxel(self):
        return None

    def on_push(self, direction, scene, gravity = False):
        pass

    def step(self, scene):
        if self.GRAVITY:
            newpos = v3_add(self.pos, (0,-1,0))
            if not scene.get_tile_by_pos(newpos):
                for i in scene.actors:
                    if newpos == i.pos:
                        if not i.on_push((0,-1,0), scene, gravity = True):
                            return None
                self.pos = newpos
                                
        
class Block(Actor):
    NAME = "Block"
    
    def as_voxel(self):
        return Voxel(self.pos, voxel_id = 3)

    def on_push(self, direction, scene, gravity = False):
        pos = (direction[0] + self.pos[0],
               direction[1] + self.pos[1],
               direction[2] + self.pos[2])

        if scene.get_tile_by_pos(pos):
            return False
        
        for i in scene.actors:
            if i.pos == pos:
                a = i.on_push(direction, scene)
                if a:
                    if gravity == False:
                        self.pos = pos
                    return True
                else:
                    return False
        if gravity == False:
            self.pos = pos
        return True


actors = [Block]

def from_dict(dic):
    return list(filter(lambda x:x == dic["name"]. actors))(dic["pos"])
    
