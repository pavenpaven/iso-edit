import pygame
from math import cos, sin, pi
import src.world as world
from src.world import tile, iso_tile, v3_add
import src.actors as actors
from src.actors import Block

WIDTHTILES = 28
HIGHTTILES = 28

SCREEN_WIDTH = tile * WIDTHTILES
SCREEN_HIGHT = tile * HIGHTTILES

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGHT), pygame.DOUBLEBUF, 32)


PLAYER_TEXTURE = pygame.image.load("Art/iso_hayhay.png")
PLAYER_TEXTURE = pygame.transform.scale(PLAYER_TEXTURE, (iso_tile, iso_tile))

class Player(actors.Actor):
    def __init__(self, pos):
        self.pos = pos
        self.carry = False
    
    def as_voxel(self):
        if self.carry:
            vox = world.Voxel(self.pos, voxel_id = 45)
        else:
            vox = world.Voxel(self.pos, voxel_id = 1)
        vox.is_player = True
        return vox

    def on_push(self, direction, scene, gravity = False):
        return not gravity

    def pull(self, vec, scene):
        pass
    
    def walk(self, vec, scene):
        old_pos = self.pos
        v = v3_add(self.pos, vec)
        on_head = list(filter(lambda x: x.pos == v3_add(self.pos, (0,1,0)), scene.actors))
        if not scene.get_tile_by_pos(v):            
            self.pos = v
        elif not scene.get_tile_by_pos(v3_add((0,1,0), v)):
            self.pos = v3_add((0,1,0), v)
            vec = v3_add((0,1,0), vec)
        for i in scene.actors:
            if i.pos == self.pos:
                if not i.on_push(vec, scene):
                    self.pos = old_pos
        
        if on_head and self.pos != old_pos:
                on_head[0].pull(vec, scene)
        self.carry = bool(list(filter(lambda x: x.pos == v3_add(self.pos, (0,1,0)), scene.actors)))
        scene.update_actors()
                
       
#    # def render(self, surface):
     #    rot_pos =(self.pos[0]*cos(pi/4) -self.pos[2]*sin(pi/4),
     #              self.pos[1],
     #              self.pos[2]*cos(pi/4) +self.pos[0]*sin(pi/4))
     #    surface.blit(PLAYER_TEXTURE,
     #                 ((2*iso_tile/3.2)*rot_pos[0] + (SCREEN_WIDTH/2),
     #                  (iso_tile/3.5)*rot_pos[2]+50 - rot_pos[1]*(2*iso_tile/3.67)))
        

                                        

def graphics(scene, player, framecount):
    window.fill((0,0,0))
    scene.update_surface(framecount)
    window.blit(scene.surface, (0,0))
    pygame.display.update()

def input_handler(events, player, scene):
    for i in events:
        if i.type == pygame.KEYDOWN:
            if i.key == pygame.K_s:
                player.walk((1, 0, 0), scene)
            if i.key == pygame.K_w:
                player.walk((-1, 0, 0), scene)
            if i.key == pygame.K_a:
                player.walk((0, 0, 1), scene)
            if i.key == pygame.K_d:
                player.walk((0, 0, -1), scene)
            if i.key == pygame.K_UP:
                player.walk((0, 1, 0), scene)
            if i.key == pygame.K_DOWN:
                player.walk((0, -1, 0), scene)
            


def main():
    scene  = world.Map((SCREEN_WIDTH, SCREEN_HIGHT))

    with open("Levels/pusseltest", "r") as fil:
        txt = fil.read()
    
    scene.load(txt)
    scene.iso_mode = True
    

    jack = Player((5,1,5))

    scene.actors.append(jack)
    
    framecount = 0

        
    clock = pygame.time.Clock()
    running = True
    while running:
        framecount += 1
        clock.tick(30)
        graphics(scene, jack, framecount)        
        
        events = pygame.event.get()

        input_handler(events, jack, scene)

        for i in events:
            if i.type == pygame.QUIT:
                pygame.quit()
                running = False

if __name__ == "__main__":
    main()

