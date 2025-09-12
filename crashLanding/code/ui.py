from settings import * 
from utils import load_font

class UI:
    def __init__(self):
        self.window = pygame.display.get_surface()

        #fonts
        self.font = load_font(40,"runescape_uf.ttf")
        self.font_back = load_font(50,"runescape_uf.ttf")
        self.font_small = load_font(20,"runescape_uf.ttf")

    def print(self,text,x,y,reg_font=True):
        text_surface = None
        if reg_font:
            text_surface = self.font.render(text,True,(255,255,255))
        else:
            text_surface = self.font_small.render(text,True,(255,255,255))
            
        text_rect = text_surface.get_rect(center = (x,y))
        self.window.blit(text_surface, text_rect)