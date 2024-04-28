import pygame
import math
from itertools import product
import json
from threading import Thread
import os
import time
import datetime
import src.world as world
from src.world import Voxel, Map, tile, TILE_TEXTURES
import src.actors as actors

WIDTHTILES = 28
HIGHTTILES = 28

SCREEN_WIDTH = tile * WIDTHTILES
SCREEN_HIGHT = tile * HIGHTTILES
pygame.font.init()

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

    def toggle_block(self, scene):
        blocks = [i.pos for i in scene.actors if i.NAME == "Block"]
        current_state = False
        if self.pos in blocks:
            current_state = True
        if self.mark2 in blocks:
            current_state = True
        elif self.mark2:
            current_state = False

        scene.actors = [i for i in scene.actors if not i.pos in self.selected_pos or not i.NAME == "Block"]
        if not current_state:
            scene.actors = scene.actors + [actors.Block(i) for i in self.selected_pos]
            
        

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
        if (not self.mark):
            return None
        if not self.mark2:
            mark2 = self.pos
        else:
            mark2 = self.mark2
        
        return pygame.Rect(tile*min(self.mark[0], mark2[0]), tile*min(self.mark[2], mark2[2]),
                           tile*abs(self.mark[0] - mark2[0])+tile, tile*abs(self.mark[2] - mark2[2]) + tile)
        

        

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
            if i.key == pygame.K_b:
                cursor.toggle_block(scene)
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
                


                
FONT = pygame.font.Font("Art/m3x6.ttf", 30)
        
        
def graphics(scene, cursor, window, framecount):
    window.fill((0,0,0))
    scene.update_surface(framecount)
    window.blit(scene.surface, (0,0))
    if cursor.selected_region_rect:
        sur = pygame.Surface(cursor.selected_region_rect.size)
        sur.fill((10,10,160))
        sur.set_alpha(100)
        window.blit(sur, cursor.selected_region_rect.topleft)
    window.blit(FONT.render(f"Level: {scene.current_layer}", False, (255,255,255)), (0,0))
    window.blit(CURSOR_TEXTURE, cursor.screen_pos)
    pygame.display.update()


def autosave(scene):
    while True:
        time.sleep(60*2)
        date = str(datetime.datetime.now())
        date = "-".join(date.split(":")[:-1])
        date = date.replace(" ", "-")
        with open("Levels/Autosaves/"+date, "x") as fil:
            fil.write(scene.to_json())
        
    
def console(scene):
    Thread(target = autosave, args = [scene]).start()
    while True:
        inp = input("> ")
        if (inp == "print"):
            print(scene.to_json())

        if (inp.startswith("load")):
            if len(inp.split(" ")) < 2:
                print("no specified file")
            else:
                filename = inp.split(" ")[1]
                if os.path.isfile("Levels/"+filename):
                    with open("Levels/"+filename, "r") as fil:
                        txt = fil.read()
                    scene.load(txt)
                else:
                    print("couldnt find file")
            
        if (inp.startswith("save")):            
            if len(inp.split(" ")) < 2:
                pass
            else:
                filename = inp.split(" ")[1]
                if os.path.isfile("Levels/" + filename):
                    if input("file already exist. Do you want to replace it (y, n) ") == "y":
                        with open("Levels/"+filename, "w") as fil:
                            fil.write(scene.to_json())
                else:
                    with open("Levels/"+filename, "x") as fil:
                        fil.write(scene.to_json())
            #with open(filename, "r") as fil:
        if (inp.startswith("list")):
            if len(inp.split(" ")) < 2:
                print(os.listdir("Levels"))
            else:
                dirname = "Levels/" + inp.split(" ")[1]
                if os.path.isdir(dirname):
                    print(os.listdir(dirname))
                
                

    
def main():
    cursor = Cursor()
    scene  = Map((SCREEN_WIDTH, SCREEN_HIGHT))

    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGHT), pygame.DOUBLEBUF, 32)
    
    framecount = 0

    Thread(target = console, daemon = True, args=[scene]).start()
    
    clock = pygame.time.Clock()
    running = True
    while running:
        framecount += 1
        clock.tick(30)
        graphics(scene, cursor, window, framecount)        
        
        events = pygame.event.get()

        input_handler(events, cursor, scene)

        for i in events:
            if i.type == pygame.QUIT:
                pygame.quit()
                running = False

if __name__ == "__main__":
    main()
