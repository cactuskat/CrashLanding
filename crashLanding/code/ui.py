from settings import * 

class UI:
    def __init__(self):
        self.window = pygame.display.get_surface()

        #fonts
        self.font = pygame.font.Font(join("..","images","ui","runescape_uf.ttf"),40)
        self.font_back = pygame.font.Font(join("..","images","ui","runescape_uf.ttf"),50)
        self.font_small = pygame.font.Font(join("..","images","ui","runescape_uf.ttf"),20)

    def print(self,text,x,y,reg_font=True):
        text_surface = None
        if reg_font:
            text_surface = self.font.render(text,True,(255,255,255))
        else:
            text_surface = self.font_small.render(text,True,(255,255,255))
            
        text_rect = text_surface.get_rect(center = (x,y))
        self.window.blit(text_surface, text_rect)