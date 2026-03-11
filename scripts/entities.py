import pygame,random

DEF_OFFSET = [(1,1),(1,0),(0,1),(0,0),(-1,-1),(-1,1),(1,-1),(-1,0),(0,-1)]

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size) -> None:
        self.game = game
        self.type = e_type
        
        self.pos = list(pos)
        self.size = size
        self.vel = [0,0]
        self.curr_move = [0,0]

        self.rect = pygame.FRect(self.pos,self.size)
        self.flip = False

    def update(self,tilemap, movement=[0,0]):
        if self.in_water(): 
            self.movement_speed = 4
        else: 
            self.movement_speed = 5
        self.curr_move = ((movement[0] + self.vel[0]) * self.movement_speed , (movement[1] + self.vel[1]) * self.movement_speed)
        self.colided = {'left': False, 'right' : False, 'top' : False,  'bottom' : False}
        if self.in_water(): self.movement_speed = 5
        else: self.movement_speed = 2

        self.rect.top += self.curr_move[1]
        for tile in tilemap.physisc_tiles_around(self.rect):
            if tile.colliderect(self.rect):
                if self.curr_move[1] > 0:
                    self.colided['bottom'] = True
                    self.rect.bottom = tile.top
                if self.curr_move[1] < 0:
                    self.colided['top'] = True
                    self.rect.top = tile.bottom
        self.rect.left += self.curr_move[0]

        for tile in tilemap.physisc_tiles_around(self.rect):
            if tile.colliderect(self.rect):
                if self.curr_move[0] > 0:
                    self.colided['right'] = True
                    self.rect.right = tile.left
                if self.curr_move[0] < 0:
                    self.colided['left'] = True
                    self.rect.left = tile.right

        #capping speed
        if int(self.vel[0]) > 0: self.vel[0] = min(3,self.vel[0] - 0.1)
        elif int(self.vel[0]) < 0: 
            self.vel[0] = max(-3,self.vel[0] + 0.1)
        elif self.vel[0] != 0: self.vel[0] = 0

        if self.in_water():
            if self.vel[0] > 0: self.vel[0] -= 0.1
            elif self.vel[0] < 0: self.vel[0] += 0.1
            if self.vel[1] > 0: self.vel[1] -= 0.1
            elif self.vel[1] < 0: self.vel[1] += 0.1
            #handle issue with speed lower than 0.1
            if abs(self.vel[0]) < 0.1: self.vel[0] = 0
            if abs(self.vel[1]) < 0.1: self.vel[1] = 0
        else: self.vel[1] = min(7, self.vel[1] + 0.1)

    
        if self.colided['bottom'] or self.colided['top']: self.vel[1] = 0

    def in_water(self):
        #print(f"{int(self.get_rect().centerx // self.game.tilemap.tile_size)}, {int(self.get_rect().centery // self.game.tilemap.tile_size)}")
        if f"{int(self.get_rect().centerx // self.game.tilemap.tile_size)},{int(self.get_rect().centery // self.game.tilemap.tile_size)}" in self.game.tilemap.data:
            return self.game.tilemap.data[f"{int(self.get_rect().centerx // self.game.tilemap.tile_size)},{int(self.get_rect().centery // self.game.tilemap.tile_size)}"]['type'] == 'water'
        return False

    def render(self, screen, offset = [0,0]):
        screen.blit(self.image,(self.rect.left - offset[0], self.rect.top - offset[1]))

    def get_rect(self):
        return self.rect

class Enemy(PhysicsEntity):
    def __init__(self, game, e_type, pos, size) -> None:
        super().__init__(game, e_type, pos, size)
        self.image = self.game.assets['enemy'][random.randint(0,3)]
        self.speed = 0.6
        self.hp = 100

    def update(self, tilemap, movement=[0, 0]):
        if self.hp < 100: self.hp += 0.1
        return super().update(tilemap, movement=self.move())

    def attacked(self):
        if self.hp > 0:
            self.hp -= 1
        else: 
            self.game.drop_list.append(Drop(self.game, 'drop', self.get_rect().center, self.game.mini_block_size,'enemy'))
            self.game.enemy_list.remove(self)

    def move(self):
        out =  [0,0]
        if abs(self.get_rect().centerx - self.game.player.get_rect().centerx) < 500 and abs(self.get_rect().centery - self.game.player.get_rect().centery) < 400:
            if (self.get_rect().centerx - self.game.player.get_rect().centerx) > 0: out[0] = -self.speed
            else: out[0] = self.speed
            if (self.get_rect().centery - self.game.player.get_rect().centery) > 0: out[1] = -self.speed
            else: out[1] = self.speed
        return out

    def draw_healthbar(self,scroll):
        max_hp = pygame.Surface((50,10))
        max_hp.fill((255,0,0))
        curr_hp = pygame.Surface((50 * (self.hp / 100),10))
        curr_hp.fill((144,238,144))
        self.game.screen.blit(max_hp, (self.get_rect().topleft[0] - scroll[0], self.get_rect().topleft[1] - 30 - scroll[1]))
        self.game.screen.blit(curr_hp, (self.get_rect().topleft[0] - scroll[0], self.get_rect().topleft[1] - 30 - scroll[1]))

def load_enemies(game,list):
    out = []
    for enemy in list:
        out.append(Enemy(game,'enemy', enemy['pos'],game.assets['enemy'][0].get_size()))
    return out

class Drop(PhysicsEntity):
    def __init__(self, game, e_type, pos, size, type) -> None:
        super().__init__(game, e_type, pos, size)
        self.image = self.game.assets['mini' + type]
        self.speed = 0.01#the higher the number the lover the speed 
        self.type = type

    def update(self, tilemap, movement=[0, 0]):
        super().update(tilemap, movement=[(self.game.player.get_rect().centerx - self.get_rect().centerx)* self.speed,(self.game.player.get_rect().centery - self.get_rect().centery) * self.speed])
        #if self.colided['left'] or self.colided['right']: return
        #else: self.rect.move_ip((self.game.player.get_rect().centerx - self.get_rect().centerx)* self.speed,(self.game.player.get_rect().centery - self.get_rect().centery) * self.speed)

    def check_col(self):
        return self.get_rect().colliderect(self.game.player.get_rect())
        
    def call_all(self,tilemap,screen,scroll):
        self.update(tilemap)
        self.render(screen, scroll)

class Player(PhysicsEntity):
    def __init__(self, game, e_type, pos, size) -> None:
        super().__init__(game, 'player', pos, size)
        self.image = pygame.Surface((size))
        self.image.fill((100,0,250))
        self.breath = 500
        self.dashing = 0
        self.dash_speed = 1.5
        self.air_time = 0
        self.mine_range = 120
        self.mine_color = (178,34,34)
        self.mine_width = 4
        self.water_jump = 0
        self.water_alert = True
        self.state = 'walking'
        self.jumps = 1

    def update(self, tilemap, movement=[0, 0]):
        super().update(tilemap, movement=movement)
        if self.curr_move[0] > 0: self.flip = False
        elif self.curr_move[0] < 0: self.flip = True
        #setting state
        if self.in_water():
            if self.curr_move[0] != 0: self.state = 'swimming'
            else: self.state = 'water'
        else:
            if self.curr_move[0] != 0 and abs(self.curr_move[1]) <=  1: self.state = 'walking'
            elif self.curr_move[0] == 0 and abs(self.curr_move[1]) <= 1: self.state = 'standing'
            elif self.curr_move[1] < 1: self.state = 'jump'
            elif self.curr_move[1] > 1: self.state = 'fall'
    

        if self.in_water(): self.breath -= 0.2
        elif self.breath < 500: self.breath += 2

        if self.breath < 1: 
            self.game.inv.alert('YOU DIED.')
            self.game.alive = False
        self.game.healthbar.update(self.breath)

        self.air_time += 1
        if self.colided['bottom']: 
            self.jumps = 1
            self.air_time = 0
        if self.dashing:
            if abs(self.dashing) > 60:
                self.vel[0] =  (abs(self.dashing) / self.dashing) * self.dash_speed
            elif self.dashing == 60:  self.vel[0] = 0
            if self.dashing > 0: self.dashing -= 1
            elif self.dashing < 0: self.dashing += 1
        if self.water_jump > 0: self.water_jump -= 1

    def jump(self):
        #if self.in_water(): self.vel[1] -= self.water_move_speed 
        if self.jumps and self.air_time < 3 and not self.in_water(): 
            self.vel[1] = -2.5
            self.jumps -= 1
            self.air_time = 5

    def mine(self):
        mpos = [pygame.mouse.get_pos()[0] / self.game.scale, pygame.mouse.get_pos()[1] / self.game.scale]
        if abs(self.rect.centerx - (mpos[0] + self.game.scroll[0])) < self.mine_range and abs(self.rect.centery - (mpos[1] + self.game.scroll[1])) < self.mine_range:
            self.game.tilemap.destroy_block((mpos[0] + self.game.scroll[0],mpos[1] + self.game.scroll[1]))
            for enemy in self.game.enemy_list.copy():
                if enemy.get_rect().collidepoint((mpos[0] + self.game.scroll[0], mpos[1] + self.game.scroll[1])): 
                    enemy.attacked()
            return [self.game.screen, self.mine_color ,(self.rect.centerx - self.game.scroll[0], self.rect.centery - self.game.scroll[1]),(mpos),self.mine_width]

    def dash(self):
        if self.in_water():
            if self.water_jump < 1:
                self.vel[1] = -2
                self.water_jump = 50
        else:
            if self.dashing != 0: return
            if self.flip: self.dashing = -80
            else: self.dashing = 80
    
    def check_col(self):
        for enemy in self.game.enemy_list:
            #print(enemy)
            if enemy.get_rect().colliderect(self.get_rect()): self.breath -= 3

class Animation():
    def __init__(self, game, images, img_dur) -> None:
        self.game = game
        self.images = images
        self.img_dur = img_dur
        self.curr = self.frame = 0


    def update(self):
        if self.curr == 'permanent': return
        if self.curr > self.img_dur:
            self.frame = (self.frame + 1) % len(self.images)
            self.curr = 0
        else: self.curr += 1
        
    def render(self, scroll = [0,0], flip = False):
        self.update()
        self.game.screen.blit(pygame.transform.flip(self.images[self.frame], flip, False),(self.game.player.get_rect().left - scroll[0], self.game.player.get_rect().top - scroll[1]))