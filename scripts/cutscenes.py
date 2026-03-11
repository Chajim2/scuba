import pygame, sys, time

class Cutscene():
    def __init__(self,game) -> None:
        self.game = game
        pygame.font.init()
        self.font = pygame.font.Font("data/font/retron2000/Retron2000.ttf",70)
        self.title_font = pygame.font.Font("data/font/retron2000/Retron2000.ttf",260)
        self.font_color = (0,0,0)
        self.warn_timer = 120

    def warn_skip(self):
        if self.warn_timer < 120: return True
        else: 
            self.game.real_screen.blit(self.font.render('press space to skip',False,self.font_color),(500,600))
            pygame.display.update()
            time.sleep(2)
            return False
            

    def handle_skip(self):
        if self.warn_timer < 120: self.warn_timer += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN: 
                if self.warn_skip(): return True
    
    def scene_end(self):
        self.game.scroll[1] = 1200
        while self.game.scroll[1] > -400:
            self.game.scroll[1] -= 3
            self.game.render_all(hide_hud = True)
            if self.handle_skip(): break
        if self.game.scroll[1] < -400: 
            self.game.real_screen.blit(self.title_font.render("SCUBA",False,(75,83,55)),(600* self.game.scale,170* self.game.scale))
            self.game.real_screen.blit(self.font.render("New Game",False,(75,83,55)),(620 * self.game.scale,400* self.game.scale))
            self.game.real_screen.blit(self.font.render("Continue",False,(75,83,55)),(620 * self.game.scale,467* self.game.scale))
            self.game.real_screen.blit(self.font.render("Exit",False,(75,83,55)),(620 * self.game.scale,535* self.game.scale))
            pygame.display.update()

        self.main_menu()

    def main_menu(self):

        while True:
            self.game.real_screen.blit(self.game.assets['main_menu'],(0,0))
            self.game.cursor.render()
            pygame.display.update()
            self.game.cursor.render()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        mpos = pygame.mouse.get_pos()
                        #all have the same x 
                        print(mpos)
                        print(self.game.scale)
                        if mpos[0] > 620 * self.game.scale and mpos[0] < (870* self.game.scale): 
                            #new game
                            if mpos[1] > 420 * self.game.scale and mpos[1] < (470 * self.game.scale): 
                                print("new game")
                                self.game.tilemap.load("base_map.json")
                                self.game.load_all('base_inv.json')
                                return
                            if mpos[1] > 487 * self.game.scale and mpos[1] < 530 * self.game.scale: 
                                self.game.tilemap.load('map.json')
                                self.game.load_all('inv.json')
                                return
                            if mpos[1] > 530 * self.game.scale and mpos[1] < 595* self.game.scale: 
                                pygame.quit()
                                sys.exit()

            
    
