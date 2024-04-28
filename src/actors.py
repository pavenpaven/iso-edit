from src.voxel import Voxel, v3_add

class Actor:
    GRAVITY = True
    NAME = "default"
    
    def __init__(self, pos):
        self.pos = pos

    def to_dict(self):
        return {"pos": self.pos, "name": self.NAME}

    @classmethod
    def from_dict(cls, dic):
        return cls(tuple(dic["pos"]))

    def as_voxel(self):
        return None

    def pull(self, vec, scene):
        pass
    
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
        return Voxel(self.pos, voxel_id = 44)

    def pull(self, vec, scene):
        newpos = v3_add(vec, self.pos)
        if not scene.get_tile_by_pos(newpos):            
            on_head = list(filter(lambda x: x.pos == v3_add(self.pos, (0,1,0)), scene.actors))
            if on_head:
                on_head[0].pull(vec, scene)
            self.pos = newpos
        
    
    def on_push(self, direction, scene, gravity = False):
        pos = (direction[0] + self.pos[0],
               direction[1] + self.pos[1],
               direction[2] + self.pos[2])

        if scene.get_tile_by_pos(pos):
            return False
        
        for i in scene.actors:
            if i.pos == pos:
                a = i.on_push(direction, scene, gravity = gravity)
                if a:
                    if gravity == False:                        
                        on_head = list(filter(lambda x: x.pos == v3_add(self.pos, (0,1,0)), scene.actors))
                        print(on_head)
                        if on_head:                            
                            on_head[0].pull(direction, scene)
                        self.pos = pos
                    return True
                else:
                    return False
        if gravity == False:
            on_head = list(filter(lambda x: x.pos == v3_add(self.pos, (0,1,0)), scene.actors))
            print(on_head)
            if on_head:                            
                on_head[0].pull(direction, scene)
            self.pos = pos
        return True


ACTORS = [Block]

def from_dict(dic):
    return list(filter(lambda x:x.NAME == dic["name"], ACTORS))[0].from_dict(dic)
    
