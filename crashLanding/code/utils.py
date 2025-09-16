from settings import *
from os.path import abspath,dirname

BASE_DIR = dirname(__file__)
GAME_ROOT = abspath(join(BASE_DIR, ".."))

def get_full_path(*path):
    """
    Get full path for assets in both dev mode & PyInstaller executable
    """
    if hasattr(sys, '_MEIPASS'):
        #executable: assets relative to sys._MEIPASS
        return join(sys._MEIPASS, *path)
    else:
         #dev mode: assests relavtive to GAME_ROOT
         return join(GAME_ROOT, *path)


def safe_load(func):
    def wrap(*args,**kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise Exception(f"Failed to load asset at {args}: {e}") from e
    return wrap

@safe_load
def load_asset(*path) -> str:
    return get_full_path(*path)

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