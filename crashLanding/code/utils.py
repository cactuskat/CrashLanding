from settings import *
from os.path import abspath,dirname

BASE_DIR = dirname(__file__)
GAME_ROOT = abspath(join(BASE_DIR, ".."))

def safe_load(func):
    def wrap(*args,**kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise Exception(f"Failed to load asset at {args}: {e}") from e
    return wrap

@safe_load
def load_asset(*path) -> str:
    return join(GAME_ROOT, *path)

@safe_load
def load_audio(*path) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(load_asset("audio",*path))

@safe_load
def load_image(*path) -> pygame.Surface:
    return pygame.image.load(load_asset("images",*path))

@safe_load
def load_font(size,*path) -> pygame.font.Font:
    return pygame.font.Font(load_asset("images","ui",*path),size)
    
@safe_load
def load_sprite(*path) -> pygame.Surface:
    return load_image(*path).convert_alpha()