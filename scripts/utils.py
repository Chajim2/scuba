import pygame
import json, os, time
#from entities import Drop
from .entities import Drop

base_img_path = "data/pictures/"
DEF_OFFSETS = [(1,1),(1,0),(0,1),(0,0),(-1,-1),(-1,1),(1,-1),(-1,0),(0,-1)]
APPLY_PHYSICS = {'grass','dirt','coal','iron','gold','diamond'}
WATER_OFFESTS = [(0,-1),(-1,0),(1,0)]
MINIBLOCK_SIZE = [10,10]
DESTROY_TIMES = {'grass': 60, 'dirt' : 90, 'tree': 40, 'coal' : 120,'iron': 160, 'gold' : 220, 'diamond' : 280}
ALERT_LIST = {}


class Healthbar():
    def __init__(self,game, pos) -> None:
        self.img = game.assets['air']
        self.ratio = 1
        self.pos = pos
        self.max_bubbles = 10
        self.game = game
        self.wait = 0
        self.spawn_point = (0,0)

    def update(self,breath):
        self.ratio = int((breath / 500) * self.max_bubbles)
    
    def render(self):
        if not self.game.player.in_water():
            if self.wait: self.wait -= 1
            else: return
        else: self.wait = 120
        for bubble in range(self.ratio):
            self.game.screen.blit(self.img,(self.pos[0] + bubble * 50, self.pos[1]))

class Tilemap():
    def __init__(self,game) -> None:
        self.game = game
        self.data = {}
        self.tile_size = 50
        self.offgrid_tiles = []
        self.destroyable_tiles = {'grass','dirt', 'tree','coal','iron'}
        self.enemies = []

    def tiles_around(self, pos):
        loc = [int(pos[0]//self.tile_size), int(pos[1]//self.tile_size)]
        out = []
        for offset in DEF_OFFSETS:
            curr = str(str(loc[0] + offset[0]) + ',' + str( loc[1] + offset[1]))
            if str(curr) in self.data: 
                out.append(self.data[str(curr)]) 
        return out

    def update_destroyable(self):
        if 'laser' in self.game.inv.equiped: self.destroyable_tiles = {'grass','dirt', 'tree','coal','iron','gold','diamond'}
        else: self.destroyable_tiles = {'grass','dirt', 'tree','coal','iron'}

    def destroy_block(self,mpos):
        mpos = [mpos[0] // self.tile_size, mpos[1] // self.tile_size]
        tile = f"{int(mpos[0])},{int(mpos[1])}"
        if tile in self.data:
                if self.data[tile]['type'] in self.destroyable_tiles:
                    self.data[tile]['destroy_counter'] += 1
                    self.destroying = tile

    def physisc_tiles_around(self,pos):
        all = self.tiles_around(pos)
        out = []
        for tile in all:
            if tile['type'] in APPLY_PHYSICS: out.append(pygame.Rect(tile['pos'][0],tile['pos'][1],self.tile_size,self.tile_size))
        return out
    
    def check_water(self,pos):
        for offset in WATER_OFFESTS:
            loc = f"{offset[0] + pos[0]},{offset[1] + pos[1]}"
            if loc in self.data:
                if self.data[loc]['type'] == 'water': self.data[f"{pos[0]},{pos[1]}"] = {'type':'water','pos': [pos[0] * self.tile_size, pos[1] * self.tile_size],
                                                                                         "destroy_counter": 0, "variant": 0}
    def drop(self,type, pos):
        self.game.drop_list.append(Drop(self.game, 'drop', pos, self.game.mini_block_size,type))

    def destroy_tree(self, pos):
        count = 1
        while f"{pos[0]},{pos[1] - count}" in self.data:
            self.drop('tree', (pos[0] * self.tile_size, (pos[1] - count) * self.tile_size))
            del self.data[f"{pos[0]},{pos[1] - count}"]
            count += 1

    def apply_physics(self,pos):
        bellow = f"{int(pos[0]//self.tile_size)},{int(pos[1]//self.tile_size + 1)}" 
        count = 1
        change = False
        while bellow not in self.data and count < 10: 
            #print(f"whole string is{bellow} count is {count}")
            count += 1
            bellow = bellow[:-1] + str(pos[0] + count)
            change = True

        if not change: return False
        elif count >= 10: 
            print('count was high')
            return True
        else: self.pos = [pos[0], bellow[-1] * self.tile_size]

        self.game.screen.blit()
        
    def render(self, offset = [0,0]):
        for y in range(offset[1] // self.tile_size,(self.game.screen.get_height() + offset[1]) // self.tile_size + 1):
            for x in range(offset[0] // self.tile_size,(self.game.screen.get_width() + offset[0])// self.tile_size + 1):
                if f'{x},{y}' in self.data:
                    if self.data[f'{x},{y}']['destroy_counter'] > 0:
                        if self.destroying == f'{x},{y}':
                            if self.data[f'{x},{y}']['destroy_counter'] > DESTROY_TIMES[self.data[f"{x},{y}"]['type']]: 
                                if self.data[f"{x},{y}"]['type'] != 'water': self.drop(self.data[f"{x},{y}"]['type'],self.data[f"{x},{y}"]['pos'])
                                if self.data[f"{x},{y}"]['type'] == 'tree': self.destroy_tree((x,y))
                                self.check_water([x,y])
                                del self.data[f'{x},{y}']
                                continue
                            else: self.data[f'{x},{y}']['destroy_counter'] += 1
                        else: self.data[f'{x},{y}']['destroy_counter'] = 0
                    
                    self.game.screen.blit(self.game.assets[self.data[f'{x},{y}']['type']][self.data[f"{x},{y}"]['variant']], (self.data[f'{x},{y}']['pos'][0] - offset[0],
                                               self.data[f'{x},{y}']['pos'][1] - offset[1]))

        for tile in self.offgrid_tiles:
            self.game.screen.blit(self.game.assets[tile['type']][tile['variant']],(tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

    def save(self,path):
        with open(path,'w') as f:
            json.dump({'spawn' : self.spawn_point,'data':self.data,'tile_size' : self.tile_size, 'offgrid_tiles': self.offgrid_tiles, 'enemies' : self.enemies}, f)


    def load(self,path):
        with open(path, 'r') as f:
            map_data = json.load(f)
        self.data = map_data['data']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid_tiles']
        self.enemies = map_data['enemies']
        self.spawn_point = map_data['spawn']

class Alerts():
    def __init__(self,game) -> None:
        pygame.font.init()
        self.font = pygame.font.Font("data/font/retron2000/Retron2000.ttf",40)
        self.game = game
        self.timer = 50
        self.data = {}
    

    def is_empty(self):
        return len(self.data) == 0
    
    def update(self):
        for alert in self.data.copy():
            if self.data[alert]['count'] < 0: 
                time.sleep(self.data[alert]['sleep'])
                del self.data[alert]
            else: self.data[alert]['count'] -= 1

    def add(self,pos,text,time, sleep = 0):
        if self.data is None: self.data = {}
        self.data[text] = {'pos' : pos, 'count' : time, 'sleep' : sleep}

    def render(self):
        self.update()
        for alert in self.data:
            self.game.screen.blit(self.font.render(alert,False, (0,0,0)), self.data[alert]['pos'])

class Cursor:
    def __init__(self,game) -> None:
        self.img = pygame.transform.scale(load_img('cursor/cursor.png'),(30,30))
        self.screen = game.real_screen

    def render(self):
        self.screen.blit(self.img, self.rect().topleft)
    
    def rect(self):
        return pygame.Rect((pygame.mouse.get_pos()[0] - 25, pygame.mouse.get_pos()[1] - 25), self.img.get_size())

def load_img(path, scale =[50,50]):
    img = pygame.image.load(base_img_path + path).convert()
    img.set_colorkey((0,0,0))
    return img

def load_imgs(path, increment = [0,0]):
    out = []
    for file_name in sorted(os.listdir(base_img_path + path)):
        out.append(pygame.transform.scale(pygame.image.load(base_img_path  + path + '/' + file_name), (50 + increment[0],50 + increment[1])))
    
    for img in out:
        img.set_colorkey((0,0,0))
    return out

def to_str(dict):
    out = {}
    for char in dict:
        out[f"{char[0]},{char[1]}"] = dict[char]
    return out

def to_dict(dict):
    out = {}
    for char in dict:
        out[(int(char[:char.find(',')]),int(char[char.find(',') + 1:]))] = dict[char]
    return out

def dict_to_str(dict) -> str:
    out = ""
    for x in range(3):
        for y in range(3):
            if (x,y) in dict: out = out + f"{x},{y}" + ':' + str(dict[(x,y)]['type']) + ';'
    
    return out

def str_to_dict(str) -> dict:
    temp = str.split(',')
    out = {}
    for char in temp:
        out[char.split(':')[0]] = char.split(':')[1]
    return out

