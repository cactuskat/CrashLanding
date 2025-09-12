from settings import *
from os.path import abspath,dirname

BASE_DIR = dirname(__file__)
GAME_ROOT = abspath(join(BASE_DIR, ".."))

#Return absolute path to an asset
def load_asset(*path):
    return join(GAME_ROOT, *path)

def load_audio(*item):
    return pygame.mixer.Sound(load_asset("audio",*item))

def load_image(*path):
    return pygame.image.load(load_asset("images",*path))

def load_font(size,*font):
    return pygame.font.Font(load_asset("images","ui",*font),size)

def load_sprite(*path):
    return load_image(*path).convert_alpha()

