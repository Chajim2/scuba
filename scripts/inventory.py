import pygame, time
from .utils import APPLY_PHYSICS, dict_to_str, str_to_dict
from .recipes import RECIPES
PLACALBE = ['grass', 'dirt']
class HUD():
    def __init__(self,game) -> None:
        self.game = game
        self.img = pygame.transform.scale_by(game.assets['inventory'], 5)
        self.items = {}
        self.selected = 1

    def add(self, item):
        mpos = pygame.mouse.get_pos()
        tile_mpos = (int(((mpos[0] / self.game.scale) - self.game.inv.inv_pos[0])//(self.game.inv.pix_size[0] /6 )),int(((mpos[1] / self.game.scale) - self.game.inv.inv_pos[1])//(self.game.inv.pix_size[1] / 5)))
        #if tile_mpos in self.items:
         #   self.game.inv.picked = self.items[tile_mpos]    
        self.items[tile_mpos] = item

    def get_selected(self):
        if (self.selected,4) in self.items:
            return self.items[(self.selected,4)]
        return {'type' : 'balls'}
    
    def place_block(self):
        if (self.selected,4) in self.items:
            if self.items[(self.selected,4)]['type'] not in PLACALBE:
                return
            mpos = (int((pygame.mouse.get_pos()[0]/self.game.scale + self.game.scroll[0])//self.game.tilemap.tile_size),int((pygame.mouse.get_pos()[1]/self.game.scale + self.game.scroll[1])//self.game.tilemap.tile_size))
            if f"{mpos[0]},{mpos[1]}" not in self.game.tilemap.data or self.game.tilemap.data[f"{mpos[0]},{mpos[1]}"]['type'] == 'water':
                self.items[(self.selected,4)]['count'] -= 1
                self.game.tilemap.data[f"{mpos[0]},{mpos[1]}"] = {
                                                                "type": self.items[(self.selected,4)]['type'],
                                                                "pos": [mpos[0] * self.game.tilemap.tile_size, mpos[1] * self.game.tilemap.tile_size],
                                                                "destroy_counter": 0,
                                                                "variant": 1
                                                                }
                if self.items[(self.selected,4)]['count'] == 0: del self.items[(self.selected,4)]

    def render(self):
        self.game.screen.blit(self.img,(450,660))
        for item in self.items:
                self.game.screen.blit(self.game.assets[self.items[item]['type'] + '1'], (470 + item[0] * 65, 680))
                self.game.screen.blit(self.game.inv.font.render(str(self.items[item]['count']),False,self.game.inv.font_color),(500 + item[0] * 65, 700))
        self.game.screen.blit(self.game.assets['inv_highlight'],(455 + self.selected * 65, 665))

class Inventory:
    def __init__(self,game) -> None:
        self.game = game
        self.inv_pos = [240,150]
        self.pix_size = [640,440]
        self.tiles_size = [8,4]
        self.tile_size  = [self.pix_size[0] / self.tiles_size[0], self.pix_size[1] / self.tiles_size[1]]
        self.img = pygame.transform.scale(self.game.assets['main_inv'],[875,450])
        self.data = {}    
        self.render_offset, self.text_offset = 20, 57
        self.font_init()
        self.picked = self.placeholder = None
        self.y_defor = 1.05
        self.crafting = {}
        self.equiped = {}
        self.right_click = False

    def drag(self):
        """
        hitbox of (1,4) is a bit off;
        """
        mpos = (pygame.mouse.get_pos()[0] / self.game.scale,pygame.mouse.get_pos()[1] / self.game.scale)
        if (mpos[0] > (self.inv_pos[0] + self.pix_size[0]) + 250) or (mpos[0] < self.inv_pos[0]) or (mpos[1] > (self.inv_pos[1] + self.pix_size[1] + 20)) or (mpos[1] < self.inv_pos[1]):
            print('clicked out of invenotry')
            #could add mechanic of throwing items out
            return
        
        elif mpos[0] > 1000 and mpos[0] < 1130 and mpos[1] > 470 and mpos[1] < 600:
            if mpos[1] > 540: curr = 'laser'
            else: curr = 'helmet'    
            if self.picked is not None:
                if self.picked['type'] == curr:
                    self.equiped[curr] = True
                    self.picked = None
                    self.game.tilemap.update_destroyable()
            else:
                if curr in self.equiped:
                    self.picked = {'type' : curr, 'count' : 1 }
                    del self.equiped[curr]
                    self.game.tilemap.update_destroyable()
            return


        #handling crafting
        #the crafting area beggins 895 and ends 1115
        elif mpos[0] > 895 and mpos[0] < 1115 and mpos[1] < 470:
            tile_mpos = (int((mpos[0] - 895) // 73), int((mpos[1] - self.inv_pos[1]) // (self.tile_size[1] / 1.3)))
            if tile_mpos[1] > 2 and tile_mpos != (2,3): return 
            if self.picked is not None: 
                if tile_mpos in self.crafting: 
                    if self.crafting[tile_mpos]['type'] == self.picked['type']:
                        self.crafting[tile_mpos]['count'] += self.picked['count']
                        self.picked = None
                        return
                self.craft(tile_mpos, self.picked.copy())
                self.picked = None
            elif tile_mpos in self.crafting:
                self.picked = self.crafting[tile_mpos] 
                del self.crafting[tile_mpos]
            elif dict_to_str(self.crafting) in RECIPES and tile_mpos == (2,3) and self.picked is None:
                self.picked = RECIPES[dict_to_str(self.crafting)]
                self.crafting = {}
                
            return
        #lower inv
        elif mpos[1] > 470:
            tile_mpos = (int((mpos[0] - self.inv_pos[0]) // (self.pix_size[0] /6)), int((mpos[1] - self.inv_pos[1]) // (self.tile_size[1] / 1.3)))
            data = self.game.hud.items
        else: #upper inv
            tile_mpos = (int((pygame.mouse.get_pos()[0] / self.game.scale - self.inv_pos[0]) // self.tile_size[0]), int((pygame.mouse.get_pos()[1] / self.game.scale - self.inv_pos[1]) // (self.tile_size[1] / 1.3)))
            data = self.data
        
        if self.picked is None:
            if tile_mpos in data:
                self.picked = data[tile_mpos].copy()
                del data[tile_mpos]
        #item in hand
        else:
            if tile_mpos in data:
                if self.picked['type'] == self.data[tile_mpos]['type']:
                    self.data[tile_mpos]['count'] += self.picked['count']
                    self.picked = None
                else:
                    temp = data[tile_mpos].copy()
                    data[tile_mpos] = self.picked
                    self.picked = temp
            else:
                data[tile_mpos] = self.picked
                self.picked = None
        
    def craft(self,tmpos, tile):
        self.crafting[tmpos] = tile
        

    def half(self):
        if not self.picked: return 
        if self.picked['count'] % 2 == 0: give = stay = int(self.picked['count'] // 2)
        else: give, stay = int((self.picked['count'] - 1) // 2), int((self.picked['count'] + 1) // 2)
        if give == 0 or stay == 0: return

        mpos = (pygame.mouse.get_pos()[0] / self.game.scale, pygame.mouse.get_pos()[1] / self.game.scale)
        #outside of invenotry
        if (mpos[0] > (self.inv_pos[0] + self.pix_size[0]) + 220) or (mpos[0] < self.inv_pos[0]) or (mpos[1] > (self.inv_pos[1] + self.pix_size[1])) or (mpos[1] < self.inv_pos[1]): return
        if mpos[0] > 895 and mpos[1] < 1115:
            #crafting area
            tile_mpos = (int((mpos[0] - 895) // 73), int((mpos[1] - self.inv_pos[1]) // (self.tile_size[1] / 1.3)))
            if tile_mpos in self.crafting: return
            #split the picked item
            else: self.crafting[tile_mpos] = {'type' : self.picked['type'], 'count' :give }
            self.picked['count'] = stay

        elif mpos[1] > 470: #lower inventory
            tile_mpos = (int((mpos[0] - self.inv_pos[0]) // (self.pix_size[0] /6)), int((mpos[1] - self.inv_pos[1]) // (self.tile_size[1] / 1.3)))
            if tile_mpos in self.game.hud.items: return
            else: self.game.hud.items[tile_mpos] = {'type' : self.picked['type'], 'count' : give}
            self.picked['count'] = stay

        else: #upper inventory
            tile_mpos = (int((pygame.mouse.get_pos()[0] / self.game.scale - self.inv_pos[0]) // self.tile_size[0]), int((pygame.mouse.get_pos()[1] / self.game.scale - self.inv_pos[1]) // (self.tile_size[1] / 1.3)))
            if tile_mpos in self.data: return
            else: self.data[tile_mpos] = {'type': self.picked['type'], 'count':give}
            self.picked['count'] = stay
           
           
    def font_init(self):
        pygame.font.init()
        self.font = pygame.font.Font("data/font/CubicCoreMono.ttf",30)
        self.font_color = (0,0,0)
    
    def pick_up(self,type):
        for tile in self.data:
            if self.data[tile]['type'] == type:
                self.data[tile]['count'] += 1
                return
        for tile in self.game.hud.items:
            if self.game.hud.items[tile]['type'] == type:
                self.game.hud.items[tile]['count'] += 1
                return
        
        for x in range(6):
            if (x,4) not in self.game.hud.items:
                self.game.hud.items[(x,4)] = {'type': type, 'count': 1}
                return

        for x in range(self.tiles_size[0]):
            for y in range(self.tiles_size[1]):
                if (x,y) not in self.data:
                    self.data[(x,y)] = {'type' : type, 'count': 1}
                    return
    def alert(self,message, pos = (700,480), wait = 3):
        font = pygame.font.Font("data/font/CubicCoreMono.ttf",150)
        self.game.real_screen.blit(font.render(message,False, self.font_color), pos)
        pygame.display.update()
        time.sleep(3)


    def render(self):
        self.game.screen.blit(self.img,self.inv_pos)
        for tile in self.data:
            #if self.data[tile] != self.picked: 
            self.game.screen.blit(self.game.assets[self.data[tile]['type'] + '1'], ( self.render_offset + self.inv_pos[0] + (tile[0] * self.pix_size[0]/self.tiles_size[0]),
                                                                    self.render_offset + self.inv_pos[1] + (tile[1] * self.pix_size[0]/(self.tiles_size[0] * self.y_defor))))
            
            self.game.screen.blit(self.font.render(str(self.data[tile]['count']),False,self.font_color),(self.text_offset + self.inv_pos[0] + (tile[0] * self.pix_size[0]/self.tiles_size[0]), self.text_offset + self.inv_pos[1] - 5 + (tile[1] * self.pix_size[0]/(self.tiles_size[0] * self.y_defor))))
        
        if self.picked: 
            self.game.screen.blit(self.game.assets[self.picked['type'] + '1'], [pygame.mouse.get_pos()[0] / self.game.scale - 25, (pygame.mouse.get_pos()[1] / self.game.scale - 25)]) 
    
            self.game.screen.blit(self.font.render(str(self.picked['count']), False,self.font_color),[pygame.mouse.get_pos()[0] / self.game.scale + 10, (pygame.mouse.get_pos()[1] / self.game.scale )])
        
        for item in self.game.hud.items: 
            #if self.game.hud.items[item] != self.picked: 
            self.game.screen.blit(self.game.assets['big' + self.game.hud.items[item]['type']],(self.inv_pos[0] + 30 + ( item[0] * self.pix_size[0] / 6.1),490))
            
            self.game.screen.blit(self.font.render(str(self.game.hud.items[item]['count']),False,self.font_color),(self.inv_pos[0] + 90 + ( item[0] * self.pix_size[0] / 6.1),530))
    
        for tile in self.crafting:
            self.game.screen.blit(self.game.assets[self.crafting[tile]['type'] + '1'], ( 895 + tile[0] * 80, 20 + self.inv_pos[1] + tile[1] * 75))
            
            self.game.screen.blit(self.font.render(str(self.crafting[tile]['count']), False,self.font_color), (930 + tile[0] * 80, 50 + self.inv_pos[1] + tile[1] * 75))
        
        for gear in self.equiped:
            if gear == 'laser': self.game.screen.blit(self.game.assets[gear + '1'],(1040,530))
            else: self.game.screen.blit(self.game.assets[gear + '1'],(1085,480))

        if dict_to_str(self.crafting) in RECIPES:
            self.game.screen.blit(self.game.assets[RECIPES[dict_to_str(self.crafting)]['type'] + '1'], (1050,405))

class Guide():
    def __init__(self,game) -> None:
        self.img = game.assets['guide']
        self.game = game
        self.one_tile = 20
        self.x_gap = 250
        self.y_gap = 350
        self.x_offset = 300
        self.y_offset = 10
        self.tile_size = 75
        self.item_offset = 20

    def render(self):
        if self.game.player.get_rect().centerx < 550 and self.game.player.get_rect().centerx > 250 and self.game.player.get_rect().centery < 600:
            x_count = 0
            y_count = 0
            for recipe in RECIPES:    
                self.game.screen.blit(self.img,(self.x_offset + x_count *self.x_gap, self.y_offset + y_count * self.y_gap))
                for item in recipe.split(';')[:-1]:    
                    self.game.screen.blit(self.game.assets[f"{item.split(':')[-1]}1"],(self.item_offset + self.x_offset + x_count * self.x_gap + int(item[0]) * self.tile_size,self.item_offset + self.y_offset + y_count * self.y_gap + int(item[2]) * self.tile_size )) 
                self.game.screen.blit(self.game.assets['big' + RECIPES[recipe]['type']],(x_count*self.x_gap + 90 + self.x_offset, self.y_offset + self.y_gap * y_count + 240))
                if (x_count + 1) % 3 != 0: x_count += 1
                else:
                    x_count = 0
                    y_count += 1
            return True
        return False

