import pygame
import math
from math import cos, sin, pi
from itertools import product


tile = 30
WIDTHTILES = 28
HIGHTTILES = 28

SCREEN_WIDTH = tile * WIDTHTILES
SCREEN_HIGHT = tile * HIGHTTILES

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGHT), pygame.DOUBLEBUF, 32)


TILE_FILENAMES = [
    "Art/iso_birchbirchplanksplanks.png",
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
    "Art/iso_waterwater.png",
    "Art/iso_waterwater_fullfull.png",            
    "Art/iso_woodwoodplanksplanks.png",  
    "Art/iso_woodwood.png"]



TILE_TEXTURES = [pygame.transform.scale(pygame.image.load(i), (tile, tile))
                     for i in TILE_FILENAMES]

iso_tile_scale = 2

iso_tile = iso_tile_scale*tile

ISO_TEXTURES =  [pygame.transform.scale(pygame.image.load(i), (tile*iso_tile_scale, tile*iso_tile_scale))
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
    def __init__(self, pos, voxel_id):
        self.pos      = pos
        self.voxel_id = voxel_id

    @property
    def texture(self):
        return TILE_TEXTURES[self.voxel_id - 1]

    @property
    def iso_texture(self):
        return ISO_TEXTURES[self.voxel_id - 1]

class Map:
    def __init__(self):
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HIGHT))
        self.tile_map = []
        self.current_layer = 0
        self.iso_mode = False

    def update_surface(self):
        if not self.iso_mode:
            self.surface.fill((0,0,0))
            for i in self.tile_map:
                if i.pos[1] == self.current_layer:
                    self.surface.blit(i.texture, (i.pos[0] * tile, i.pos[2] * tile))
        else:
            self.surface.fill((0,0,0))
            diagonal = apply_rotation(convert_to_diagonal_order(self.tile_map))
            for i in diagonal:
                self.surface.blit(i.iso_texture,
                                  ((2*iso_tile/3.2)*i.pos[0]+(SCREEN_WIDTH/2),
                                   (iso_tile/3.5)*i.pos[2]+50 - i.pos[1]*(2*iso_tile/3.57)))            
                

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
    

CURSOR_TEXTURE = pygame.image.load("Art/curser.png")
CURSOR_TEXTURE = pygame.transform.scale(CURSOR_TEXTURE, (tile, tile))

class Cursor:
    def __init__(self):
        self.pos = (2,0,2)
        self.selected = 0
        self.mark = None
        self.mark2 = None
        self.copied_region =  []

        
    def change_voxel(self, scene, step = 1):
        if self.mark2:
            current_voxel = scene.get_tile_by_pos(self.mark2)
        else:
            current_voxel = scene.get_tile_by_pos(self.pos)


        for i in self.selected_pos:
            if current_voxel:
                scene.change_tile_by_pos(i, (current_voxel.voxel_id + step) % (len(TILE_TEXTURES) + 1))
            else:
                scene.change_tile_by_pos(i, step % (len(TILE_TEXTURES) + 1))
        

    @property
    def screen_pos(self):
        return (self.pos[0]*tile, self.pos[2]*tile)

    @property
    def selected_pos(self):
        if (not self.mark2):
            return [self.pos]

        return list(product(range(min(self.mark[0], self.mark2[0]),
                                  min(self.mark[0], self.mark2[0]) +
                                  abs(self.mark[0] - self.mark2[0]) + 1),
                            range(min(self.mark[1], self.mark2[1]),
                                  min(self.mark[1], self.mark2[1]) +
                                  abs(self.mark[1] - self.mark2[1]) + 1),
                            range(min(self.mark[2], self.mark2[2]),
                                  min(self.mark[2], self.mark2[2]) +
                                  abs(self.mark[2] - self.mark2[2]) + 1)))
        
    
    @property
    def selected_region_rect(self):
        if (not self.mark) or (not self.mark2):
            return None
        
        return pygame.Rect(tile*min(self.mark[0], self.mark2[0]), tile*min(self.mark[2], self.mark2[2]),
                           tile*abs(self.mark[0] - self.mark2[0])+tile, tile*abs(self.mark[2] - self.mark2[2]) + tile)
        

        

def input_handler(events, cursor, scene):
    mouse_pos = pygame.mouse.get_pos()
    cursor.pos = (math.floor(mouse_pos[0] / tile), cursor.pos[1], math.floor( mouse_pos[1] / tile ))
    if pygame.mouse.get_pressed()[0]:
        for i in cursor.selected_pos:
            scene.change_tile_by_pos(i, cursor.selected)
        
    for i in events:
        if i.type == pygame.KEYDOWN:
            if i.key == pygame.K_x:
                cursor.change_voxel(scene)
            if i.key == pygame.K_UP:
                cursor.pos = (cursor.pos[0], cursor.pos[1] + 1, cursor.pos[2])
                scene.current_layer += 1
            if i.key == pygame.K_DOWN:
                cursor.pos = (cursor.pos[0], cursor.pos[1] - 1, cursor.pos[2])
                scene.current_layer -= 1
            if i.key == pygame.K_i:
                scene.iso_mode = not scene.iso_mode
            if i.key == pygame.K_m:
                if cursor.mark:
                    if cursor.mark2:
                        cursor.mark  = None
                        cursor.mark2 = None
                    else:
                        cursor.mark2 = cursor.pos
                else:
                    cursor.mark = cursor.pos
            if i.key == pygame.K_c:
                if cursor.mark2:
                    cursor.copied_region = [Voxel((i[0] - cursor.mark[0], i[1] - cursor.mark[1], i[2] - cursor.mark[2]), scene.get_tile_by_pos(i).voxel_id)
                                            for i in cursor.selected_pos if scene.get_tile_by_pos(i)]                    
            if i.key == pygame.K_v:
                for j in cursor.copied_region:
                    scene.change_tile_by_pos((j.pos[0] + cursor.pos[0], j.pos[1] + cursor.pos[1], j.pos[2] + cursor.pos[2]), j.voxel_id)
        if i.type == pygame.MOUSEBUTTONDOWN:
            if i.button == 3: # right click
                selected_voxel = scene.get_tile_by_pos(cursor.pos)
                if selected_voxel:
                    cursor.selected = selected_voxel.voxel_id
                else:
                    cursor.selected = 0
            #if i.button == 1: # left click
            #    scene.change_tile_by_pos(cursor.pos, cursor.selected)
            if i.button == 4: # up scroll
                cursor.change_voxel(scene)
            if i.button == 5: # down scroll
                cursor.change_voxel(scene, step = -1)
                
                
        
        
def graphics(scene, cursor):
    window.fill((0,0,0))
    scene.update_surface()
    window.blit(scene.surface, (0,0))
    if cursor.selected_region_rect:
        sur = pygame.Surface(cursor.selected_region_rect.size)
        sur.fill((10,10,160))
        sur.set_alpha(100)
        window.blit(sur, cursor.selected_region_rect.topleft)
    window.blit(CURSOR_TEXTURE, cursor.screen_pos)
    pygame.display.update()

def main():
    cursor = Cursor()
    scene  = Map()
    
    framecount = 0
    
    clock = pygame.time.Clock()
    running = True
    while running:
        framecount += 1
        clock.tick(30)
        graphics(scene, cursor)        
        
        events = pygame.event.get()

        input_handler(events, cursor, scene)

        for i in events:
            if i.type == pygame.QUIT:
                pygame.quit()
                running = False

if __name__ == "__main__":
    main()
