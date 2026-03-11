import pygame, sys, random
from utils import Tilemap, load_imgs, load_img


RENDER_SCALE = 1
class Editor(): 
    def __init__(self):
        pygame.init()
        self.real_screen = pygame.display.set_mode((1600,900))
        self.screen = pygame.Surface((1600,900))
        self.clock = pygame.time.Clock()
        self.scroll = [0,0]
        self.flood = None

        #settings   
        self.background_color = (100,100,100)
        self.camera_speed = 12

        self.should_move = {"right": False,"left": False, "up": False,"down": False,}
        self.tilemap = Tilemap(self)
        try:
            self.tilemap.load('map.json')
        except:
            print('file not found')

        self.assets = {
            'grass' : load_imgs("grass"),
            'dirt' : load_imgs('dirt'),
            'water': load_imgs('water'),
            'tree' : load_imgs('tree'),
            'coal' : load_imgs('ores/coal'),
            'iron' : load_imgs('ores/iron'),
            'gold' : load_imgs('ores/gold'),
            'diamond' : load_imgs('ores/diamond'),
            'enemy': load_imgs('enemy'),
            'rocket' : load_imgs('rocket', [100,200])
                    }
        self.asset_list = list(self.assets)
        self.curr_tile = 0
        self.left_click = False
        self.right_click = False
        self.shift = False
        self.curr_ver = 0
        self.mid_click = False
        self.floodfill = [0,0]

    def run(self):   
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                try:
                    self.picked = self.assets[self.asset_list[self.curr_tile]][self.curr_ver]
                except:
                    self.picked = self.assets[self.asset_list[self.curr_tile]][0]

                mpos = pygame.mouse.get_pos()
                mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
                tile_mpos = [int((mpos[0] + self.scroll[0])/(self.tilemap.tile_size)), int((mpos[1] + self.scroll[1])/(self.tilemap.tile_size))]

                if self.left_click:
                    self.tilemap.data[f"{tile_mpos[0]},{tile_mpos[1]}"] = {'type': self.asset_list[self.curr_tile], 'pos' : [tile_mpos[0] * self.tilemap.tile_size, tile_mpos[1] * self.tilemap.tile_size], 'destroy_counter': 0, 'variant': self.curr_ver}
                if self.right_click:
                    tile_pos = f"{tile_mpos[0]},{tile_mpos[1]}"
                    if tile_pos in self.tilemap.data:
                        del self.tilemap.data[tile_pos] 

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.left_click = True
                    if event.button == 2:
                        self.flood_fill(tile_mpos)
                    if event.button == 3:    
                        self.right_click = True
                    if event.button == 4:
                        if self.shift: self.curr_ver = (self.curr_ver + 1) % len(self.assets[self.asset_list[self.curr_tile]])
                        else:self.curr_tile = (self.curr_tile + 1) %  len(self.asset_list)
                    if event.button == 5:
                        if self.shift: self.curr_ver = (self.curr_ver - 1) % len(self.assets[self.asset_list[self.curr_tile]])
                        else: self.curr_tile = (self.curr_tile - 1) % len(self.asset_list)
                try:
                    if self.curr_ver >= len(self.assets[self.asset_list[self.curr_tile]]): self.curr_ver = 0
                except: pass
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.left_click = False
                    if event.button == 2:
                        self.mid_click = True
                        self.floodfill[1] = pygame.mouse.get_pos()
                    if event.button == 3:
                        self.right_click = False

                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w: self.should_move['up'] = True
                    if event.key == pygame.K_a: self.should_move['left'] = True
                    if event.key == pygame.K_d: self.should_move['right'] = True
                    if event.key == pygame.K_s: self.should_move['down'] = True 
                    if event.key == pygame.K_LSHIFT: self.shift = True  
                    if event.key == pygame.K_o: self.tilemap.save('map.json')
                    if event.key == pygame.K_t: self.tree(tile_mpos)
                    if event.key == pygame.K_e: self.add_enemy()
                    if event.key == pygame.K_y: self.tilemap.spawn_point = [(pygame.mouse.get_pos()[0] + self.scroll[0]) / RENDER_SCALE, (pygame.mouse.get_pos()[1] + self.scroll[1]) / RENDER_SCALE]
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w: self.should_move["up"] = False
                    if event.key == pygame.K_a: self.should_move['left'] = False
                    if event.key == pygame.K_d: self.should_move['right'] = False
                    if event.key == pygame.K_s: self.should_move['down'] = False #dont delete, USEFUL
                    if event.key == pygame.K_LSHIFT: self.shift = False  
            
            self.scroll[0] += (self.should_move['right'] - self.should_move['left']) * self.camera_speed
            self.scroll[1] += (self.should_move["down"] - self.should_move['up']) * self.camera_speed
            self.render_scroll = [int(self.scroll[0]), int(self.scroll[1])]
            
            #drawingsd
            self.screen.fill(self.background_color)
            self.picked.set_alpha(100)
            self.screen.blit(self.picked,((tile_mpos[0])* self.tilemap.tile_size - self.scroll[0], (tile_mpos[1]) * self.tilemap.tile_size - self.scroll[1]))
            self.picked.set_alpha(255)
            self.tilemap.render(self.render_scroll)  
            self.screen.blit(pygame.transform.scale(self.picked,(40,40)),(0,0))
            self.real_screen.blit(pygame.transform.scale_by(self.screen,self.real_screen.get_width()/self.screen.get_width()),(0,0))
            pygame.display.update()
            self.clock.tick(60)
    
    def flood_fill(self,tmpos):
        if self.flood == None: self.flood = tmpos
        else:
            for x in range(self.flood[0] - 1,tmpos[0] - 1):
                for y in range(self.flood[1] + 1,tmpos[1] + 1):
                    self.tilemap.data[f"{x},{y}"] =  {'type': self.asset_list[self.curr_tile], 'pos' : [x * self.tilemap.tile_size, y * self.tilemap.tile_size], 'destroy_counter': 0, 'variant': self.curr_ver}
            self.flood = None
            
    def tree(self, tile_mpos):
        height = random.randint(3,8)
        for tile in range(height):
            self.tilemap.data[f"{tile_mpos[0]},{tile_mpos[1] - tile}"] = {'type': 'tree', 'pos': [tile_mpos[0] * self.tilemap.tile_size, (tile_mpos[1] - tile)* self.tilemap.tile_size], 'variant': random.randint(0,4), 'destroy_counter' : 0}


    def add_enemy(self):
        mpos = (pygame.mouse.get_pos()[0] / RENDER_SCALE + self.scroll[0], pygame.mouse.get_pos()[1] / RENDER_SCALE + self.scroll[1])
        self.tilemap.enemies.append({'type': 'enemy', 'pos': mpos, 'variant': random.randint(0,3)})

Editor().run()